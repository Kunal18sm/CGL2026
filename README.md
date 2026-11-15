# SSC CGL 2026 — 20 Papers Analysis & Practice Portal

An intelligent analytics dashboard and interactive practice engine built for SSC CGL 2026 Tier 1 aspirants. Analyzes all 20 actual exam shifts (2,000 questions), categorizing every question into granular micro-topics and providing an authentic 60-minute mock test environment with official answer keys (+2 correct, -0.5 negative marking).

---

## 🌟 Key Features

- **Granular 125-Subtopic Taxonomy**:
  - Detailed subcategory breakdown across all 4 sections:
    - **General Awareness**: Ancient, Medieval & Modern Indian History (Indus Valley, Vedic, Buddhism, Mughals, 1857 Revolt), Indian Polity (BNS/BNSS 2024 Criminal Codes, Articles, DPSP), Static GK (Dances, Music, Festivals, Books/Authors, Sports), Geography, Economy, Science.
    - **Reasoning**: Syllogism, Blood Relations, Direction & Distance, Seating Arrangements, Coding-Decoding, Non-Verbal, Analogies.
    - **Quantitative Aptitude**: Geometry, Trigonometry, Algebra, Arithmetic, Mensuration, Number System.
    - **English Comprehension**: Error Spotting, Cloze Test, Vocabulary (Synonyms, Antonyms, Idioms, OWS), Sentence Rearrangement.
- **High-Yield Frequency Analytics**:
  - Subtopics ranked by frequency across all 20 shifts.
  - Interactive table sorting by Section, Subtopic, Question Count, and Shift Presence (e.g. `20/20 shifts`).
- **Interactive Question Bank (2,000 Questions)**:
  - Clean text typography for questions and all 4 options.
  - Instant official vector answer verification.
  - Optional scan toggle to view original response sheet crop for diagrams.
- **Authentic Practice & Timed Mock Exam**:
  - Subtopic-targeted practice mode with instant explanations.
  - 60-Minute Timed Mock Exam mode replicating real SSC interface, question palette, and score report (+2 / -0.5 marking).
- **Modern Minimal UI with Dark Theme**:
  - Clean slate & zinc layout, high contrast, zero unnecessary glow.
  - One-click Light / Dark Mode toggle with persistent preference.

---

## 🚀 Getting Started

1. Clone or download the repository:
   ```bash
   git clone https://github.com/Kunal18sm/CGL2026.git
   cd CGL2026
   ```

2. Launch the local web server:
   - On Windows: Double click `start_website.bat`
   - Or run in terminal:
     ```bash
     python -m http.server 8080
     ```

3. Open your browser and navigate to:
   ```
   http://localhost:8080
   ```

---

## 📂 Project Structure

```
├── index.html        # Clean minimal portal UI
├── style.css         # Modern light/dark theme styles
├── app.js            # Interactive analytics, filters & test engine
├── data.json         # Complete dataset (2,000 Qs + 125 Subtopics)
├── favicon.svg       # Portal app icon
├── cards/            # 2,000 cropped question scan cards
├── extract_all_text.py   # OCR & text extraction engine
├── recategorize.py       # 125-subtopic classification pipeline
├── start_website.bat     # One-click Windows launcher
└── README.md
```
