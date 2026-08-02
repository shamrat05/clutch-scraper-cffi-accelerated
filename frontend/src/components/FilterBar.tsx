import React from 'react';
import { Search, Globe, Tag, Star, MessageSquare, Save, LayoutGrid, List, Trash2 } from 'lucide-react';
import type { FilterState, MetaData } from '../types';

interface FilterBarProps {
  filters: FilterState;
  meta: MetaData;
  onChange: (updated: Partial<FilterState>) => void;
  onReset: () => void;
  onSaveView: () => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  meta,
  onChange,
  onReset,
  onSaveView,
}) => {
  return (
    <section className="toolbar-section">
      <div className="search-box">
        <Search className="search-icon" size={18} />
        <input
          type="text"
          placeholder="Search agency name, city, or services (e.g. SEO, London, Web Dev)..."
          value={filters.search}
          onChange={(e) => onChange({ search: e.target.value, page: 1 })}
        />
      </div>

      <div className="filters-row">
        <div className="filter-group">
          <label><Globe size={13} /> Country</label>
          <select
            value={filters.country}
            onChange={(e) => onChange({ country: e.target.value, page: 1 })}
          >
            <option value="">All Countries</option>
            {meta.countries.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label><Tag size={13} /> Rate Range</label>
          <select
            value={filters.price_range}
            onChange={(e) => onChange({ price_range: e.target.value, page: 1 })}
          >
            <option value="">All Rates</option>
            {meta.price_ranges.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label><Star size={13} /> Min Rating</label>
          <select
            value={filters.min_rating}
            onChange={(e) => onChange({ min_rating: e.target.value, page: 1 })}
          >
            <option value="">Any Rating</option>
            <option value="4.8">4.8+ Stars ⭐</option>
            <option value="4.5">4.5+ Stars ⭐</option>
            <option value="4.0">4.0+ Stars ⭐</option>
          </select>
        </div>

        <div className="filter-group">
          <label><MessageSquare size={13} /> Min Reviews</label>
          <select
            value={filters.min_reviews}
            onChange={(e) => onChange({ min_reviews: e.target.value, page: 1 })}
          >
            <option value="">Any Reviews</option>
            <option value="50">50+ Reviews</option>
            <option value="20">20+ Reviews</option>
            <option value="10">10+ Reviews</option>
            <option value="1">1+ Review</option>
          </select>
        </div>

        <div className="filter-group" style={{ flexDirection: 'row', gap: '16px', alignItems: 'center' }}>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={filters.has_phone}
              onChange={(e) => onChange({ has_phone: e.target.checked, page: 1 })}
            />
            Has Phone
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={filters.has_website}
              onChange={(e) => onChange({ has_website: e.target.checked, page: 1 })}
            />
            Has Website
          </label>
        </div>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            className="btn btn-danger"
            onClick={onReset}
            title="Clear All Filters & Search Inputs"
            style={{ fontWeight: 600, fontSize: '13px' }}
          >
            <Trash2 size={15} /> Clear All
          </button>

          <button className="btn btn-secondary btn-icon-only" onClick={onSaveView} title="Save Current Custom View">
            <Save size={16} />
          </button>

          <div className="view-toggle">
            <button
              className={`toggle-btn ${filters.viewMode === 'card' ? 'active' : ''}`}
              onClick={() => onChange({ viewMode: 'card' })}
              title="Grid Card View"
            >
              <LayoutGrid size={16} />
            </button>
            <button
              className={`toggle-btn ${filters.viewMode === 'list' ? 'active' : ''}`}
              onClick={() => onChange({ viewMode: 'list' })}
              title="List Table View"
            >
              <List size={16} />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};
