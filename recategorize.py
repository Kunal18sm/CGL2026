import json, re, time

def classify_detailed(q):
    qn = q['q_num']
    stmt = q['statement']
    s = stmt.lower()
    
    # -------------------------------------------------------------
    # SECTION 1: GENERAL INTELLIGENCE & REASONING (Q1 - Q25)
    # -------------------------------------------------------------
    if 1 <= qn <= 25:
        section = "General Intelligence & Reasoning"
        
        # 1. Syllogism & Logic
        if any(w in s for w in ['conclusion', 'statement:', 'statement :', 'statements:', 'conclusions:']) or 'follow' in s:
            if 'course of action' in s:
                return section, "Logical Deduction", "Statement & Course of Action", "Decision making & remedial action"
            if 'assumption' in s:
                return section, "Logical Deduction", "Statement & Assumptions", "Implicit premise deduction"
            return section, "Syllogism", "Statements & Conclusions", "Standard syllogistic deduction (Some/All/No)"
            
        # 2. Blood Relations
        if any(w in s for w in ['brother', 'sister', 'mother', 'father', 'son', 'daughter', 'uncle', 'aunt', 'nephew', 'niece', 'paternal', 'maternal', 'husband', 'wife', 'child of']):
            if any(sym in s for sym in ['@', '#', '$', '%', '&', '*']):
                return section, "Blood Relations", "Coded Blood Relations", "Symbolic relationship expressions (e.g. A # B % C)"
            return section, "Blood Relations", "Family Tree & Direct Relations", "Pointer / Direct generational family tree"
            
        # 3. Direction & Distance
        if any(w in s for w in ['north', 'south', 'east', 'west', 'left turn', 'right turn', 'kilometre', 'towards north', 'towards south', 'facing', 'shadow', 'direction']):
            return section, "Direction & Distance", "Cardinal Directions & Navigation", "Turns, compass navigation & Pythagoras displacement"
            
        # 4. Seating & Puzzles
        if any(w in s for w in ['seated', 'sitting', 'circular table', 'facing centre', 'stack', 'boxes are kept', 'linear row', 'eight boxes', 'arranged in a row', 'floor']):
            if any(w in s for w in ['box', 'stack', 'soft toy', 'toys']):
                return section, "Puzzles & Arrangement", "Box & Stack Arrangement", "Vertical item ordering & positioning"
            if 'circular' in s or 'circle' in s:
                return section, "Puzzles & Arrangement", "Circular Seating Arrangement", "Inward/Outward facing circular tables"
            return section, "Puzzles & Arrangement", "Linear Seating Arrangement", "Single or double parallel row alignment"
            
        # 5. Order & Ranking
        if any(w in s for w in ['rank', 'from the top', 'from the bottom', 'from the left', 'taller than', 'heavier than', 'shorter than', 'seminar was held on', 'days after', 'days before', 'roll numbers']):
            if 'seminar' in s or 'days after' in s or 'days before' in s or 'roll numbers' in s:
                return section, "Order & Ranking", "Calendar & Sequential Scheduling", "Date calculation & temporal ordering"
            return section, "Order & Ranking", "Comparison & Position in Line", "Relative comparison of attributes & ranks"
            
        # 6. Word Formation & Dictionary
        if any(w in s for w in ['rearrange the letters', 'meaningful word', 'dictionary', 'alphabetical order', 'jumbled', 'letters of that word', 'form a meaningful']):
            if 'dictionary' in s or 'alphabetical' in s:
                return section, "Word Formation", "English Dictionary Order", "Sequential lexicon arrangement"
            return section, "Word Formation", "Meaningful Word from Jumbled Letters", "Anagram unscrambling & valid word formation"
            
        # 7. Coding - Decoding
        if any(w in s for w in ['coded as', 'code for', 'written as', 'in a certain code', 'if red is called', 'secret code', 'cipher']):
            if re.search(r'\d+', s):
                return section, "Coding - Decoding", "Letter-to-Number Coding", "Numerical value / positional shift ciphers"
            return section, "Coding - Decoding", "Letter-to-Letter Substitution", "Alphabetical shift & reversal patterns"
            
        # 8. Series
        if any(w in s for w in ['complete the pattern', 'complete the series', 'next number', 'missing number', 'series:']) or re.search(r'\b\d+,\s*\d+,\s*\d+\b', s):
            if re.search(r'\b\d+,\s*\d+,\s*\d+\b', s) or any(c.isdigit() for c in stmt):
                return section, "Series Completion", "Number Series & Pattern Progression", "Arithmetic, geometric, square & difference progression"
            return section, "Series Completion", "Alphabetical & Mixed Series", "Letter progression & alternating sequences"
            
        # 9. Analogy
        if any(w in s for w in ['analogy', 'related to', 'best completes the analogy']) or ' : ' in stmt or '::' in stmt:
            if re.search(r'[a-zA-Z]\s*:\s*\d+', stmt) or re.search(r'\d+\s*:\s*\d+', stmt):
                return section, "Analogy", "Letter-Number & Symbolic Analogy", "Alphanumeric ratio relationships"
            return section, "Analogy", "Word & Semantic Analogy", "Vocabulary, classification & semantic pairing"
            
        # 10. Classification / Odd One Out
        if any(w in s for w in ['does not belong', 'odd one', 'different from the others', 'odd pair', 'classification', 'group:']):
            if any(c.isdigit() for c in stmt):
                return section, "Classification", "Number Odd-One-Out", "Cubes, primes, parity & mathematical anomaly"
            return section, "Classification", "Word & Letter Odd-One-Out", "Category mismatch & property divergence"
            
        # 11. Mathematical Operations
        if any(w in s for w in ['interchanged', 'interchange', 'signs', 'equation is correct', 'mathematical signs', 'bodmas']):
            return section, "Mathematical Operations", "Sign & Number Interchange", "BODMAS operator replacement & balance"
            
        # 12. Venn Diagrams
        if any(w in s for w in ['venn', 'diagram represents', 'represent the relationship']):
            return section, "Venn Diagrams", "Geometric & Set Relationship Venn", "3-set intersection & categorical mapping"
            
        # 13. Non-Verbal
        if any(w in s for w in ['mirror image', 'water image']):
            return section, "Non-Verbal Reasoning", "Mirror & Water Reflections", "Lateral & vertical inversion geometry"
        if any(w in s for w in ['paper', 'folding', 'punched', 'unfold']):
            return section, "Non-Verbal Reasoning", "Paper Folding & Cutting", "Symmetrical cutout analysis"
        if any(w in s for w in ['dice', 'cube', 'opposite face', 'opposite to']):
            return section, "Non-Verbal Reasoning", "Cubes & Dice", "Standard & open dice surface mapping"
        if any(w in s for w in ['embedded figure', 'hidden inside', 'pattern completion', 'rotation is not allowed']):
            return section, "Non-Verbal Reasoning", "Embedded Figures & Pattern Completion", "Visual contour detection"
            
        return section, "General Intelligence", "Logical Puzzle & Deductive Reasoning", "Integrated analytical thinking"

    # -------------------------------------------------------------
    # SECTION 2: GENERAL AWARENESS (Q26 - Q50)
    # -------------------------------------------------------------
    elif 26 <= qn <= 50:
        section = "General Awareness"
        
        # 1. NEW CRIMINAL LAWS & LEGAL REFORMS
        if any(w in s for w in ['bharatiya nagarik suraksha', 'bharatiya sakshya', 'bharatiya nyaya', 'bnss', 'bsa', 'bns', 'conclusive proof', 'first information report', 'firs']):
            return section, "Legal System & Law Reforms", "New Criminal Codes (BNS, BNSS, BSA)", "Evidence admissibility, FIR reforms & criminal jurisprudence"
            
        # 2. KEY APPOINTMENTS & CURRENT AFFAIRS
        if any(w in s for w in ['chief of the naval staff', 'cns', 'appointed as', 'admiral dinesh', 'chairperson of the national commission', 'ncw', 'vijaya rahatkar', 'rekha sharma', 'sworn in may', 'mamata banerjee', 'chief minister']):
            if 'naval' in s or 'admiral' in s:
                return section, "Current Affairs: Appointments", "Defence & Military Leadership Appointments", "Chiefs of Armed Forces (Naval Staff, Army, Air Force)"
            if 'commission for women' in s or 'ncw' in s:
                return section, "Current Affairs: Appointments", "National Statutory Commissions (NCW)", "Statutory chairpersons & constitutional appointments"
            if 'chief minister' in s or 'sworn in' in s:
                return section, "Current Affairs: Governance", "State Politics & Chief Ministerial Tenures", "State executive mandates & legislative elections"
            return section, "Current Affairs: General", "National Dignitaries & Recent Appointments", "High constitutional & governmental personnel changes"

        # 3. GOVERNMENT SCHEMES, POLICIES & MISSIONS
        if any(w in s for w in ['bhashini', 'nltm', 'national digital health mission', 'ndhm', 'nep 2020', 'policy on education', 'urdpfi', 'urban and regional development', 'twenty-point', 'tpp', 'pradhan mantri', 'yojana', 'uniform civil code', 'ucc', 'uttarakhand']):
            if 'uniform civil code' in s or 'ucc' in s:
                return section, "Polity & Governance", "Uniform Civil Code (UCC) & State Legislation", "Article 44, civil codes & personal law reforms (Uttarakhand)"
            if 'bhashini' in s or 'translation' in s:
                return section, "Government Schemes & Missions", "Digital India & Language Tech (BHASHINI)", "AI-driven language translation & NLTM ecosystem"
            if 'ndhm' in s or 'digital health' in s:
                return section, "Government Schemes & Missions", "National Digital Health Mission (NDHM)", "Integrated health IDs, electronic records & tele-health"
            if 'nep' in s or 'policy on education' in s:
                return section, "Government Schemes & Missions", "National Education Policy (NEP 2020)", "Foundational literacy, 5+3+3+4 schooling & higher ed"
            if 'urdpfi' in s:
                return section, "Government Schemes & Missions", "Urban Planning & Regional Guidelines (URDPFI)", "Spatial urban development, master plans & GIS mapping"
            if 'twenty-point' in s:
                return section, "Government Schemes & Missions", "Targeted Welfare (Twenty-Point Programme)", "Poverty alleviation & rural development plans"
            return section, "Government Schemes & Missions", "National Flagship Schemes", "Central government socio-economic programmes"

        # 4. SPORTS & ATHLETICS
        if any(w in s for w in ['american football', 'touchdown', 'world cup final', 'narendra modi stadium', 'cricket', 'olympic', 'tennis', 'grand slam', 'australian open', 'rohan bopanna', 'mahesh bhupati', 'leander paes', 'dhing express', 'hima das', 'singh sisters', 'basketball', 'kho-kho', 'tent pegging', 'polo', 'judo', 'pommel horse', 'gymnastics', 'sports', 'medal', 'athlete']):
            if any(w in s for w in ['tennis', 'grand slam', 'australian open', 'rohan bopanna', 'mahesh bhupati', 'leander paes']):
                return section, "Sports & Athletics", "Tennis Grand Slams & Indian Pioneers", "Open Era records, doubles championships & Grand Slam titles"
            if any(w in s for w in ['cricket', 'world cup final', 'narendra modi stadium', 'stadium']):
                return section, "Sports & Athletics", "Cricket World Cups & Sporting Venues", "World Cup finals, stadium capacities & ICC tournaments"
            if any(w in s for w in ['dhing express', 'singh sisters', 'hima das', 'basketball', 'judo']):
                return section, "Sports & Athletics", "Indian Athletes, Sobriquets & Team Sports", "National champions, sport nicknames (Dhing Express) & medals"
            if any(w in s for w in ['american football', 'touchdown', 'tent pegging', 'kho-kho', 'pommel horse', 'gymnastics']):
                return section, "Sports & Athletics", "Sports Dimensions, Scoring & Traditional Games", "Gymnastics apparatus (pommel horse), traditional sports & rules"
            return section, "Sports & Athletics", "Global Tournaments & Sporting Records", "Multi-sport championships & international events"

        # 5. LITERATURE, BOOKS & AWARDS
        if any(w in s for w in ['booker prize', 'heat and dust', 'vikram chandra', 'sacred games', 'commonwealth writers', 'dsc prize', 'sleeping on jupiter', 'anuradha roy', 'silappadikaram', 'kannagi', 'epic', 'book', 'author', 'novel', 'nobel', 'bharat ratna', 'award']):
            if 'silappadikaram' in s or 'kannagi' in s or 'madurai' in s:
                return section, "History & Literature", "Sangam Literature & Ancient Epics (Silappadikaram)", "Tamil Sangam epics, Kannagi legend & Pandya kingdom (Madurai)"
            return section, "Literature, Books & Awards", "Literary Prizes & Celebrated Authors", "Booker Prize, DSC Prize, Commonwealth awards & Indian novels"

        # 6. ART, CULTURE & FESTIVALS
        if any(w in s for w in ['teej', 'festival', 'dance', 'classical dance', 'folk dance', 'monsoon', 'gharana', 'sitar', 'tabla', 'flute', 'music', 'temple', 'architecture', 'gandhara', 'sculpture']):
            if 'gandhara' in s or 'sculpture' in s or 'greek art' in s:
                return section, "Art & Culture", "Gandhara School of Art & Sculpture", "Greco-Buddhist artistic syncretism & Buddha iconography"
            if 'teej' in s or 'festival' in s or 'monsoon' in s:
                return section, "Art & Culture", "Indian Festivals & Seasonal Heritage", "Cultural festivals (Teej/Monsoon) & regional folk customs"
            return section, "Art & Culture", "Classical Dances, Music & Traditions", "Performing arts, musical gharanas & monumental heritage"

        # 7. HISTORY: ANCIENT, MEDIEVAL & MODERN
        if any(w in s for w in ['history', 'harappa', 'mohenjo', 'indus valley', 'vedic', 'buddha', 'buddhism', 'jainism', 'maurya', 'ashoka', 'kalinga', 'gupta', 'heliodorus', 'vidisha', 'delhi sultanate', 'mughal', 'taj mahal', 'akbar', 'babur', 'shah jahan', 'aurangzeb', 'pitt\'s india act', '1784', '1857', 'gandhi', 'congress', 'viceroy', 'governor general', 'british', 'east india', 'macaulay', 'english as the medium', 'freedom fighter', 'revolt', 'agni of india', 'durgawati', 'chola', 'dynasty']):
            # Ancient
            if any(w in s for w in ['harappa', 'mohenjo', 'indus', 'vedic', 'rigveda', 'upanishad']):
                return section, "History: Ancient India", "Indus Valley Civilization & Vedic Age", "Urban planning, drainage, seals & Vedic social order"
            if any(w in s for w in ['heliodorus', 'vidisha', 'pillar', 'parthian', 'kushan', 'shunga']):
                return section, "History: Ancient India", "Post-Mauryan Kingdoms & Foreign Contacts (Heliodorus)", "Heliodorus Garuda pillar, Indo-Greeks & Shunga empire"
            if any(w in s for w in ['buddha', 'buddhism', 'jainism', 'mahavira']):
                return section, "History: Ancient India", "Buddhism & Jainism Movements", "Doctrines, monastic orders & ancient religious councils"
            if any(w in s for w in ['maurya', 'ashoka', 'kalinga', 'gupta', 'samudragupta', 'chola', 'pallava', 'dynasty']):
                return section, "History: Ancient India", "Mauryan, Gupta & Southern Empires", "Imperial conquests, Ashokan inscriptions & statecraft"
            # Medieval
            if any(w in s for w in ['mughal', 'taj mahal', 'akbar', 'shah jahan', 'babur', 'aurangzeb']):
                return section, "History: Medieval India", "Mughal Empire & Architecture (Taj Mahal)", "Architectural masterpieces, revenue systems & imperial court"
            if any(w in s for w in ['delhi sultanate', 'sultan', 'slave dynasty', 'khilji', 'tughlaq', 'lodi', 'shivaji', 'peshwa', 'vijayanagara']):
                return section, "History: Medieval India", "Delhi Sultanate & Regional Empires", "Dynastic succession, medieval warfare & Vijayanagara state"
            # Modern
            if any(w in s for w in ['pitt\'s india act', '1784', 'regulating act', 'charter act']):
                return section, "History: Modern India", "British Constitutional Acts (Pitt's India Act 1784)", "Board of Control, dual governance & Company regulation"
            if any(w in s for w in ['macaulay', 'english as the medium', 'medium of instruction', 'governor general', 'viceroy', 'british']):
                return section, "History: Modern India", "British Policies, Education & Administration", "Macaulay's minute, educational acts & colonial civil policy"
            if any(w in s for w in ['1857', 'agni of india', 'durgawati', 'revolt', 'freedom fighter', 'sepoy', 'rani laxmibai']):
                return section, "History: Modern India", "1857 Revolt & Revolutionary Movements", "First war of independence, revolutionary patriots & heroines"
            if any(w in s for w in ['gandhi', 'congress', 'inc session', 'swadeshi', 'non-cooperation', 'quit india', 'civil disobedience']):
                return section, "History: Modern India", "Indian Freedom Struggle & Gandhian Movements", "Mass movements, INC annual sessions & independence struggles"
            return section, "History: General", "Indian Historical Milestones", "Chronological development of Indian history"

        # 8. POLITY & CONSTITUTION
        if any(w in s for w in ['article', 'constitution', 'fundamental right', 'fundamental duty', 'dpsp', 'amendment', 'parliament', 'lok sabha', 'rajya sabha', 'president', 'prime minister', 'governor', 'supreme court', 'high court', 'panchayat', 'basic structure', 'kesavananda', 'inter-state council', '73rd']):
            if 'basic structure' in s or 'kesavananda' in s or 'article 368' in s:
                return section, "Polity & Constitution", "Landmark Judgments & Basic Structure (Art. 368)", "Kesavananda Bharati case, judicial review & amending limits"
            if '73rd' in s or 'inter-state council' in s or 'federal' in s:
                return section, "Polity & Constitution", "Federalism & Constitutional Amendments (73rd/ISC)", "Inter-State coordination & Panchayati Raj devolution"
            if any(w in s for w in ['article 14', 'article 19', 'article 21', 'article 32', 'fundamental right', 'dpsp', 'fundamental duty']):
                return section, "Polity & Constitution", "Fundamental Rights & Constitutional Articles", "Civil liberties, directive principles & citizen duties"
            if any(w in s for w in ['parliament', 'lok sabha', 'rajya sabha', 'speaker', 'president', 'ordinance']):
                return section, "Polity & Constitution", "Parliament & Union Executive", "Parliamentary legislation, electoral procedures & presidential powers"
            return section, "Polity & Constitution", "Indian Constitutional Framework", "System of governance & administrative architecture"

        # 9. GEOGRAPHY: INDIAN, PHYSICAL & CLIMATOLOGY
        if any(w in s for w in ['stratosphere', 'troposphere', 'atmosphere', 'coriolis', 'deflection of moving objects', 'meridian', '1st meridian', 'standard time', 'latitude', 'longitude', 'continent', 'indian ocean', 'africa', 'astheno', 'mantle', 'sugarcane', 'pulse production', 'cereals', 'cropped area', 'assam', 'oil wells', 'digboi', 'naharkatiya', 'ports', 'iron ore', 'coal', 'tropical', 'broadleaf forests', 'river', 'mountain', 'himalaya', 'soil', 'monsoon']):
            if 'coriolis' in s or 'deflection' in s or 'moving objects' in s:
                return section, "Geography: Physical", "Planetary Winds, Pressure Belts & Coriolis Effect", "Ferrel's law, deflection of trade winds & ocean currents"
            if 'meridian' in s or 'standard time' in s or 'longitude' in s or 'midnight' in s:
                return section, "Geography: Physical", "Mathematical Geography: Meridians & Time Zones", "Longitudinal time calculations & Earth's axial rotation"
            if 'stratosphere' in s or 'atmosphere' in s or 'ozone' in s:
                return section, "Geography: Physical", "Atmosphere: Stratosphere & Thermal Layers", "Inversion layers, ozone absorption & temperature gradients"
            if 'continent' in s or 'indian ocean' in s or 'africa' in s or 'ocean' in s:
                return section, "Geography: World", "World Continents, Oceans & Landmass Locations", "Continental boundaries, oceanic basins & spatial geography"
            if 'astheno' in s or 'mantle' in s or 'crust' in s:
                return section, "Geography: Physical", "Geomorphology: Earth's Mantle & Asthenosphere", "Plastic mantle flow, magma genesis & lithospheric support"
            if 'sugarcane' in s or 'cereals' in s or 'pulse' in s or 'cropped area' in s or 'kharif' in s:
                return section, "Geography: Indian", "Agriculture: Cropping Patterns & Cash Crops (Sugarcane/Cereals)", "Cropped area percentages, sugarcane belts & harvest seasons"
            if 'oil wells' in s or 'digboi' in s or 'assam' in s or 'iron ore' in s or 'ports' in s:
                return section, "Geography: Indian", "Mineral Resources & Industrial Seaports", "Digboi petroleum fields, eastern mineral ports & logistics"
            if 'forests' in s or 'broadleaf' in s or 'vegetation' in s:
                return section, "Geography: Indian", "Indian Forests & Biogeographical Zones", "Tropical moist broadleaf forests, rainfall belts & biodiversity"
            if 'river' in s or 'ganga' in s or 'indus' in s or 'drainage' in s:
                return section, "Geography: Indian", "River Drainage Systems & Water Basins", "Himalayan and Peninsular river networks & catchment areas"
            return section, "Geography: General", "Indian & Physical Geography", "Geographical distributions & environmental physiography"

        # 10. ECONOMICS: INDIAN, MACRO & GLOBAL
        if any(w in s for w in ['socialist economy', 'karl marx', 'demand', 'price of the commodity', 'foreign investment', 'fdi', 'bpo', 'business process outsourcing', 'privatisation', 'pse', 'disinvestment', '1991', 'reforms of 1991', 'human development index', 'hdi', 'world happiness', 'happiness report', 'gallup', 'well-being', 'gdp', 'inflation', 'rbi', 'monetary', 'budget', 'five-year plan']):
            if 'socialist economy' in s or 'karl marx' in s or 'adam smith' in s:
                return section, "Economics: Theory", "Economic Systems & Thinkers (Socialism / Karl Marx)", "Command economies, means of production & economic philosophers"
            if 'demand' in s or 'price of the commodity' in s or 'elasticity' in s:
                return section, "Economics: Micro", "Law of Demand & Consumer Behaviour", "Determinants of demand, price elasticity & utility"
            if 'bpo' in s or 'foreign investment' in s or 'privatisation' in s or 'disinvestment' in s or '1991' in s:
                return section, "Economics: Indian", "1991 Reforms: LPG, Disinvestment & Global Outsourcing (BPO)", "New Economic Policy, foreign capital inflow & PSU disinvestments"
            if 'hdi' in s or 'human development index' in s or 'happiness' in s or 'gallup' in s:
                return section, "Economics: Development", "Global Socio-Economic Indices (HDI & Happiness)", "Multidimensional human welfare, education & life satisfaction"
            if 'rbi' in s or 'monetary' in s or 'repo' in s or 'banking' in s:
                return section, "Economics: Macro", "Banking, RBI & Monetary Governance", "Liquidity management, benchmark rates & price stability"
            if 'five-year plan' in s or 'planning' in s or 'niti' in s:
                return section, "Economics: Indian", "National Economic Planning & Five-Year Plans", "Economic growth models, sectoral targets & plan outlays"
            return section, "Economics: General", "Macroeconomics & Public Finance", "Fiscal balances, taxation & national economic indicators"

        # 11. SCIENCE: BIOLOGY, CHEMISTRY, PHYSICS & SPACE
        if any(w in s for w in ['isro', 'satellite', 'risat', 'rlv-td', 'myopia', 'eye lens', 'curvature of the eye', 'muscle fatigue', 'lactic acid', 'pulse rate', 'beats per minute', 'radionuclide', 'half-life', 'magnetic flux', 'weber', 'resistivity', 'ohm-meter', 'ideal gas', 'isothermal', 'cancer', 'tumor', 'proliferation', 'anabolic steroids', 'food web', 'air quality index', 'aqi', 'cell', 'vitamin', 'force', 'energy', 'light']):
            if 'myopia' in s or 'curvature of the eye' in s or 'eye lens' in s:
                return section, "Science: Biology & Optics", "Human Eye & Vision Defects (Myopia/Hypermetropia)", "Refractive ocular disorders, focal adjustments & concave correction"
            if 'muscle fatigue' in s or 'lactic acid' in s or 'pulse rate' in s or 'heart' in s:
                return section, "Science: Biology", "Human Physiology: Anaerobic Respiration & Heart Rate", "Lactic acid buildup during exertion & cardiac frequency"
            if 'cancer' in s or 'tumor' in s or 'steroids' in s or 'anabolic' in s:
                return section, "Science: Biology", "Pathology, Oncology & Human Physiology", "Metastatic cellular pathways & steroid pharmacological risks"
            if 'isro' in s or 'risat' in s or 'rlv-td' in s or 'satellite' in s:
                return section, "Science & Technology", "Space Technology: ISRO Missions & Satellites", "Reusable launch technology (RLV-TD), radar imaging & disaster tech"
            if 'resistivity' in s or 'ohm-meter' in s or 'magnetic flux' in s or 'weber' in s:
                return section, "Science: Physics", "Electricity & Magnetism: Units & Quantities", "SI units of resistivity (Ohm-m) & magnetic flux (Weber)"
            if 'radionuclide' in s or 'half-life' in s:
                return section, "Science: Physics", "Nuclear Physics: Radioactive Decay & Half-Life", "Exponential nuclear decay rates & undecayed mass calculations"
            if 'food web' in s or 'air quality index' in s or 'aqi' in s:
                return section, "Environment & Ecology", "Ecosystem Ecology & Air Quality (AQI)", "Trophic dynamics, food webs & EPA air quality rating scales"
            if 'ideal gas' in s or 'isothermal' in s or 'expansion' in s:
                return section, "Science: Physics & Chem", "Thermodynamics: Isothermal Gas Expansion", "Thermodynamic state changes, ideal gas equations & heat transfer"
            return section, "Science: General", "General Scientific Foundations", "Fundamental physical, chemical & life sciences"

        # 12. INTERNATIONAL RELATIONS & CORRIDORS
        if any(w in s for w in ['imec', 'economic corridor', 'brics', 'bist-ec', 'bimstec', 'south-south cooperation', 'quad', 'quadrilateral security dialogue']):
            if 'imec' in s or 'economic corridor' in s:
                return section, "International Relations & Trade", "Strategic Corridors: IMEC Infrastructure", "India-Middle East-Europe trade corridor & multimodal transit"
            if 'bist-ec' in s or 'bimstec' in s or 'myanmar' in s:
                return section, "International Relations & Trade", "Regional Economic Alliances: BIMSTEC Evolution", "Bay of Bengal integration & institutional expansion"
            if 'brics' in s or 'south-south' in s:
                return section, "International Relations & Trade", "BRICS & South-South Cooperation", "Emerging market solidarity, trade alliances & multipolar forums"
            if 'quad' in s:
                return section, "International Relations & Trade", "Strategic Alliances: QUAD Diplomacy", "Indo-Pacific maritime security & multilateral strategic dialogues"
            return section, "International Relations & Trade", "Global Organizations & Foreign Policy", "Bilateral treaties, international forums & strategic partnerships"

        return section, "General Awareness", "Contemporary National & International Affairs", "Current events & multi-disciplinary awareness"

    # -------------------------------------------------------------
    # SECTION 3: QUANTITATIVE APTITUDE (Q51 - Q75)
    # -------------------------------------------------------------
    elif 51 <= qn <= 75:
        section = "Quantitative Aptitude"
        
        # Geometry
        if any(w in s for w in ['triangle', 'circle', 'tangent', 'chord', 'radius', 'diameter', 'cyclic', 'quadrilateral', 'angle', 'hypotenuse', 'incentre', 'circumcentre', 'orthocentre', 'centroid']):
            if any(w in s for w in ['circle', 'tangent', 'chord', 'cyclic']):
                return section, "Geometry", "Circles, Chords & Tangents", "Secant theorems, tangent perpendicularity & cyclic properties"
            return section, "Geometry", "Triangles, Polygons & Angles", "Similarity, pythagorean triples & triangle center properties"
            
        # Trigonometry
        if any(w in s for w in ['sin', 'cos', 'tan', 'cot', 'sec', 'cosec', 'degree', 'elevation', 'depression', 'height and distance', 'trigonometric']):
            if 'elevation' in s or 'depression' in s or 'height' in s:
                return section, "Trigonometry", "Heights & Distances", "Triangulation, angle of elevation & line-of-sight metrics"
            return section, "Trigonometry", "Trigonometric Identities & Equations", "Pythagorean identities & complementary angle transformations"
            
        # Mensuration
        if any(w in s for w in ['cylinder', 'cone', 'sphere', 'hemisphere', 'cube', 'cuboid', 'volume', 'surface area', 'perimeter', 'area of', 'prism', 'pyramid', 'slant']):
            if any(w in s for w in ['cylinder', 'cone', 'sphere', 'hemisphere', 'cube', 'cuboid', 'volume', 'prism']):
                return section, "Mensuration", "3D Solid Volumes & Surface Areas", "Total and curved surface areas & volumetric capacities"
            return section, "Mensuration", "2D Plane Figures & Perimeters", "Plane area calculations, perimeter lengths & boundary metrics"
            
        # Algebra
        if any(w in s for w in ['x +', 'x -', 'x^2', 'x²', 'polynomial', 'identity', 'quadratic', 'roots of', 'a^3 + b^3', 'x =', 'value of x', 'algebra']):
            return section, "Algebra", "Algebraic Identities & Equations", "Binomial expansions, symmetrical sums ($x + 1/x$) & polynomial roots"
            
        # Simple & Compound Interest
        if any(w in s for w in ['simple interest', 'compound interest', 'sum of money amounts', 'rate of interest', 'compounded annually', 'per annum', 'rate of simple interest']):
            if 'compound' in s:
                return section, "Arithmetic", "Compound Interest & Installments", "Exponential compounding, nominal yields & compounding differential"
            return section, "Arithmetic", "Simple Interest", "Linear principal appreciation & constant annual interest accrual"
            
        # Profit, Loss & Discount
        if any(w in s for w in ['profit', 'loss', 'discount', 'cost price', 'selling price', 'marked price', 'shopkeeper', 'markup']):
            return section, "Arithmetic", "Profit, Loss & Successive Discounts", "Margin margins, marked price discounting & commercial transaction math"
            
        # Percentage
        if any(w in s for w in ['percent', 'percentage', '%', 'increased by', 'decreased by', 'expenditure', 'consumption']):
            return section, "Arithmetic", "Percentage & Expenditure Balances", "Relative percent changes, consumption compensatory shifts & fractions"
            
        # Time & Work
        if any(w in s for w in ['time and work', 'can do a job', 'can complete a work', 'efficiency', 'work in', 'days to finish', 'pipe', 'cistern', 'leak', 'people can do a job']):
            if 'pipe' in s or 'cistern' in s:
                return section, "Arithmetic", "Pipes & Cisterns", "Flow rates, reservoir intake capacity & outflow leak mechanics"
            return section, "Arithmetic", "Time & Work / Man-Days", "Worker efficiencies, combined man-day products & task schedules"
            
        # Speed, Time & Distance
        if any(w in s for w in ['speed', 'distance', 'train', 'boat', 'stream', 'upstream', 'downstream', 'km/h', 'm/s', 'relative speed', 'trains']):
            if 'boat' in s or 'stream' in s or 'upstream' in s:
                return section, "Arithmetic", "Boats & Streams", "River drift velocities, upstream drag & downstream assistance"
            return section, "Arithmetic", "Time, Speed, Distance & Trains", "Relative closure velocities, train length crossings & average speeds"
            
        # Ratio & Partnership
        if any(w in s for w in ['ratio', 'proportion', 'partnership', 'proportional', 'divided between', 'share of']):
            return section, "Arithmetic", "Ratio, Proportion & Partnership", "Proportional division, mean proportionals & capital-time investments"
            
        # Average
        if any(w in s for w in ['average', 'mean of', 'average age', 'average weight', 'average marks', 'average becomes', 'average of 3 friends']):
            return section, "Arithmetic", "Averages & Cohort Shifts", "Central tendencies, cohort addition/replacement & weighted averages"
            
        # Mixture & Alligation
        if any(w in s for w in ['mixture', 'alligation', 'water and milk', 'replaced with']):
            return section, "Arithmetic", "Mixtures & Alligation", "Concentration ratios, cross-alligation rules & successive fluid replacements"
            
        # Data Interpretation
        if any(w in s for w in ['chart', 'graph', 'pie chart', 'bar chart', 'table shows', 'data interpretation']):
            return section, "Data Interpretation", "Charts, Graphs & Tabular DI", "Statistical deduction, ratio comparisons & trend evaluations"
            
        # Number System
        if any(w in s for w in ['divisible', 'remainder', 'lcm', 'hcf', 'unit digit', 'number system', 'simplification', 'simplify', 'prime number']):
            return section, "Arithmetic", "Number System & Divisibility", "Divisibility criteria, remainder theorems, unit digits & factors"
            
        return section, "Arithmetic", "General Arithmetic & Operations", "Fundamental numeric computation & problem solving"

    # -------------------------------------------------------------
    # SECTION 4: ENGLISH COMPREHENSION (Q76 - Q100)
    # -------------------------------------------------------------
    else:
        section = "English Comprehension"
        
        # Spotting Errors
        if any(w in s for w in ['error', 'contains an error', 'grammatical error', 'spot the error', 'part of the sentence']):
            return section, "Grammar", "Spotting Errors in Sentences", "Subject-verb agreement, tense syntax, prepositions & modifiers"
            
        # Sentence Improvement
        if any(w in s for w in ['improvement', 'substitute the underlined', 'improve the bracketed', 'no substitution', 'no improvement']):
            return section, "Grammar", "Sentence Improvement / Phrase Replacement", "Idiomatic phrasing, grammatical precision & stylistic corrections"
            
        # Active / Passive Voice
        if any(w in s for w in ['active voice', 'passive voice', 'voice of the sentence', 'change the voice']):
            return section, "Grammar", "Active & Passive Voice", "Auxiliary verb shifts & agent-patient syntactic transformations"
            
        # Direct / Indirect Speech
        if any(w in s for w in ['direct speech', 'indirect speech', 'narration', 'reported speech']):
            return section, "Grammar", "Direct & Indirect Speech (Narration)", "Reporting verb tense modifications, pronoun shifts & backshifting"
            
        # Fill in the Blanks
        if any(w in s for w in ['fill in the blank', 'fill in the blanks', 'blank space', 'appropriate option to fill']):
            return section, "Grammar", "Fill in the Blanks & Collocations", "Contextual prepositions, phrasal verbs & vocabulary fit"
            
        # Synonyms
        if any(w in s for w in ['synonym', 'most similar', 'same meaning', 'closest in meaning', 'means the same']):
            return section, "Vocabulary", "Synonyms", "Semantic equivalents, nuance discrimination & word connotations"
            
        # Antonyms
        if any(w in s for w in ['antonym', 'opposite in meaning', 'most opposite']):
            return section, "Vocabulary", "Antonyms", "Direct lexical opposites, contradictory terms & antonymic pairs"
            
        # Idioms & Phrases
        if any(w in s for w in ['idiom', 'phrase', 'meaning of the underlined idiom', 'idiomatic']):
            return section, "Vocabulary", "Idioms & Phrasal Expressions", "Figurative cultural idioms, metaphorical expressions & colloquialisms"
            
        # One Word Substitution
        if any(w in s for w in ['one word', 'substituted for the given group', 'group of words', 'substitute for']):
            return section, "Vocabulary", "One Word Substitution (OWS)", "Single word encapsulations of complex definitions & occupations"
            
        # Spelling Errors
        if any(w in s for w in ['correctly spelt', 'incorrectly spelt', 'misspelt', 'spelling', 'supercilious']):
            return section, "Vocabulary", "Spelling Accuracy & Rules", "Orthographic conventions, doubled consonants & vowel combinations"
            
        # Para Jumbles
        if any(w in s for w in ['jumbled', 'para jumble', 'rearrange the parts', 'pqrs', 's1', 's6', 'order to form a meaningful']):
            return section, "Comprehension", "Sentence Rearrangement (PQRS)", "Narrative progression, discourse markers & logical cohesion"
            
        # Cloze Test / Reading Comprehension
        if any(w in s for w in ['passage', 'comprehension', 'cloze test', 'blank 1', 'blank 2', 'read the passage']):
            return section, "Comprehension", "Cloze Test & Reading Comprehension", "Passage context comprehension, discourse flow & reading analysis"
            
        return section, "Grammar", "Applied English Grammar & Syntax", "Core lexical structures & contextual language conventions"

