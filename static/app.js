// Application State
const state = {
    search: '',
    country: '',
    price_range: '',
    min_rating: '',
    min_reviews: '',
    has_phone: false,
    has_website: false,
    sort_by: 'lead_score',
    sort_order: 'DESC',
    page: 1,
    limit: 24,
    viewMode: 'card', // 'card' or 'list'
    savedViews: JSON.parse(localStorage.getItem('clutch_saved_views') || '[]')
};

// DOM Elements
const searchInput = document.getElementById('searchInput');
const countryFilter = document.getElementById('countryFilter');
const priceFilter = document.getElementById('priceFilter');
const ratingFilter = document.getElementById('ratingFilter');
const reviewsFilter = document.getElementById('reviewsFilter');
const phoneOnlyCheck = document.getElementById('phoneOnlyCheck');
const websiteOnlyCheck = document.getElementById('websiteOnlyCheck');
const sortBySelect = document.getElementById('sortBySelect');
const sortOrderBtn = document.getElementById('sortOrderBtn');
const sortOrderIcon = document.getElementById('sortOrderIcon');
const resetFiltersBtn = document.getElementById('resetFiltersBtn');
const saveCurrentViewBtn = document.getElementById('saveCurrentViewBtn');

const cardViewBtn = document.getElementById('cardViewBtn');
const listViewBtn = document.getElementById('listViewBtn');
const cardsGrid = document.getElementById('cardsGrid');
const tableContainer = document.getElementById('tableContainer');
const tableBody = document.getElementById('tableBody');

const prevPageBtn = document.getElementById('prevPageBtn');
const nextPageBtn = document.getElementById('nextPageBtn');
const currentPageNum = document.getElementById('currentPageNum');
const totalPagesNum = document.getElementById('totalPagesNum');
const matchedCount = document.getElementById('matchedCount');
const totalCountBadge = document.getElementById('totalCountBadge');

// Drawer Elements
const drawerOverlay = document.getElementById('drawerOverlay');
const detailDrawer = document.getElementById('detailDrawer');
const closeDrawerBtn = document.getElementById('closeDrawerBtn');

// Modal Elements
const savedViewsBtn = document.getElementById('savedViewsBtn');
const savedViewsModal = document.getElementById('savedViewsModal');
const savedViewsCount = document.getElementById('savedViewsCount');
const savedViewsList = document.getElementById('savedViewsList');

const openExportBtn = document.getElementById('openExportBtn');
const exportModal = document.getElementById('exportModal');
const confirmExportBtn = document.getElementById('confirmExportBtn');
const selectAllColsBtn = document.getElementById('selectAllColsBtn');
const deselectAllColsBtn = document.getElementById('deselectAllColsBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    fetchMeta();
    fetchCompanies();
    updateSavedViewsCount();
    setupEventListeners();
});

// Fetch Metadata (Countries, Price Ranges, Total)
async function fetchMeta() {
    try {
        const res = await fetch('/api/meta');
        const meta = await res.json();
        totalCountBadge.textContent = meta.total_companies.toLocaleString();

        meta.countries.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c;
            opt.textContent = c;
            countryFilter.appendChild(opt);
        });

        meta.price_ranges.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p;
            opt.textContent = p;
            priceFilter.appendChild(opt);
        });
    } catch (err) {
        console.error("Error fetching meta:", err);
    }
}

