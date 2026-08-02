import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { FilterBar } from './components/FilterBar';
import { CardView } from './components/CardView';
import { TableView } from './components/TableView';
import { SideDrawer } from './components/SideDrawer';
import { SavedViewsModal } from './components/SavedViewsModal';
import { ExportModal } from './components/ExportModal';
import type { Company, FilterState, SavedView, MetaData } from './types';
import { ChevronLeft, ChevronRight, ArrowUpDown } from 'lucide-react';

const INITIAL_FILTERS: FilterState = {
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
  viewMode: 'card',
};

export function App() {
  const [filters, setFilters] = useState<FilterState>(INITIAL_FILTERS);
  const [meta, setMeta] = useState<MetaData>({ total_companies: 0, countries: [], price_ranges: [] });
  const [items, setItems] = useState<Company[]>([]);
  const [totalMatched, setTotalMatched] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [isSavedViewsOpen, setIsSavedViewsOpen] = useState(false);
  const [isExportOpen, setIsExportOpen] = useState(false);

  const [savedViews, setSavedViews] = useState<SavedView[]>(() => {
    try {
      return JSON.parse(localStorage.getItem('clutch_saved_views') || '[]');
    } catch {
      return [];
    }
  });

  // Fetch Meta
  useEffect(() => {
    fetch('/api/meta')
      .then((res) => res.json())
      .then((data) => setMeta(data))
      .catch((err) => console.error('Error fetching meta:', err));
  }, []);

  // Fetch Companies
  useEffect(() => {
    setIsLoading(true);
    const params = new URLSearchParams({
      search: filters.search,
      country: filters.country,
      price_range: filters.price_range,
      min_rating: filters.min_rating,
      min_reviews: filters.min_reviews,
      has_phone: String(filters.has_phone),
      has_website: String(filters.has_website),
      sort_by: filters.sort_by,
      sort_order: filters.sort_order,
      page: String(filters.page),
      limit: String(filters.limit),
    });

    fetch(`/api/companies?${params.toString()}`)
      .then((res) => res.json())
      .then((data) => {
        setItems(data.items || []);
        setTotalMatched(data.total || 0);
        setTotalPages(data.total_pages || 1);
      })
      .catch((err) => console.error('Error fetching companies:', err))
      .finally(() => setIsLoading(false));
  }, [filters]);

  const handleFilterChange = (updated: Partial<FilterState>) => {
    setFilters((prev) => ({ ...prev, ...updated }));
  };

  const handleResetFilters = () => {
    setFilters(INITIAL_FILTERS);
  };

  const handleSaveCurrentView = () => {
    const name = prompt("Enter custom name for this lead filter view (e.g. 'US High Ticket Agencies'):");
    if (name) {
      const newView: SavedView = {
        id: Date.now(),
        name,
        state: { ...filters },
      };
      const updatedViews = [...savedViews, newView];
      setSavedViews(updatedViews);
      localStorage.setItem('clutch_saved_views', JSON.stringify(updatedViews));
    }
  };

  const handleDeleteSavedView = (id: number) => {
    const updated = savedViews.filter((v) => v.id !== id);
    setSavedViews(updated);
    localStorage.setItem('clutch_saved_views', JSON.stringify(updated));
  };

  const handleApplySavedView = (saved: SavedView) => {
    setFilters(saved.state);
    setIsSavedViewsOpen(false);
  };

  const handleToggleSortOrder = () => {
    setFilters((prev) => ({
      ...prev,
      sort_order: prev.sort_order === 'DESC' ? 'ASC' : 'DESC',
    }));
  };

  return (
    <div className="app-container">
      <Header
        totalCount={meta.total_companies}
        savedViewsCount={savedViews.length}
        onOpenSavedViews={() => setIsSavedViewsOpen(true)}
        onOpenExport={() => setIsExportOpen(true)}
      />

      <FilterBar
        filters={filters}
        meta={meta}
        onChange={handleFilterChange}
        onReset={handleResetFilters}
        onSaveView={handleSaveCurrentView}
      />

      <main>
        <div className="results-header">
          <div className="results-count">
            Found <strong>{totalMatched.toLocaleString()}</strong> matching agencies
          </div>

          <div className="sort-controls">
            <span>Sort By:</span>
            <select
              value={filters.sort_by}
              onChange={(e) => handleFilterChange({ sort_by: e.target.value })}
            >
              <option value="lead_score">Lead Quality Score</option>
              <option value="review_count">Review Count</option>
              <option value="rating">Overall Rating</option>
              <option value="company_name">Company Name</option>
            </select>
            <button
              className="btn btn-secondary btn-icon-only"
              onClick={handleToggleSortOrder}
              title="Toggle Sort Direction"
            >
              <ArrowUpDown size={14} />
            </button>
          </div>
        </div>

        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '80px', color: '#94a3b8' }}>
            Loading DuckDB lead dataset...
          </div>
        ) : filters.viewMode === 'card' ? (
          <CardView items={items} onSelect={(comp) => setSelectedCompany(comp)} />
        ) : (
          <TableView items={items} onSelect={(comp) => setSelectedCompany(comp)} />
        )}

        <div className="pagination-bar">
          <button
            className="btn btn-secondary"
            disabled={filters.page <= 1}
            onClick={() => handleFilterChange({ page: filters.page - 1 })}
          >
            <ChevronLeft size={16} /> Previous
          </button>
          <span style={{ fontSize: '14px', color: '#94a3b8' }}>
            Page <strong>{filters.page}</strong> of <strong>{totalPages}</strong>
          </span>
          <button
            className="btn btn-secondary"
            disabled={filters.page >= totalPages}
            onClick={() => handleFilterChange({ page: filters.page + 1 })}
          >
            Next <ChevronRight size={16} />
          </button>
        </div>
      </main>

      <SideDrawer company={selectedCompany} onClose={() => setSelectedCompany(null)} />

      <SavedViewsModal
        isOpen={isSavedViewsOpen}
        savedViews={savedViews}
        onClose={() => setIsSavedViewsOpen(false)}
        onApply={handleApplySavedView}
        onDelete={handleDeleteSavedView}
      />

      <ExportModal isOpen={isExportOpen} filters={filters} onClose={() => setIsExportOpen(false)} />
    </div>
  );
}
