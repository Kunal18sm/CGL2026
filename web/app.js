// =========================================================
// SSC CGL 2026 — Intelligence, Analytics & Practice Engine
// =========================================================

let globalData = null;
let currentTab = 'analytics-tab';

// Sorting State for Analytics Table (Default: High Yield / Total Questions Descending)
let currentSort = {
  col: 'total_questions',
  dir: 'desc'
};

// Question Bank State
let qbFiltered = [];
let qbCurrentPage = 1;
const QB_PAGE_SIZE = 15;

// Test / Practice State
let activeTest = {
  mode: 'topic', // 'topic' or 'mock'
  title: '',
  subtitle: '',
  questions: [],
  currentIndex: 0,
  userAnswers: {},
  reviewMarked: {},
  timerSeconds: 3600,
  timerInterval: null,
  isSubmitted: false
};

// ================= Init Application =================
document.addEventListener('DOMContentLoaded', async () => {
  initTheme();
  setupNavigation();
  setupTableSorting();
  setupTopicFilters();
  setupQuestionBankFilters();
  setupPracticeControls();
  
  await loadDatabase();
});

// ================= Theme / Dark Mode =================
function initTheme() {
  const savedTheme = localStorage.getItem('cgl_theme') || 'light';
  applyTheme(savedTheme);

  const toggleBtn = document.getElementById('theme-toggle-btn');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      const nextTheme = current === 'dark' ? 'light' : 'dark';
      applyTheme(nextTheme);
    });
  }
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('cgl_theme', theme);

  const iconEl = document.getElementById('theme-icon');
  const textEl = document.getElementById('theme-text');
  if (iconEl && textEl) {
    if (theme === 'dark') {
      iconEl.textContent = '☀️';
      textEl.textContent = 'Light';
    } else {
      iconEl.textContent = '🌙';
      textEl.textContent = 'Dark';
    }
  }
}

// ================= Navigation Tabs =================
function setupNavigation() {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      switchTab(targetTab);
    });
  });
}

function switchTab(tabId) {
  currentTab = tabId;
  document.querySelectorAll('.nav-btn').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-tab') === tabId);
  });
  document.querySelectorAll('.tab-pane').forEach(p => {
    p.classList.toggle('active', p.id === tabId);
  });
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ================= Load Database =================
async function loadDatabase() {
  try {
    const res = await fetch('data.json?v=' + Date.now());
    if (!res.ok) throw new Error('Data file not ready yet');
    globalData = await res.json();
    renderAnalytics();
    renderPapersGrid();
    initQuestionBank();
    populatePracticeDropdowns();
  } catch (err) {
    console.warn('Waiting for database...', err);
    setTimeout(loadDatabase, 2000);
  }
}

// ================= Render Analytics =================
function renderAnalytics() {
  if (!globalData) return;

  const subtopics = globalData.subtopics || [];

  // KPIs
  document.getElementById('stat-papers').textContent = (globalData.papers || []).length;
  document.getElementById('stat-questions').textContent = (globalData.questions || []).length.toLocaleString();
  document.getElementById('stat-topics').textContent = subtopics.length;

  renderTopicsTable();
}

function setupTableSorting() {
  document.querySelectorAll('#topics-table th.sortable').forEach(th => {
    th.addEventListener('click', () => {
      const col = th.getAttribute('data-col');
      if (currentSort.col === col) {
        currentSort.dir = currentSort.dir === 'asc' ? 'desc' : 'asc';
      } else {
        currentSort.col = col;
        currentSort.dir = (col === 'total_questions' || col === 'shifts_appeared' || col === 'weightage_pct') ? 'desc' : 'asc';
      }
      updateTableSortHeaders();
      const activeFilter = document.querySelector('#topic-section-filters .filter-pill.active')?.getAttribute('data-filter') || 'all';
      const searchVal = document.getElementById('topic-search')?.value || '';
      renderTopicsTable(activeFilter, searchVal);
    });
  });
}