// Fetch Companies with Filters & Pagination
async function fetchCompanies() {
    cardsGrid.innerHTML = `<div class="loading-spinner"><i class="fa-solid fa-spinner fa-spin"></i> Loading DuckDB dataset...</div>`;
    tableBody.innerHTML = `<tr><td colspan="8"><i class="fa-solid fa-spinner fa-spin"></i> Loading...</td></tr>`;

    const params = new URLSearchParams({
        search: state.search,
        country: state.country,
        price_range: state.price_range,
        min_rating: state.min_rating,
        min_reviews: state.min_reviews,
        has_phone: state.has_phone,
        has_website: state.has_website,
        sort_by: state.sort_by,
        sort_order: state.sort_order,
        page: state.page,
        limit: state.limit
    });

    try {
        const res = await fetch(`/api/companies?${params.toString()}`);
        const data = await res.json();

        matchedCount.textContent = data.total.toLocaleString();
        currentPageNum.textContent = data.page;
        totalPagesNum.textContent = data.total_pages;

        prevPageBtn.disabled = data.page <= 1;
        nextPageBtn.disabled = data.page >= data.total_pages;

        if (state.viewMode === 'card') {
            renderCards(data.items);
        } else {
            renderTable(data.items);
        }
    } catch (err) {
        console.error("Error fetching companies:", err);
        cardsGrid.innerHTML = `<div class="error-msg">Error loading dataset. Please check backend server.</div>`;
    }
}

// Render Card Grid View
function renderCards(items) {
    if (!items.length) {
        cardsGrid.innerHTML = `<div class="empty-msg">No agencies match your criteria. Try loosening filters.</div>`;
        return;
    }

    cardsGrid.innerHTML = items.map(item => {
        const rating = item.rating ? `${item.rating} ⭐` : 'Unrated';
        const reviews = item.review_count || 0;
        const location = [item.locality, item.country].filter(Boolean).join(', ') || 'Global';
        const services = (item.services_offered || '').split(',').slice(0, 3).filter(Boolean);

        return `
            <div class="agency-card">
                <div class="card-header">
                    <div class="card-title-group">
                        <h3>${escapeHtml(item.company_name)}</h3>
                        <div class="card-location"><i class="fa-solid fa-location-dot"></i> ${escapeHtml(location)}</div>
                    </div>
                    <span class="lead-score-pill" title="Lead Quality Score">Score: ${item.lead_score}</span>
                </div>

                <div class="card-metrics">
                    <div class="metric-item rating-item"><i class="fa-solid fa-star"></i> ${rating} (${reviews})</div>
                    ${item.price_range ? `<div class="metric-item"><i class="fa-solid fa-tag"></i> ${escapeHtml(item.price_range)}</div>` : ''}
                    ${item.founding_year ? `<div class="metric-item"><i class="fa-solid fa-calendar"></i> ${escapeHtml(item.founding_year)}</div>` : ''}
                </div>

                <div class="card-services">
                    ${services.map(s => `<span class="service-tag">${escapeHtml(s.trim())}</span>`).join('')}
                </div>

                <div class="card-footer">
                    <div class="card-actions">
                        ${item.official_website ? `<a href="${escapeHtml(item.official_website)}" target="_blank" title="Visit Website"><i class="fa-solid fa-globe"></i></a>` : ''}
                        ${item.phone ? `<a href="tel:${escapeHtml(item.phone)}" title="Call Agency"><i class="fa-solid fa-phone"></i></a>` : ''}
                    </div>
                    <button class="btn btn-secondary btn-sm view-detail-btn" data-company='${encodeURIComponent(JSON.stringify(item))}'>
                        View Details <i class="fa-solid fa-arrow-right"></i>
                    </button>
                </div>
            </div>
        `;
    }).join('');

    attachDetailClickHandlers();
}

// Render List / Table View
function renderTable(items) {
    if (!items.length) {
        tableBody.innerHTML = `<tr><td colspan="8" class="text-center">No agencies found.</td></tr>`;
        return;
    }

    tableBody.innerHTML = items.map(item => {
        const rating = item.rating ? `${item.rating} ⭐` : '-';
        const location = [item.locality, item.country].filter(Boolean).join(', ') || '-';

        return `
            <tr>
                <td><strong>${escapeHtml(item.company_name)}</strong></td>
                <td>${escapeHtml(location)}</td>
                <td><span class="text-amber">${rating}</span></td>
                <td>${item.review_count || 0}</td>
                <td>${escapeHtml(item.price_range || '-')}</td>
                <td><span class="lead-score-pill">Score: ${item.lead_score}</span></td>
                <td>
                    ${item.official_website ? `<a href="${escapeHtml(item.official_website)}" target="_blank" class="icon-link"><i class="fa-solid fa-globe"></i></a>` : ''}
                    ${item.phone ? `<a href="tel:${escapeHtml(item.phone)}" class="icon-link"><i class="fa-solid fa-phone"></i></a>` : ''}
                </td>
                <td>
                    <button class="btn btn-secondary btn-sm view-detail-btn" data-company='${encodeURIComponent(JSON.stringify(item))}'>
                        Inspect
                    </button>
                </td>
            </tr>
        `;
    }).join('');

    attachDetailClickHandlers();
}

