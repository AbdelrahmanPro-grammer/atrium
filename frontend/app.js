/**
 * Atrium — Frontend application logic.
 *
 * All API calls and DOM rendering live here, organized under the global
 * `Atrium` namespace. Each page calls the function it needs after DOMContentLoaded.
 */

const Atrium = (() => {

  // -----------------------------------------------------------------------
  // Configuration
  // -----------------------------------------------------------------------

  const API_BASE = 'http://127.0.0.1:5000/api';

  // -----------------------------------------------------------------------
  // API helpers
  // -----------------------------------------------------------------------

  async function apiRequest(path, options = {}) {
    const url = `${API_BASE}${path}`;
    const response = await fetch(url, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const message = data.message || `Request failed (${response.status})`;
      throw new Error(message);
    }
    return data;
  }

  // -----------------------------------------------------------------------
  // Utilities
  // -----------------------------------------------------------------------

  function escapeHtml(value) {
    if (value == null) return '';
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function formatDate(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString.replace(' ', 'T') + 'Z');
    const now = new Date();
    const diffMs = now - date;
    const diffMin = Math.floor(diffMs / 60000);
    const diffHr = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHr / 24);

    if (diffMin < 1) return 'just now';
    if (diffMin < 60) return `${diffMin} min ago`;
    if (diffHr < 24) return `${diffHr} hr ago`;
    if (diffDay < 7) return `${diffDay} day${diffDay === 1 ? '' : 's'} ago`;
    return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  }

  function getQueryParam(name) {
    return new URLSearchParams(window.location.search).get(name);
  }

  // -----------------------------------------------------------------------
  // Insight card rendering
  // -----------------------------------------------------------------------

  function renderInsightCard(insight, options = {}) {
    const includeProfessor = options.includeProfessor !== false;

    const metaParts = [];
    if (includeProfessor && insight.professor_name) {
      metaParts.push(`<span class="professor-name">${escapeHtml(insight.professor_name)}</span>`);
    }
    if (insight.course_code) {
      metaParts.push(`<span class="course-code">${escapeHtml(insight.course_code)}</span>`);
    }
    if (insight.course_name) {
      metaParts.push(`<span>${escapeHtml(insight.course_name)}</span>`);
    }
    metaParts.push(`<span>${formatDate(insight.created_at)}</span>`);

    const attributes = [];
    if (insight.workload) {
      attributes.push(`<span class="insight-attribute"><strong>Workload:</strong> ${escapeHtml(insight.workload)}</span>`);
    }
    if (insight.clarity != null) {
      attributes.push(`<span class="insight-attribute"><strong>Clarity:</strong> ${insight.clarity} / 5</span>`);
    }
    if (insight.fairness != null) {
      attributes.push(`<span class="insight-attribute"><strong>Fairness:</strong> ${insight.fairness} / 5</span>`);
    }

    return `
      <article class="insight-card" data-insight-id="${insight.id}">
        <div class="insight-meta">${metaParts.join('<span>·</span>')}</div>
        <p class="insight-text">${escapeHtml(insight.text)}</p>
        ${attributes.length ? `<div class="insight-attributes">${attributes.join('')}</div>` : ''}
        <div class="insight-footer">
          <span class="helpful-count">${insight.helpful_count || 0} found this helpful</span>
          <button class="helpful-button" data-insight-id="${insight.id}">Found this helpful</button>
        </div>
      </article>
    `;
  }

  function attachHelpfulHandlers(container) {
    container.querySelectorAll('.helpful-button').forEach(button => {
      button.addEventListener('click', async () => {
        const insightId = button.dataset.insightId;
        button.disabled = true;
        try {
          await apiRequest(`/insights/${insightId}/helpful`, { method: 'POST' });
          const card = button.closest('.insight-card');
          const countEl = card.querySelector('.helpful-count');
          const current = parseInt(countEl.textContent, 10) || 0;
          countEl.textContent = `${current + 1} found this helpful`;
          button.textContent = 'Marked';
        } catch (err) {
          button.disabled = false;
          alert(`Could not mark helpful: ${err.message}`);
        }
      });
    });
  }

  // -----------------------------------------------------------------------
  // Page: index.html
  // -----------------------------------------------------------------------

  async function renderRecentInsights(containerId) {
    const container = document.getElementById(containerId);
    try {
      const insights = await apiRequest('/insights?limit=30');
      if (insights.length === 0) {
        container.innerHTML = `<div class="empty-state">No insights yet.</div>`;
        return;
      }
      container.innerHTML = insights.map(i => renderInsightCard(i)).join('');
      attachHelpfulHandlers(container);
    } catch (err) {
      container.innerHTML = `<div class="error-message">Could not load insights: ${escapeHtml(err.message)}</div>`;
    }
  }

  // -----------------------------------------------------------------------
  // Page: professors.html
  // -----------------------------------------------------------------------

  async function renderProfessorList(containerId, searchInputId) {
    const container = document.getElementById(containerId);
    const searchInput = document.getElementById(searchInputId);
    let allProfessors = [];

    function display(filtered) {
      if (filtered.length === 0) {
        container.innerHTML = `<div class="empty-state">No professors match that search.</div>`;
        return;
      }
      container.innerHTML = `
        <ul class="professor-list">
          ${filtered.map(p => `
            <li class="professor-item">
              <a class="professor-link" href="professor.html?id=${p.id}">
                <div class="professor-name-row">${escapeHtml(p.name)}</div>
                <div class="professor-department">${escapeHtml(p.department)}</div>
              </a>
            </li>
          `).join('')}
        </ul>
      `;
    }

    try {
      allProfessors = await apiRequest('/professors');
      display(allProfessors);

      searchInput.addEventListener('input', () => {
        const query = searchInput.value.trim().toLowerCase();
        if (!query) {
          display(allProfessors);
          return;
        }
        const filtered = allProfessors.filter(p =>
          p.name.toLowerCase().includes(query) ||
          p.department.toLowerCase().includes(query)
        );
        display(filtered);
      });
    } catch (err) {
      container.innerHTML = `<div class="error-message">Could not load professors: ${escapeHtml(err.message)}</div>`;
    }
  }

  // -----------------------------------------------------------------------
  // Page: professor.html
  // -----------------------------------------------------------------------

  async function renderProfessorDetail(containerIds) {
    const { headerId, insightsId, formId } = containerIds;
    const headerEl = document.getElementById(headerId);
    const insightsEl = document.getElementById(insightsId);
    const formEl = document.getElementById(formId);

    const professorId = parseInt(getQueryParam('id'), 10);
    if (!professorId) {
      headerEl.innerHTML = `<div class="error-message">No professor specified.</div>`;
      return;
    }

    try {
      const [detail, courses] = await Promise.all([
        apiRequest(`/professors/${professorId}`),
        apiRequest('/courses'),
      ]);

      headerEl.innerHTML = `
        <h2 class="section-title">${escapeHtml(detail.professor.name)}</h2>
        <p class="section-subtitle">${escapeHtml(detail.professor.department)}</p>
      `;

      if (detail.insights.length === 0) {
        insightsEl.innerHTML = `<div class="empty-state">No insights yet for this professor. Be the first to share.</div>`;
      } else {
        insightsEl.innerHTML = detail.insights
          .map(i => renderInsightCard(i, { includeProfessor: false }))
          .join('');
        attachHelpfulHandlers(insightsEl);
      }

      buildInsightForm(formEl, professorId, courses);

    } catch (err) {
      headerEl.innerHTML = `<div class="error-message">Could not load professor: ${escapeHtml(err.message)}</div>`;
    }
  }

  function buildInsightForm(formEl, professorId, courses) {
    formEl.innerHTML = `
      <h3 class="section-title">Share what you learned</h3>
      <div class="form-help">
        Atrium is for academic insight, not personal judgment. Please describe how the
        course was structured, what kind of preparation worked, or advice for students
        considering this course.
      </div>

      <form id="insight-form">
        <div class="form-field">
          <label for="course-select">Course</label>
          <select id="course-select" required>
            <option value="">Select a course…</option>
            ${courses.map(c => `
              <option value="${c.id}">${escapeHtml(c.code)} — ${escapeHtml(c.name)}</option>
            `).join('')}
          </select>
        </div>

        <div class="form-field">
          <label for="text-input">Your insight</label>
          <textarea id="text-input" required maxlength="2000"
            placeholder="What helped you in this course? What would you tell a student considering it?"></textarea>
        </div>

        <div class="form-row">
          <div class="form-field">
            <label for="workload-select">Workload <span class="form-optional">(optional)</span></label>
            <select id="workload-select">
              <option value="">—</option>
              <option value="light">Light</option>
              <option value="moderate">Moderate</option>
              <option value="heavy">Heavy</option>
            </select>
          </div>
          <div class="form-field">
            <label for="clarity-select">Clarity <span class="form-optional">(optional)</span></label>
            <select id="clarity-select">
              <option value="">—</option>
              <option value="1">1</option><option value="2">2</option>
              <option value="3">3</option><option value="4">4</option>
              <option value="5">5</option>
            </select>
          </div>
          <div class="form-field">
            <label for="fairness-select">Fairness <span class="form-optional">(optional)</span></label>
            <select id="fairness-select">
              <option value="">—</option>
              <option value="1">1</option><option value="2">2</option>
              <option value="3">3</option><option value="4">4</option>
              <option value="5">5</option>
            </select>
          </div>
        </div>

        <div id="form-status"></div>
        <button type="submit" class="submit-button">Share insight</button>
      </form>
    `;

    const form = formEl.querySelector('#insight-form');
    const statusEl = formEl.querySelector('#form-status');
    const submitBtn = formEl.querySelector('.submit-button');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      statusEl.innerHTML = '';

      const courseId = parseInt(form.querySelector('#course-select').value, 10);
      const text = form.querySelector('#text-input').value.trim();
      const workload = form.querySelector('#workload-select').value || null;
      const clarityRaw = form.querySelector('#clarity-select').value;
      const fairnessRaw = form.querySelector('#fairness-select').value;

      if (!courseId || !text) {
        statusEl.innerHTML = `<div class="error-message">Please select a course and write your insight.</div>`;
        return;
      }

      const payload = {
        professor_id: professorId,
        course_id: courseId,
        text,
      };
      if (workload) payload.workload = workload;
      if (clarityRaw) payload.clarity = parseInt(clarityRaw, 10);
      if (fairnessRaw) payload.fairness = parseInt(fairnessRaw, 10);

      submitBtn.disabled = true;
      submitBtn.textContent = 'Sharing…';

      try {
        await apiRequest('/insights', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        statusEl.innerHTML = `<div class="success-message">Thank you. Your insight has been shared.</div>`;
        form.reset();
        setTimeout(() => window.location.reload(), 1200);
      } catch (err) {
        statusEl.innerHTML = `<div class="error-message">${escapeHtml(err.message)}</div>`;
        submitBtn.disabled = false;
        submitBtn.textContent = 'Share insight';
      }
    });
  }

  // -----------------------------------------------------------------------
  // Public API
  // -----------------------------------------------------------------------

  return {
    renderRecentInsights,
    renderProfessorList,
    renderProfessorDetail,
  };

})();