function updateTableSortHeaders() {
  document.querySelectorAll('#topics-table th.sortable').forEach(th => {
    const col = th.getAttribute('data-col');
    const icon = th.querySelector('.sort-icon');
    if (col === currentSort.col) {
      th.classList.add('active');
      if (icon) icon.textContent = currentSort.dir === 'asc' ? '↑' : '↓';
    } else {
      th.classList.remove('active');
      if (icon) icon.textContent = '↕';
    }
  });
}

function renderTopicsTable(filterSection = 'all', searchQuery = '') {
  const tbody = document.getElementById('topics-table-body');
  if (!tbody || !globalData) return;

  let topics = [...(globalData.subtopics || [])];

  // Filter by Section
  if (filterSection !== 'all') {
    topics = topics.filter(t => t.section === filterSection);
  }

  // Filter by Search Query
  if (searchQuery.trim()) {
    const q = searchQuery.toLowerCase();
    topics = topics.filter(t => 
      (t.topic && t.topic.toLowerCase().includes(q)) || 
      (t.subtopic && t.subtopic.toLowerCase().includes(q)) ||
      (t.micro_scope && t.micro_scope.toLowerCase().includes(q)) ||
      (t.section && t.section.toLowerCase().includes(q))
    );
  }

  // Sort topics according to currentSort
  topics.sort((a, b) => {
    let valA = a[currentSort.col];
    let valB = b[currentSort.col];

    if (typeof valA === 'string') valA = valA.toLowerCase();
    if (typeof valB === 'string') valB = valB.toLowerCase();

    if (valA < valB) return currentSort.dir === 'asc' ? -1 : 1;
    if (valA > valB) return currentSort.dir === 'asc' ? 1 : -1;
    return 0;
  });

  if (topics.length === 0) {
    tbody.innerHTML = `<tr><td colspan="10" class="text-center py-6 text-muted">No subcategories matching your criteria</td></tr>`;
    return;
  }

  tbody.innerHTML = topics.map(t => {
    const secBadgeClass = getSectionBadgeClass(t.section);
    const yieldBadge = t.yield_tag === 'High Yield' ? 'badge-yield-high' : (t.yield_tag === 'Medium Yield' ? 'badge-yield-moderate' : 'badge-yield-low');
    
    return `
      <tr>
        <td><span class="badge ${secBadgeClass}">${getShortSection(t.section)}</span></td>
        <td><strong>${escapeHtml(t.topic || 'General')}</strong></td>
        <td><span style="font-weight:600; color:var(--text-main);">${escapeHtml(t.subtopic)}</span></td>
        <td class="text-muted" style="font-size:0.8rem; max-width:280px;">${escapeHtml(t.micro_scope || '')}</td>
        <td class="text-right"><strong>${t.total_questions}</strong></td>
        <td class="text-right"><span class="shift-stat-val">${t.shifts_appeared}</span><span class="shift-stat-total">/20</span></td>
        <td class="text-right"><strong>${t.weightage_pct}%</strong></td>
        <td><span class="badge ${yieldBadge}">${t.yield_tag}</span></td>
        <td class="text-center">
          <button class="btn-secondary btn-xs" onclick="startPracticeForTopic('${escapeHtml(t.subtopic)}')">
            Practice
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function setupTopicFilters() {
  const searchInput = document.getElementById('topic-search');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const activeFilter = document.querySelector('#topic-section-filters .filter-pill.active')?.getAttribute('data-filter') || 'all';
      renderTopicsTable(activeFilter, e.target.value);
    });
  }

  document.querySelectorAll('#topic-section-filters .filter-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#topic-section-filters .filter-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.getAttribute('data-filter');
      const searchVal = document.getElementById('topic-search')?.value || '';
      renderTopicsTable(filter, searchVal);
    });
  });

  // Section cards click
  document.querySelectorAll('.sec-card').forEach(card => {
    card.addEventListener('click', () => {
      const sec = card.getAttribute('data-sec');
      const pill = Array.from(document.querySelectorAll('#topic-section-filters .filter-pill')).find(p => p.getAttribute('data-filter') === sec);
      if (pill) pill.click();
      document.getElementById('topics-table')?.scrollIntoView({ behavior: 'smooth' });
    });
  });
}

// ================= Render 20 Shifts Grid =================
function renderPapersGrid() {
  const grid = document.getElementById('paper-grid');
  if (!grid || !globalData) return;

  grid.innerHTML = globalData.papers.map(p => `
    <div class="paper-card" onclick="startMockForPaper(${p.id})">
      <div class="paper-title">Paper ${p.id}</div>
      <div class="paper-date">${escapeHtml(p.date)}</div>
      <div class="paper-shift">${escapeHtml(p.shift)}</div>
      <div class="paper-meta">
        <span>100 Questions</span> • <span>60 Mins</span>
      </div>
      <button class="btn-primary w-full mt-3">Start Full Mock</button>
    </div>
  `).join('');
}

// ================= Question Bank =================
function initQuestionBank() {
  if (!globalData) return;

  // Populate subtopic filter dropdown
  const subtopicFilter = document.getElementById('q-topic-filter');
  if (subtopicFilter) {
    const uniqueSubtopics = [...new Set(globalData.questions.map(q => q.subtopic))].sort();
    subtopicFilter.innerHTML = '<option value="all">All Subcategories</option>' + 
      uniqueSubtopics.map(s => `<option value="${escapeHtml(s)}">${escapeHtml(s)}</option>`).join('');
  }

  // Populate paper filter dropdown
  const paperFilter = document.getElementById('q-paper-filter');
  if (paperFilter) {
    paperFilter.innerHTML = '<option value="all">All 20 Shifts</option>' + 
      globalData.papers.map(p => `<option value="${p.id}">Paper ${p.id} (${p.date})</option>`).join('');
  }

  filterQuestionBank();
}

function setupQuestionBankFilters() {
  ['q-search', 'q-sec-filter', 'q-topic-filter', 'q-paper-filter'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', () => filterQuestionBank());
    if (el) el.addEventListener('change', () => filterQuestionBank());
  });

  document.getElementById('q-reset-filters')?.addEventListener('click', () => {
    const search = document.getElementById('q-search');
    if (search) search.value = '';
    const sec = document.getElementById('q-sec-filter');
    if (sec) sec.value = 'all';
    const top = document.getElementById('q-topic-filter');
    if (top) top.value = 'all';
    const pap = document.getElementById('q-paper-filter');
    if (pap) pap.value = 'all';
    filterQuestionBank();
  });

  document.getElementById('prev-page')?.addEventListener('click', () => {
    if (qbCurrentPage > 1) {
      qbCurrentPage--;
      renderQuestionBankPage();
      window.scrollTo({ top: 300, behavior: 'smooth' });
    }
  });

  document.getElementById('next-page')?.addEventListener('click', () => {
    const totalPages = Math.ceil(qbFiltered.length / QB_PAGE_SIZE);
    if (qbCurrentPage < totalPages) {
      qbCurrentPage++;
      renderQuestionBankPage();
      window.scrollTo({ top: 300, behavior: 'smooth' });
    }
  });
}

function filterQuestionBank() {
  if (!globalData) return;

  const query = document.getElementById('q-search')?.value.toLowerCase().trim() || '';
  const sec = document.getElementById('q-sec-filter')?.value || 'all';
  const sub = document.getElementById('q-topic-filter')?.value || 'all';
  const paper = document.getElementById('q-paper-filter')?.value || 'all';

  qbFiltered = globalData.questions.filter(q => {
    if (sec !== 'all' && q.section !== sec) return false;
    if (sub !== 'all' && q.subtopic !== sub) return false;
    if (paper !== 'all' && q.paper_id.toString() !== paper) return false;
    if (query) {
      const matchStmt = q.statement && q.statement.toLowerCase().includes(query);
      const matchOpts = q.options && q.options.some(opt => opt.toLowerCase().includes(query));
      const matchSub = q.subtopic && q.subtopic.toLowerCase().includes(query);
      if (!matchStmt && !matchOpts && !matchSub) return false;
    }
    return true;
  });

  document.getElementById('q-filtered-count').textContent = qbFiltered.length.toLocaleString();
  qbCurrentPage = 1;
  renderQuestionBankPage();
}

function renderQuestionBankPage() {
  const container = document.getElementById('questions-list');
  if (!container) return;

  const totalPages = Math.ceil(qbFiltered.length / QB_PAGE_SIZE) || 1;
  document.getElementById('page-info').textContent = `Page ${qbCurrentPage} of ${totalPages}`;

  document.getElementById('prev-page').disabled = (qbCurrentPage <= 1);
  document.getElementById('next-page').disabled = (qbCurrentPage >= totalPages);

  const startIdx = (qbCurrentPage - 1) * QB_PAGE_SIZE;
  const pageItems = qbFiltered.slice(startIdx, startIdx + QB_PAGE_SIZE);

  if (pageItems.length === 0) {
    container.innerHTML = `<div class="card text-center py-8 text-muted">No questions found matching your filter criteria.</div>`;
    return;
  }

  const paperMap = {};
  (globalData.papers || []).forEach(p => { paperMap[p.id] = p; });

  const letters = ['A', 'B', 'C', 'D'];

  container.innerHTML = pageItems.map(q => {
    const secBadgeClass = getSectionBadgeClass(q.section);
    const paper = paperMap[q.paper_id];
    const opts = q.options || ['Option 1', 'Option 2', 'Option 3', 'Option 4'];

    return `
      <div class="q-bank-item" id="card-${q.id}">
        <div class="q-bank-top">
          <div class="q-badges">
            <span class="badge ${secBadgeClass}">Q${q.q_num} • ${getShortSection(q.section)}</span>
            <span class="badge-outline"><strong>${escapeHtml(q.topic || '')}</strong></span>
            <span class="badge-outline">${escapeHtml(q.subtopic || '')}</span>
          </div>
          <div style="font-size:0.775rem; color:var(--text-subtle);">
            Paper ${q.paper_id} (${paper ? escapeHtml(paper.date) + ' - ' + escapeHtml(paper.shift) : ''})
          </div>
        </div>

        <!-- Question Statement in Clean Typography Text -->
        <div class="q-statement-box">
          <p class="q-statement-text">${escapeHtml(q.statement || 'Question Text')}</p>
        </div>

        <!-- Real Extracted Option Buttons -->
        <div class="q-bank-options" id="opt-group-${q.id}">
          ${opts.map((optText, idx) => `
            <div class="q-bank-opt" onclick="checkQBankAnswer('${q.id}', ${idx + 1}, ${q.correct_option})">
              <span class="q-bank-opt-key">${letters[idx]}</span>
              <span class="q-bank-opt-val">${escapeHtml(optText || 'Option ' + (idx + 1))}</span>
            </div>
          `).join('')}
        </div>

        <!-- Optional Collapsible Diagram / Scan Toggle -->
        <div class="q-scan-toggle-row">
          <button type="button" class="btn-toggle-diagram" onclick="toggleCardImage('${q.id}')">
            <span>📷 View Response Sheet Scan</span>
          </button>
          <div id="scan-img-${q.id}" class="q-scan-collapsible hidden">
            <img src="${q.card_image}" alt="Original Scan" loading="lazy">
          </div>
        </div>

        <div class="q-bank-bottom">
          <span class="q-answer-reveal" id="ans-text-${q.id}">Official Answer: <em>Hidden</em></span>
          <button class="btn-secondary btn-xs" onclick="revealQBankAnswer('${q.id}', ${q.correct_option})">
            Reveal Answer
          </button>
        </div>
      </div>
    `;
  }).join('');
}

window.toggleCardImage = function(qid) {
  const el = document.getElementById(`scan-img-${qid}`);
  if (el) el.classList.toggle('hidden');
};

window.checkQBankAnswer = function(qid, chosenOpt, correctOpt) {
  const group = document.getElementById(`opt-group-${qid}`);
  if (!group) return;
  const opts = group.querySelectorAll('.q-bank-opt');
  opts.forEach((el, idx) => {
    el.classList.remove('correct', 'wrong');
    const optNum = idx + 1;
    if (optNum === correctOpt) el.classList.add('correct');
    else if (optNum === chosenOpt && chosenOpt !== correctOpt) el.classList.add('wrong');
  });
  revealQBankAnswer(qid, correctOpt);
};

window.revealQBankAnswer = function(qid, correctOpt) {
  const ansText = document.getElementById(`ans-text-${qid}`);
  const letters = ['A', 'B', 'C', 'D'];
  const optLetter = letters[correctOpt - 1] || correctOpt;

  if (ansText) {
    ansText.innerHTML = `Official Answer: <strong>Option (${optLetter})</strong> (Verified Vector Key)`;
    ansText.classList.add('revealed');
  }
  const group = document.getElementById(`opt-group-${qid}`);
  if (group) {
    const opts = group.querySelectorAll('.q-bank-opt');
    opts.forEach((el, idx) => {
      if (idx + 1 === correctOpt) el.classList.add('correct');
    });
  }
};

// ================= Practice & Mock Test Engine =================
function populatePracticeDropdowns() {
  if (!globalData) return;

  // Populate mock paper select
  const mockSelect = document.getElementById('mock-paper-select');
  if (mockSelect) {
    mockSelect.innerHTML = globalData.papers.map(p => 
      `<option value="${p.id}">Paper ${p.id} — ${escapeHtml(p.date)} (${escapeHtml(p.shift)})</option>`
    ).join('');
  }

  // Populate subtopic practice select based on section
  const secSelect = document.getElementById('practice-sec-select');
  if (secSelect) {
    secSelect.addEventListener('change', () => updatePracticeTopicOptions(secSelect.value));
    updatePracticeTopicOptions(secSelect.value);
  }
}

function updatePracticeTopicOptions(sectionName) {
  const topSelect = document.getElementById('practice-topic-select');
  if (!topSelect || !globalData) return;

  const matchingSubtopics = (globalData.subtopics || []).filter(t => t.section === sectionName);
  topSelect.innerHTML = matchingSubtopics.map(t => 
    `<option value="${escapeHtml(t.subtopic)}">${escapeHtml(t.subtopic)} (${t.total_questions} Qs)</option>`
  ).join('');
}

function setupPracticeControls() {
  document.getElementById('btn-start-topic-practice')?.addEventListener('click', () => {
    const subtopic = document.getElementById('practice-topic-select')?.value;
    const countVal = document.getElementById('practice-count-select')?.value;
    if (subtopic) startPracticeForTopic(subtopic, countVal);
  });

  document.getElementById('btn-start-mock-exam')?.addEventListener('click', () => {
    const paperId = parseInt(document.getElementById('mock-paper-select')?.value, 10);
    if (paperId) startMockForPaper(paperId);
  });

  // Test question options click
  document.querySelectorAll('#test-options-container .opt-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const opt = parseInt(btn.getAttribute('data-opt'), 10);
      selectTestAnswer(opt);
    });
  });

  document.getElementById('btn-prev-q')?.addEventListener('click', () => navigateTestQuestion(-1));
  document.getElementById('btn-next-q')?.addEventListener('click', () => navigateTestQuestion(1));
  document.getElementById('btn-clear-q')?.addEventListener('click', () => clearCurrentTestAnswer());
  document.getElementById('btn-review-q')?.addEventListener('click', () => toggleMarkForReview());
  document.getElementById('btn-check-practice-ans')?.addEventListener('click', () => checkActivePracticeAnswer());
  document.getElementById('btn-finish-test')?.addEventListener('click', () => submitActiveTest());

  document.getElementById('btn-retake-test')?.addEventListener('click', () => {
    document.getElementById('test-result-view').classList.add('hidden');
    document.getElementById('practice-selector').classList.remove('hidden');
  });

  document.getElementById('btn-back-to-analytics')?.addEventListener('click', () => {
    switchTab('analytics-tab');
  });

  // Toggle diagram in test view
  document.getElementById('btn-toggle-diagram')?.addEventListener('click', () => {
    const container = document.getElementById('test-q-image-container');
    if (container) container.classList.toggle('hidden');
  });
}

window.startPracticeForTopic = function(subtopicName, countLimit = '20') {
  if (!globalData) return;
  switchTab('practice-tab');

  let questions = globalData.questions.filter(q => q.subtopic === subtopicName);
  if (questions.length === 0) {
    questions = globalData.questions.filter(q => q.topic === subtopicName);
  }

  // Shuffle questions
  questions = [...questions].sort(() => 0.5 - Math.random());
  if (countLimit !== 'all') {
    const limit = parseInt(countLimit, 10);
    if (!isNaN(limit)) questions = questions.slice(0, limit);
  }

  initTestSession({
    mode: 'topic',
    title: `Practice: ${subtopicName}`,
    subtitle: `${questions.length} Targeted Questions • Instant Answer Mode`,
    questions: questions,
    timed: false
  });
};

window.startMockForPaper = function(paperId) {
  if (!globalData) return;
  switchTab('practice-tab');

  const paper = (globalData.papers || []).find(p => p.id === paperId);
  const questions = globalData.questions.filter(q => q.paper_id === paperId);

  initTestSession({
    mode: 'mock',
    title: `SSC CGL Mock: Paper ${paperId}`,
    subtitle: `${paper?.date || ''} (${paper?.shift || ''}) • 100 Questions`,
    questions: questions,
    timed: true,
    seconds: 3600 // 60 minutes
  });
};

function initTestSession({ mode, title, subtitle, questions, timed, seconds = 3600 }) {
  if (activeTest.timerInterval) clearInterval(activeTest.timerInterval);

  activeTest = {
    mode: mode,
    title: title,
    subtitle: subtitle,
    questions: questions,
    currentIndex: 0,
    userAnswers: {},
    reviewMarked: {},
    timerSeconds: seconds,
    timerInterval: null,
    isSubmitted: false
  };

  document.getElementById('practice-selector').classList.add('hidden');
  document.getElementById('test-result-view').classList.add('hidden');
  document.getElementById('active-test-view').classList.remove('hidden');

  document.getElementById('test-title').textContent = title;
  document.getElementById('test-subtitle').textContent = subtitle;

  const timerBox = document.getElementById('test-timer-box');
  const checkAnsBtn = document.getElementById('btn-check-practice-ans');

  if (timed) {
    timerBox.classList.remove('hidden');
    checkAnsBtn.classList.add('hidden');
    startTimer();
  } else {
    timerBox.classList.add('hidden');
    checkAnsBtn.classList.remove('hidden');
  }

  renderTestPalette();
  loadTestQuestion(0);
}

function startTimer() {
  updateTimerDisplay();
  activeTest.timerInterval = setInterval(() => {
    activeTest.timerSeconds--;
    updateTimerDisplay();
    if (activeTest.timerSeconds <= 0) {
      clearInterval(activeTest.timerInterval);
      submitActiveTest();
    }
  }, 1000);
}

function updateTimerDisplay() {
  const m = Math.floor(activeTest.timerSeconds / 60);
  const s = activeTest.timerSeconds % 60;
  document.getElementById('test-timer-val').textContent = 
    `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

function renderTestPalette() {
  const grid = document.getElementById('test-palette-grid');
  if (!grid) return;

  grid.innerHTML = activeTest.questions.map((q, idx) => `
    <button class="pal-btn" id="pal-btn-${idx}" onclick="jumpToTestQuestion(${idx})">
      ${idx + 1}
    </button>
  `).join('');
  updatePaletteState();
}

function updatePaletteState() {
  activeTest.questions.forEach((_, idx) => {
    const btn = document.getElementById(`pal-btn-${idx}`);
    if (!btn) return;

    btn.className = 'pal-btn';
    if (idx === activeTest.currentIndex) btn.classList.add('current');
    if (activeTest.userAnswers[idx] !== undefined) btn.classList.add('answered');
    if (activeTest.reviewMarked[idx]) btn.classList.add('review');
  });
}

function loadTestQuestion(index) {
  if (index < 0 || index >= activeTest.questions.length) return;
  activeTest.currentIndex = index;

  const q = activeTest.questions[index];

  document.getElementById('test-q-num').textContent = `Question ${index + 1} of ${activeTest.questions.length}`;
  document.getElementById('test-q-sec').textContent = getShortSection(q.section);
  document.getElementById('test-q-topic').textContent = q.subtopic || q.topic;
  document.getElementById('test-q-paper').textContent = `Paper ${q.paper_id}`;

  // Question statement in clean typography
  document.getElementById('test-q-statement').textContent = q.statement || 'Question Text';

  // Option text population
  const opts = q.options || ['Option 1', 'Option 2', 'Option 3', 'Option 4'];
  const opt1El = document.getElementById('test-opt-1-text');
  const opt2El = document.getElementById('test-opt-2-text');
  const opt3El = document.getElementById('test-opt-3-text');
  const opt4El = document.getElementById('test-opt-4-text');

  if (opt1El) opt1El.textContent = opts[0] || 'Option 1';
  if (opt2El) opt2El.textContent = opts[1] || 'Option 2';
  if (opt3El) opt3El.textContent = opts[2] || 'Option 3';
  if (opt4El) opt4El.textContent = opts[3] || 'Option 4';

  // Card scan image (hidden by default)
  const imgEl = document.getElementById('test-q-img');
  if (imgEl) {
    imgEl.src = q.card_image;
    document.getElementById('test-q-image-container')?.classList.add('hidden');
  }

  // Option selection state
  const selectedOpt = activeTest.userAnswers[index];
  document.querySelectorAll('#test-options-container .opt-btn').forEach(btn => {
    btn.className = 'opt-btn';
    const optNum = parseInt(btn.getAttribute('data-opt'), 10);
    if (selectedOpt === optNum) btn.classList.add('selected');
  });

  // Hide feedback box
  document.getElementById('practice-feedback-box').classList.add('hidden');

  // Disable Prev on first, change Next label on last
  document.getElementById('btn-prev-q').disabled = (index === 0);
  document.getElementById('btn-next-q').textContent = (index === activeTest.questions.length - 1) ? 'Review' : 'Next';

  updatePaletteState();
}

function selectTestAnswer(optNum) {
  activeTest.userAnswers[activeTest.currentIndex] = optNum;
  document.querySelectorAll('#test-options-container .opt-btn').forEach(btn => {
    const val = parseInt(btn.getAttribute('data-opt'), 10);
    btn.classList.toggle('selected', val === optNum);
  });
  updatePaletteState();
}

function clearCurrentTestAnswer() {
  delete activeTest.userAnswers[activeTest.currentIndex];
  document.querySelectorAll('#test-options-container .opt-btn').forEach(b => b.classList.remove('selected'));
  updatePaletteState();
}

function toggleMarkForReview() {
  const curr = activeTest.currentIndex;
  activeTest.reviewMarked[curr] = !activeTest.reviewMarked[curr];
  updatePaletteState();
}

function navigateTestQuestion(step) {
  const target = activeTest.currentIndex + step;
  if (target >= 0 && target < activeTest.questions.length) {
    loadTestQuestion(target);
  }
}

window.jumpToTestQuestion = function(idx) {
  loadTestQuestion(idx);
};

function checkActivePracticeAnswer() {
  const curr = activeTest.currentIndex;
  const q = activeTest.questions[curr];
  const userAns = activeTest.userAnswers[curr];

  const feedbackBox = document.getElementById('practice-feedback-box');
  const statusMsg = document.getElementById('feedback-status-msg');
  const explanation = document.getElementById('feedback-explanation');
  const letters = ['A', 'B', 'C', 'D'];

  feedbackBox.classList.remove('hidden');

  const correctLetter = letters[q.correct_option - 1] || q.correct_option;
  const correctText = (q.options && q.options[q.correct_option - 1]) ? q.options[q.correct_option - 1] : `Option ${correctLetter}`;

  if (userAns === undefined) {
    statusMsg.className = 'feedback-status text-warning';
    statusMsg.textContent = `Please select an option first. Correct answer is Option (${correctLetter}): "${correctText}"`;
    explanation.textContent = `Concept: ${q.subtopic || q.topic} (${q.micro_scope || ''})`;
    return;
  }

  const isCorrect = (userAns === q.correct_option);

  document.querySelectorAll('#test-options-container .opt-btn').forEach(btn => {
    const optNum = parseInt(btn.getAttribute('data-opt'), 10);
    btn.classList.remove('correct-revealed', 'wrong-revealed');
    if (optNum === q.correct_option) btn.classList.add('correct-revealed');
    else if (optNum === userAns && !isCorrect) btn.classList.add('wrong-revealed');
  });

  if (isCorrect) {
    statusMsg.className = 'feedback-status text-success';
    statusMsg.textContent = `✓ Correct Answer! (+2 Marks)`;
    explanation.textContent = `Verified Official Key: Option (${correctLetter}) — "${correctText}". Topic: ${q.subtopic || q.topic}`;
  } else {
    const userLetter = letters[userAns - 1] || userAns;
    statusMsg.className = 'feedback-status text-danger';
    statusMsg.textContent = `✗ Incorrect. (-0.5 Negative Mark)`;
    explanation.textContent = `You selected (${userLetter}). Correct answer is (${correctLetter}): "${correctText}".`;
  }
}

function submitActiveTest() {
  if (activeTest.timerInterval) clearInterval(activeTest.timerInterval);
  activeTest.isSubmitted = true;

  const total = activeTest.questions.length;
  let correct = 0;
  let incorrect = 0;
  let skipped = 0;

  activeTest.questions.forEach((q, idx) => {
    const ans = activeTest.userAnswers[idx];
    if (ans === undefined) {
      skipped++;
    } else if (ans === q.correct_option) {
      correct++;
    } else {
      incorrect++;
    }
  });

  // SSC Marking: +2 for correct, -0.5 for wrong
  const score = (correct * 2) - (incorrect * 0.5);
  const maxScore = total * 2;
  const accuracy = (correct + incorrect > 0) ? Math.round((correct / (correct + incorrect)) * 100) : 0;
  const scorePct = Math.round((score / maxScore) * 100);

  document.getElementById('active-test-view').classList.add('hidden');
  document.getElementById('test-result-view').classList.remove('hidden');

  document.getElementById('result-meta-sub').textContent = `${activeTest.title} • Completed`;
  document.getElementById('result-score-val').textContent = `${score} / ${maxScore}`;
  document.getElementById('result-score-percent').textContent = `${scorePct}% Net Marks`;
  document.getElementById('result-accuracy-val').textContent = `${accuracy}%`;
  document.getElementById('result-correct-count').textContent = correct;
  document.getElementById('result-incorrect-count').textContent = incorrect;
  document.getElementById('result-skipped-count').textContent = skipped;
}

// ================= Helpers =================
function getShortSection(sec) {
  if (!sec) return 'General';
  if (sec.includes('Reasoning')) return 'Reasoning';
  if (sec.includes('Awareness')) return 'GA (GK)';
  if (sec.includes('Quantitative')) return 'Maths';
  if (sec.includes('English')) return 'English';
  return sec;
}

function getSectionBadgeClass(sec) {
  if (!sec) return '';
  if (sec.includes('Reasoning')) return 'badge-reasoning';
  if (sec.includes('Awareness')) return 'badge-ga';
  if (sec.includes('Quantitative')) return 'badge-maths';
  if (sec.includes('English')) return 'badge-english';
  return '';
}

function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