// Attach Drawer Inspect Click Handlers
function attachDetailClickHandlers() {
    document.querySelectorAll('.view-detail-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const rawData = e.currentTarget.getAttribute('data-company');
            const company = JSON.parse(decodeURIComponent(rawData));
            openDrawer(company);
        });
    });
}

// Open Side Drawer
function openDrawer(company) {
    document.getElementById('drawerCompanyName').textContent = company.company_name;
    document.getElementById('drawerLeadScore').textContent = `Lead Score: ${company.lead_score}/100`;
    document.getElementById('drawerRating').textContent = company.rating ? `${company.rating} ⭐ (${company.review_count || 0} Reviews)` : 'No Ratings Yet';

    const location = [company.street_address, company.locality, company.region, company.country].filter(Boolean).join(', ');
    const reviews = company.reviews_sample || [];

    const bodyHtml = `
        <div class="detail-section">
            <h4><i class="fa-solid fa-address-card"></i> Contact & HQ Information</h4>
            <div class="detail-grid">
                <div class="detail-card">
                    <div class="label">Official Website</div>
                    <div class="value">${company.official_website ? `<a href="${escapeHtml(company.official_website)}" target="_blank" class="link">${escapeHtml(company.official_website)}</a>` : 'Not Listed'}</div>
                </div>
                <div class="detail-card">
                    <div class="label">Direct Phone</div>
                    <div class="value">${company.phone ? `<a href="tel:${escapeHtml(company.phone)}" class="link">${escapeHtml(company.phone)}</a>` : 'Not Listed'}</div>
                </div>
                <div class="detail-card" style="grid-column: span 2;">
                    <div class="label">Headquarters Address</div>
                    <div class="value">${escapeHtml(location || 'Not Listed')}</div>
                </div>
            </div>
        </div>

        <div class="detail-section">
            <h4><i class="fa-solid fa-chart-pie"></i> Firmographic Overview</h4>
            <div class="detail-grid">
                <div class="detail-card">
                    <div class="label">Founding Year</div>
                    <div class="value">${escapeHtml(company.founding_year || 'Unknown')}</div>
                </div>
                <div class="detail-card">
                    <div class="label">Price Range / Hour</div>
                    <div class="value">${escapeHtml(company.price_range || 'Undisclosed')}</div>
                </div>
            </div>
        </div>

        ${company.services_offered ? `
            <div class="detail-section">
                <h4><i class="fa-solid fa-list-check"></i> Services Offered Catalog</h4>
                <div class="card-services">
                    ${company.services_offered.split(',').map(s => `<span class="service-tag">${escapeHtml(s.trim())}</span>`).join('')}
                </div>
            </div>
        ` : ''}

        ${company.description ? `
            <div class="detail-section">
                <h4><i class="fa-solid fa-circle-info"></i> Company Description</h4>
                <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6;">${escapeHtml(company.description)}</p>
            </div>
        ` : ''}

        ${reviews.length ? `
            <div class="detail-section">
                <h4><i class="fa-solid fa-comments"></i> Extracted Verified Client Feedback (${reviews.length})</h4>
                ${reviews.map(r => `
                    <div class="review-card-item">
                        <div class="review-card-header">
                            <span>${escapeHtml(r.title || 'Client Review')}</span>
                            <span class="text-amber">${r.rating ? `${r.rating} ⭐` : ''}</span>
                        </div>
                        <div class="review-card-body">"${escapeHtml(r.body || '')}"</div>
                        <div style="font-size:11px; color:var(--text-dim); margin-top:4px;">By: ${escapeHtml(r.author || 'Verified Client')}</div>
                    </div>
                `).join('')}
            </div>
        ` : ''}
    `;

    document.getElementById('drawerBody').innerHTML = bodyHtml;
    drawerOverlay.style.display = 'block';
    detailDrawer.classList.add('open');
}