def run_recategorization():
    t0 = time.time()
    data_path = r'c:\Users\yash9\OneDrive\Desktop\CGL2026\web\data.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    total_q = len(data["questions"])
    print(f'Starting granular recategorization for {total_q} questions...')
    
    # Track stats
    topic_map = {}
    
    for q in data['questions']:
        section, topic_group, subcategory, detail = classify_detailed(q)
        q['section'] = section
        q['topic_group'] = topic_group
        q['topic'] = f'{topic_group} — {subcategory}'
        q['subtopic'] = subcategory
        q['subtopic_detail'] = detail
        
        full_key = f"{section} || {topic_group} || {subcategory}"
        if full_key not in topic_map:
            topic_map[full_key] = {
                'section': section,
                'topic_group': topic_group,
                'topic': f'{topic_group} — {subcategory}',
                'subtopic': subcategory,
                'subtopic_detail': detail,
                'count': 0,
                'papers': set(),
                'sample_questions': []
            }
        topic_map[full_key]['count'] += 1
        topic_map[full_key]['papers'].add(q['paper_id'])
        if len(topic_map[full_key]['sample_questions']) < 3:
            topic_map[full_key]['sample_questions'].append({
                'id': q['id'],
                'statement': q['statement'][:150] + ('...' if len(q['statement']) > 150 else ''),
                'correct_option': q['correct_option']
            })
            
    # Format topic summary
    topics_list = []
    for k, v in topic_map.items():
        avg = round(v['count'] / 20.0, 2)
        wt = round((v['count'] / 2000.0) * 100.0, 2)
        topics_list.append({
            'section': v['section'],
            'topic_group': v['topic_group'],
            'topic': v['topic'],
            'subtopic': v['subtopic'],
            'subtopic_detail': v['subtopic_detail'],
            'total_questions': v['count'],
            'frequency_papers': len(v['papers']),
            'avg_per_paper': avg,
            'weightage_percent': wt,
            'yield_level': 'High' if avg >= 1.5 else ('Moderate' if avg >= 0.75 else 'Standard'),
            'sample_questions': v['sample_questions']
        })
        
    topics_list.sort(key=lambda x: (x['section'], x['topic_group'], -x['total_questions']))
    
    data['topics_summary'] = topics_list
    data['metadata']['granular_taxonomy'] = 'Deep SSC CGL Subtopic Taxonomy v2'
    data['metadata']['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
    
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    t1 = time.time()
    print(f'Granular recategorization completed in {t1 - t0:.2f}s!')
    print(f'Total Granular Subcategories Identified: {len(topics_list)}')
    
    # Print sample GA breakdown
    print('\nDetailed General Awareness Granular Breakdown:')
    ga_topics = [t for t in topics_list if t['section'] == 'General Awareness']
    for t in ga_topics:
        print(f" - [{t['topic_group']}] {t['subtopic']}: {t['total_questions']} Qs ({t['avg_per_paper']}/shift, {t['weightage_percent']}%)")

if __name__ == '__main__':
    run_recategorization()
