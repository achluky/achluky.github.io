/**
 * Course Detail Loader
 * Renders a course detail page (header, info panel, weekly RPS accordion)
 * from a per-course JSON file. Set `window.COURSE_DATA_URL` before loading
 * this script to point at the right data file (defaults to 'data.json').
 * Author: Ahmad Luky Ramdani
 */

(function () {
    function escapeHtml(value) {
        const div = document.createElement('div');
        div.textContent = value == null ? '' : String(value);
        return div.innerHTML;
    }

    function renderBadges(container, badges) {
        container.innerHTML = (badges || [])
            .map(badge => `<span class="badge">${escapeHtml(badge)}</span>`)
            .join('');
    }

    function renderInfoGrid(container, info) {
        const entries = Object.entries(info || {});
        container.innerHTML = entries.map(([label, values]) => {
            const clean = (values || []).filter(v => v !== null && String(v).trim() !== '');
            const value = clean.length ? clean.map(escapeHtml).join('<br>') : '&nbsp;';
            return `
                <div class="info-cell">
                    <span class="info-label">${escapeHtml(label)}</span>
                    ${value}
                </div>`;
        }).join('');
    }

    function renderObjective(objective) {
        if (Array.isArray(objective)) {
            return `<ul class="topic-list">${objective.map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`;
        }
        return escapeHtml(objective);
    }

    function renderMaterials(materials) {
        if (!materials || !materials.length) return '';
        const links = materials.map(m => {
            const target = m.external ? ' target="_blank" rel="noopener"' : '';
            return `<a href="${escapeHtml(m.href)}" class="link-btn"${target}><i class="${escapeHtml(m.icon || 'fas fa-file')}"></i> ${escapeHtml(m.label)}</a>`;
        }).join('');
        return `<div class="material-links"><h6>Materi & Link:</h6>${links}</div>`;
    }

    function renderAssessment(assessment) {
        if (assessment === undefined || assessment === null) return '';
        return `<div class="assessment-box"><strong>Tugas:</strong> ${escapeHtml(assessment)}</div>`;
    }

    function renderWeek(week) {
        return `
            <div class="week-card">
                <div class="week-header">
                    <span class="week-number">${escapeHtml(week.number)}</span>
                    <h4 class="week-title">${escapeHtml(week.title)}</h4>
                    <i class="fas fa-chevron-down week-icon"></i>
                </div>
                <div class="week-content">
                    <div class="learning-objective">
                        <strong>Tujuan Pembelajaran:</strong>
                        ${renderObjective(week.objective)}
                    </div>
                    <div class="learning-objective">
                        <strong>Topik Bahasan</strong>
                        <ul class="topic-list">${(week.topics || []).map(t => `<li>${escapeHtml(t)}</li>`).join('')}</ul>
                    </div>
                    ${renderMaterials(week.materials)}
                    ${renderAssessment(week.assessment)}
                </div>
            </div>`;
    }

    function renderWeeks(container, weeks) {
        container.innerHTML = (weeks || []).map(renderWeek).join('');
        container.querySelectorAll('.week-header').forEach(header => {
            header.addEventListener('click', function () {
                const card = this.parentElement;
                const wasActive = card.classList.contains('active');
                container.querySelectorAll('.week-card').forEach(c => c.classList.remove('active'));
                if (!wasActive) card.classList.add('active');
            });
        });
    }

    function showLoadError(container, message) {
        container.innerHTML = `<div class="assessment-box">${escapeHtml(message)}</div>`;
    }

    async function init() {
        const url = window.COURSE_DATA_URL || 'data.json';
        const titleEl = document.getElementById('course-title');
        const badgesEl = document.getElementById('course-badges');
        const bioEl = document.getElementById('course-bio');
        const infoEl = document.getElementById('info-grid');
        const weeksEl = document.getElementById('weeks-container');

        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();

            if (titleEl) titleEl.textContent = data.title || '';
            if (badgesEl) renderBadges(badgesEl, data.badges);
            if (bioEl) bioEl.textContent = data.description || '';
            if (infoEl) renderInfoGrid(infoEl, data.info);
            if (weeksEl) renderWeeks(weeksEl, data.weeks);
        } catch (error) {
            console.error('Gagal memuat data mata kuliah:', error);
            if (weeksEl) {
                showLoadError(weeksEl, 'Gagal memuat data mata kuliah (RPS). Periksa file data.json di folder ini.');
            }
        }
    }

    document.addEventListener('DOMContentLoaded', init);
})();
