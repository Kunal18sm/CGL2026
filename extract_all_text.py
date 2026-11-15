import asyncio, fitz, re, time, os, json
import winrt.windows.graphics.imaging as imaging
import winrt.windows.media.ocr as ocr
import winrt.windows.storage.streams as streams
from recategorize import classify_detailed

def clean_text(s):
    if not s:
        return ""
    # Fix joined ordinals like 17thJuly -> 17th July
    s = re.sub(r'(\d+(?:st|nd|rd|th))([A-Za-z]+)', r'\1 \2', s)
    # Fix multiple spaces
    s = re.sub(r'\s+', ' ', s)
    # Remove junk characters like #rmissible -> permissible if obvious
    s = s.replace('#rmissible', 'permissible')
    return s.strip()

def sort_words_in_lines(words):
    if not words:
        return ""
    words_sorted = sorted(words, key=lambda w: (w.get('pno', 0), w['y']))
    lines = []
    curr_line = []
    curr_y = None
    for w in words_sorted:
        if curr_y is None or abs(w['y'] - curr_y) <= 4.0:
            curr_line.append(w)
            curr_y = w['y'] if curr_y is None else (curr_y * (len(curr_line) - 1) + w['y']) / len(curr_line)
        else:
            curr_line.sort(key=lambda x: x['x'])
            lines.append(' '.join(x['text'] for x in curr_line))
            curr_line = [w]
            curr_y = w['y']
    if curr_line:
        curr_line.sort(key=lambda x: x['x'])
        lines.append(' '.join(x['text'] for x in curr_line))
    return clean_text(' '.join(lines))

