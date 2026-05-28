/**
 * Dynamic Publications Loader
 * Loads and displays publications from JSON file
 * Author: Ahmad Luky Ramdani
 */

class PublicationManager {
    constructor(dataUrl = 'data/publications.json') {
        this.dataUrl = dataUrl;
        this.data = null;
    }

    async loadPublications() {
        try {
            const response = await fetch(this.dataUrl);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.data = await response.json();
            return this.data;
        } catch (error) {
            console.error('Error loading publications:', error);
            this.showError('Gagal memuat data publikasi. Menggunakan data contoh.');
            return this.getFallbackData();
        }
    }

    getFallbackData() {
        return {
            lastUpdated: new Date().toISOString().split('T')[0],
            publications: [],
            presentations: []
        };
    }

    renderPublications(containerId = 'publications-container') {
        const container = document.getElementById(containerId);
        if (!container || !this.data) return;

        const publications = this.data.publications || [];
        
        if (publications.length === 0) {
            container.innerHTML = '<p class="text-muted"><i>Belum ada publikasi yang ditambahkan.</i></p>';
            return;
        }

        const publicationHTML = publications.map((pub, index) => `
            <li>
                <div class="pub-content">
                    <span class="pub-title">${this.escapeHtml(pub.title)}</span>
                    <div class="pub-details">
                        <small class="text-muted">
                            ${this.escapeHtml(pub.authors)} - 
                            <i>${this.escapeHtml(pub.venue)}, ${pub.year}</i>
                            ${pub.citations > 0 ? `<span class="badge bg-secondary ms-2">${pub.citations} citations</span>` : ''}
                        </small>
                    </div>
                </div>
                ${pub.pdfUrl ? `<a href="${this.escapeHtml(pub.pdfUrl)}" class="pdf-link" target="_blank"><i class="fas fa-file-pdf"></i> PDF</a>` : ''}
            </li>
        `).join('');

        container.innerHTML = publicationHTML;
    }

    renderPresentations(containerId = 'presentations-container') {
        const container = document.getElementById(containerId);
        if (!container || !this.data) return;

        const presentations = this.data.presentations || [];
        
        if (presentations.length === 0) {
            container.innerHTML = '<p class="text-muted"><i>Belum ada presentasi yang ditambahkan.</i></p>';
            return;
        }

        const presentationHTML = presentations.map((pres, index) => `
            <li>
                <div class="pub-content">
                    <span class="pub-title">${this.escapeHtml(pres.title)}</span>
                    <div class="pub-details">
                        <small class="text-muted">
                            ${this.escapeHtml(pres.event)}
                            ${pres.location ? ` - ${this.escapeHtml(pres.location)}` : ''}
                            ${pres.date ? ` (${this.formatDate(pres.date)})` : ''}
                        </small>
                    </div>
                </div>
                ${pres.slidesUrl ? `<a href="${this.escapeHtml(pres.slidesUrl)}" class="pdf-link" target="_blank"><i class="fas fa-file-powerpoint"></i> Slides</a>` : ''}
            </li>
        `).join('');

        container.innerHTML = presentationHTML;
    }

    renderStats(containerId = 'stats-container') {
        const container = document.getElementById(containerId);
        if (!container || !this.data) return;

        const stats = `
            <div class="stats-bar">
                <div class="stat-item">
                    <i class="fas fa-file-alt"></i>
                    <strong>${this.data.publications?.length || 0}</strong>
                    <span>Publications</span>
                </div>
                <div class="stat-item">
                    <i class="fas fa-quote-right"></i>
                    <strong>${this.data.totalCitations || 0}</strong>
                    <span>Citations</span>
                </div>
                <div class="stat-item">
                    <i class="fas fa-presentation"></i>
                    <strong>${this.data.presentations?.length || 0}</strong>
                    <span>Presentations</span>
                </div>
                ${this.data.lastUpdated ? `
                <div class="stat-item">
                    <i class="fas fa-sync-alt"></i>
                    <small>Updated: ${this.formatDate(this.data.lastUpdated)}</small>
                </div>
                ` : ''}
            </div>
        `;

        container.innerHTML = stats;
    }

    showError(message) {
        console.warn(message);
        // You can add UI notification here if needed
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('id-ID', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
    }

    async init() {
        await this.loadPublications();
        this.renderStats();
        this.renderPublications();
        this.renderPresentations();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const pubManager = new PublicationManager();
    pubManager.init();
});