// Close Drawer
function closeDrawer() {
    detailDrawer.classList.remove('open');
    drawerOverlay.style.display = 'none';
}

// Setup Event Listeners
function setupEventListeners() {
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        state.search = e.target.value;
        searchTimeout = setTimeout(() => {
            state.page = 1;
            fetchCompanies();
        }, 300);
    });

    countryFilter.addEventListener('change', (e) => { state.country = e.target.value; state.page = 1; fetchCompanies(); });
    priceFilter.addEventListener('change', (e) => { state.price_range = e.target.value; state.page = 1; fetchCompanies(); });
    ratingFilter.addEventListener('change', (e) => { state.min_rating = e.target.value; state.page = 1; fetchCompanies(); });
    reviewsFilter.addEventListener('change', (e) => { state.min_reviews = e.target.value; state.page = 1; fetchCompanies(); });
    phoneOnlyCheck.addEventListener('change', (e) => { state.has_phone = e.target.checked; state.page = 1; fetchCompanies(); });
    websiteOnlyCheck.addEventListener('change', (e) => { state.has_website = e.target.checked; state.page = 1; fetchCompanies(); });

    sortBySelect.addEventListener('change', (e) => { state.sort_by = e.target.value; fetchCompanies(); });
    sortOrderBtn.addEventListener('click', () => {
        state.sort_order = state.sort_order === 'DESC' ? 'ASC' : 'DESC';
        sortOrderIcon.className = state.sort_order === 'DESC' ? 'fa-solid fa-arrow-down-wide-short' : 'fa-solid fa-arrow-up-short-wide';
        fetchCompanies();
    });

    resetFiltersBtn.addEventListener('click', () => {
        searchInput.value = '';
        countryFilter.value = '';
        priceFilter.value = '';
        ratingFilter.value = '';
        reviewsFilter.value = '';
        phoneOnlyCheck.checked = false;
        websiteOnlyCheck.checked = false;

        state.search = '';
        state.country = '';
        state.price_range = '';
        state.min_rating = '';
        state.min_reviews = '';
        state.has_phone = false;
        state.has_website = false;
        state.page = 1;
        fetchCompanies();
    });

    cardViewBtn.addEventListener('click', () => {
        cardViewBtn.classList.add('active');
        listViewBtn.classList.remove('active');
        cardsGrid.style.display = 'grid';
        tableContainer.style.display = 'none';
        state.viewMode = 'card';
        fetchCompanies();
    });

    listViewBtn.addEventListener('click', () => {
        listViewBtn.classList.add('active');
        cardViewBtn.classList.remove('active');
        cardsGrid.style.display = 'none';
        tableContainer.style.display = 'block';
        state.viewMode = 'list';
        fetchCompanies();
    });

    prevPageBtn.addEventListener('click', () => { if (state.page > 1) { state.page--; fetchCompanies(); } });
    nextPageBtn.addEventListener('click', () => { state.page++; fetchCompanies(); });

    closeDrawerBtn.addEventListener('click', closeDrawer);
    drawerOverlay.addEventListener('click', closeDrawer);

    // Saved Views Modal
    savedViewsBtn.addEventListener('click', () => {
        renderSavedViews();
        savedViewsModal.style.display = 'flex';
    });

    saveCurrentViewBtn.addEventListener('click', () => {
        const name = prompt("Enter custom name for this filter view (e.g. 'US High Ticket Agencies'):");
        if (name) {
            const newView = {
                id: Date.now(),
                name: name,
                state: { ...state }
            };
            state.savedViews.push(newView);
            localStorage.setItem('clutch_saved_views', JSON.stringify(state.savedViews));
            updateSavedViewsCount();
            alert(`Saved view '${name}' successfully!`);
        }
    });

    // Export Modal
    openExportBtn.addEventListener('click', () => { exportModal.style.display = 'flex'; });

    document.querySelectorAll('.closeModalBtn').forEach(btn => {
        btn.addEventListener('click', () => {
            savedViewsModal.style.display = 'none';
            exportModal.style.display = 'none';
        });
    });

    selectAllColsBtn.addEventListener('click', () => {
        document.querySelectorAll('#columnsGrid input').forEach(c => c.checked = true);
    });
    deselectAllColsBtn.addEventListener('click', () => {
        document.querySelectorAll('#columnsGrid input').forEach(c => c.checked = false);
    });

    confirmExportBtn.addEventListener('click', async () => {
        const selectedFormat = document.querySelector('input[name="exportFormat"]:checked').value;
        const selectedCols = Array.from(document.querySelectorAll('#columnsGrid input:checked')).map(c => c.value);

        const payload = {
            search: state.search,
            country: state.country,
            price_range: state.price_range,
            min_rating: state.min_rating,
            min_reviews: state.min_reviews,
            has_phone: state.has_phone,
            has_website: state.has_website,
            columns: selectedCols,
            format: selectedFormat
        };

        try {
            confirmExportBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Generating Export...`;
            const res = await fetch('/api/export', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `clutch_leads_export.${selectedFormat}`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            exportModal.style.display = 'none';
        } catch (err) {
            alert('Export failed: ' + err.message);
        } finally {
            confirmExportBtn.innerHTML = `<i class="fa-solid fa-download"></i> Download Export`;
        }
    });
}

function updateSavedViewsCount() {
    savedViewsCount.textContent = state.savedViews.length;
}

function renderSavedViews() {
    if (!state.savedViews.length) {
        savedViewsList.innerHTML = `<p class="empty-msg">No custom lead views saved yet. Filter agencies and click the Save icon!</p>`;
        return;
    }

    savedViewsList.innerHTML = state.savedViews.map(view => `
        <div class="saved-view-item" style="display:flex; justify-content:space-between; align-items:center; padding:12px; border-bottom:1px solid var(--border-color);">
            <div>
                <strong>${escapeHtml(view.name)}</strong>
                <div style="font-size:12px; color:var(--text-muted);">Country: ${view.state.country || 'All'} | Min Rating: ${view.state.min_rating || 'Any'}</div>
            </div>
            <div>
                <button class="btn btn-secondary btn-sm apply-view-btn" data-id="${view.id}">Apply</button>
                <button class="btn btn-secondary btn-sm delete-view-btn" data-id="${view.id}" style="color:var(--rose);"><i class="fa-solid fa-trash"></i></button>
            </div>
        </div>
    `).join('');

    document.querySelectorAll('.apply-view-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(e.currentTarget.getAttribute('data-id'));
            const saved = state.savedViews.find(v => v.id === id);
            if (saved) {
                Object.assign(state, saved.state);
                searchInput.value = state.search;
                countryFilter.value = state.country;
                priceFilter.value = state.price_range;
                ratingFilter.value = state.min_rating;
                reviewsFilter.value = state.min_reviews;
                phoneOnlyCheck.checked = state.has_phone;
                websiteOnlyCheck.checked = state.has_website;
                savedViewsModal.style.display = 'none';
                fetchCompanies();
            }
        });
    });

    document.querySelectorAll('.delete-view-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(e.currentTarget.getAttribute('data-id'));
            state.savedViews = state.savedViews.filter(v => v.id !== id);
            localStorage.setItem('clutch_saved_views', JSON.stringify(state.savedViews));
            updateSavedViewsCount();
            renderSavedViews();
        });
    });
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