async def process_all_papers():
    total_start = time.time()
    engine = ocr.OcrEngine.try_create_from_user_profile_languages()
    scale = 150.0 / 72.0
    
    # Load existing data.json for existing answers and meta
    with open('web/data.json', 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
        
    papers_meta = existing_data.get('papers', [])
    existing_questions_map = {(q['paper_id'], q['q_num']): q for q in existing_data.get('questions', [])}
    
    all_updated_questions = []
    
    for pi in range(1, 21):
        t0 = time.time()
        pdf_path = f'C:/Users/yash9/Downloads/paper{pi}.pdf'
        if not os.path.exists(pdf_path):
            print(f"File {pdf_path} not found!")
            continue
            
        doc = fitz.open(pdf_path)
        
        # 1. Locate Q.No positions
        q_locs = []
        for pno in range(len(doc)):
            page = doc[pno]
            for b in page.get_text('blocks'):
                if 'Q.No:' in b[4]:
                    m = re.search(r'Q\.No:\s*(\d+)', b[4])
                    if m:
                        q_locs.append({'q_num': int(m.group(1)), 'pno': pno, 'y0': b[1], 'y1': b[3]})
        q_locs.sort(key=lambda x: x['q_num'])
        
        # 2. OCR pages with questions
        q_pages = sorted(list(set(q['pno'] for q in q_locs)))
        # Also include any next pages for multi-page questions
        expanded_pages = set(q_pages)
        for pno in q_pages:
            if pno + 1 < len(doc):
                expanded_pages.add(pno + 1)
        expanded_pages = sorted(list(expanded_pages))
        
        page_words = {}
        for pno in expanded_pages:
            page = doc[pno]
            # Skip cover / empty pages
            if not page.get_drawings() and len(page.get_text()) < 50:
                continue
            pix = page.get_pixmap(dpi=150)
            mem = streams.InMemoryRandomAccessStream()
            w = streams.DataWriter(mem)
            w.write_bytes(pix.tobytes('png'))
            await w.store_async(); await w.flush_async(); mem.seek(0)
            dec = await imaging.BitmapDecoder.create_async(mem)
            bmp = await dec.get_software_bitmap_async()
            res = await engine.recognize_async(bmp)
            
            words = []
            for line in res.lines:
                for wd in line.words:
                    r = wd.bounding_rect
                    words.append({
                        'text': wd.text,
                        'x': r.x / scale,
                        'y': r.y / scale,
                        'ymid': (r.y + r.height / 2.0) / scale,
                        'pno': pno
                    })
            page_words[pno] = words
            
        # 3. Detect cell groups per page
        all_groups = []
        for pno in range(len(doc)):
            page = doc[pno]
            cells = []
            for d in page.get_drawings():
                r = d['rect']
                if abs(r.x0 - 20.25) < 3.0 and (r.x1 - r.x0) > 40.0 and (r.x1 - r.x0) < 70.0 and (r.y1 - r.y0) > 8.0:
                    cells.append((round(r.y0, 1), round(r.y1, 1)))
            cells = sorted(list(set(cells)), key=lambda x: x[0])
            
            page_groups = []
            curr = []
            for c in cells:
                if not curr or abs(c[0] - curr[-1]['y1']) <= 3.0:
                    curr.append({'pno': pno, 'y0': c[0], 'y1': c[1]})
                else:
                    page_groups.append(curr)
                    curr = [{'pno': pno, 'y0': c[0], 'y1': c[1]}]
            if curr:
                page_groups.append(curr)
                
            all_groups.extend(page_groups)
            
        # Merge spillover groups
        merged_groups = []
        i = 0
        while i < len(all_groups):
            grp = all_groups[i]
            if len(grp) < 5 and i + 1 < len(all_groups):
                next_grp = all_groups[i+1]
                if len(grp) + len(next_grp) in [5, 6]:
                    merged_groups.append(grp + next_grp)
                    i += 2
                    continue
            merged_groups.append(grp)
            i += 1
            
        # Extract 100 questions for this paper
        for qn in range(1, 101):
            existing_q = existing_questions_map.get((pi, qn), {})
            ans = existing_q.get('correct_option', 1)
            
            grp = merged_groups[qn - 1] if qn - 1 < len(merged_groups) else []
            opt_cells = grp[-4:] if len(grp) >= 4 else []
            stmt_cells = grp[:-4] if len(grp) > 4 else []
            
            # Extract statement
            stmt_words = []
            if stmt_cells:
                for sc in stmt_cells:
                    spw = page_words.get(sc['pno'], [])
                    wlist = [w for w in spw if sc['y0'] - 2 <= w['ymid'] <= sc['y1'] + 2 and w['x'] >= 70.0]
                    stmt_words.extend(wlist)
            else:
                # Fallback if stmt_cells empty
                loc = q_locs[qn - 1] if qn - 1 < len(q_locs) else None
                if loc:
                    spw = page_words.get(loc['pno'], [])
                    y_end = opt_cells[0]['y0'] if opt_cells and opt_cells[0]['pno'] == loc['pno'] else 9999
                    wlist = [w for w in spw if loc['y0'] - 15 <= w['ymid'] < y_end and w['x'] >= 70.0]
                    stmt_words.extend(wlist)
                    
            stmt_text = sort_words_in_lines(stmt_words)
            if not stmt_text and existing_q.get('statement'):
                stmt_text = existing_q['statement']
                
            # Extract 4 options
            options = []
            for oc in opt_cells:
                opw = page_words.get(oc['pno'], [])
                wlist = [w for w in opw if oc['y0'] - 2 <= w['ymid'] <= oc['y1'] + 2 and w['x'] >= 70.0]
                options.append(sort_words_in_lines(wlist))
                
            while len(options) < 4:
                options.append(f"Option {len(options) + 1}")
                
            # Classify
            temp_q = {'q_num': qn, 'statement': stmt_text}
            sec, top, sub, scope = classify_detailed(temp_q)
            
            q_obj = {
                'id': f'p{pi}_q{qn}',
                'paper_id': pi,
                'q_num': qn,
                'section': sec,
                'topic': top,
                'subtopic': sub,
                'micro_scope': scope,
                'statement': stmt_text,
                'options': options,
                'correct_option': ans,
                'card_image': f'cards/p{pi}_q{qn}.png'
            }
            all_updated_questions.append(q_obj)
            
        print(f"Paper {pi:02d} processed in {time.time()-t0:.1f}s (100 questions extracted)")
        
    # Build granular subtopics table with high-yield sorting
    subtopic_counts = {}
    for q in all_updated_questions:
        key = (q['section'], q['topic'], q['subtopic'], q['micro_scope'])
        if key not in subtopic_counts:
            subtopic_counts[key] = {
                'section': q['section'],
                'topic': q['topic'],
                'subtopic': q['subtopic'],
                'micro_scope': q['micro_scope'],
                'total_questions': 0,
                'shift_counts': [0] * 20
            }
        subtopic_counts[key]['total_questions'] += 1
        subtopic_counts[key]['shift_counts'][q['paper_id'] - 1] += 1
        
    subtopics_list = list(subtopic_counts.values())
    for s in subtopics_list:
        total = s['total_questions']
        s['avg_per_shift'] = round(total / 20.0, 2)
        s['weightage_pct'] = round((total / 2000.0) * 100, 2)
        s['shifts_appeared'] = sum(1 for c in s['shift_counts'] if c > 0)
        if total >= 30:
            s['yield_tag'] = 'High Yield'
        elif total >= 12:
            s['yield_tag'] = 'Medium Yield'
        else:
            s['yield_tag'] = 'Low Yield'
            
    # SORT SUBTOPICS: HIGH YIELD FIRST (total_questions descending)
    subtopics_list.sort(key=lambda s: s['total_questions'], reverse=True)
    
    # Sections aggregation
    sec_counts = {}
    for q in all_updated_questions:
        sec = q['section']
        sec_counts[sec] = sec_counts.get(sec, 0) + 1
        
    final_data = {
        'total_papers': 20,
        'total_questions': len(all_updated_questions),
        'papers': papers_meta,
        'sections_summary': [{'section': k, 'total': v, 'pct': round((v/2000)*100, 1)} for k, v in sec_counts.items()],
        'subtopics': subtopics_list,
        'questions': all_updated_questions
    }
    
    with open('web/data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
        
    print(f"ALL 20 PAPERS COMPLETED in {time.time()-total_start:.1f}s!")
    print(f"Updated web/data.json with {len(all_updated_questions)} questions and {len(subtopics_list)} sorted subtopics.")

if __name__ == '__main__':
    asyncio.run(process_all_papers())
