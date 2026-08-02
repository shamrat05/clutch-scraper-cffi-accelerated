import React, { useState, useEffect } from 'react';
import { Search, Star, Globe, Phone, MapPin, User, FileText, Download, ChevronLeft, ChevronRight, Layers } from 'lucide-react';
import type { ReviewLead, MetaData } from '../types';

interface ReviewHubViewProps {
  meta: MetaData;
}

export const ReviewHubView: React.FC<ReviewHubViewProps> = ({ meta }) => {
  const [search, setSearch] = useState('');
  const [country, setCountry] = useState('');
  const [minRating, setMinRating] = useState('');
  const [page, setPage] = useState(1);
  const [limit] = useState(12);

  const [reviews, setReviews] = useState<ReviewLead[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setIsLoading(true);
    const params = new URLSearchParams({
      search,
      country,
      min_rating: minRating,
      page: String(page),
      limit: String(limit),
    });

    fetch(`/api/reviews?${params.toString()}`)
      .then((res) => res.json())
      .then((data) => {
        setReviews(data.items || []);
        setTotal(data.total || 0);
        setTotalPages(data.total_pages || 1);
      })
      .catch((err) => console.error('Error fetching reviews:', err))
      .finally(() => setIsLoading(false));
  }, [search, country, minRating, page, limit]);

  const handleExportReviews = async () => {
    const payload = {
      search,
      country,
      min_rating: minRating,
      format: 'csv',
    };

    try {
      const res = await fetch('/api/export_reviews', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'clutch_reviewer_leads.csv';
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      alert('Export failed: ' + (err as Error).message);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Review Search Header */}
      <div className="toolbar-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <User size={20} color="#3b82f6" /> Google & LinkedIn Style Reviewer Lead Search
            </h2>
            <span style={{ fontSize: '12px', color: '#94a3b8' }}>
              Search decision-makers and client reviewers by name, project scope, agency, or feedback
            </span>
          </div>
          <button className="btn btn-primary" onClick={handleExportReviews}>
            <Download size={15} /> Export Reviewer Leads
          </button>
        </div>

        <div className="search-box">
          <Search className="search-icon" size={18} />
          <input
            type="text"
            placeholder="Search reviewer name (e.g. 'Tauhidul Islam'), project title, agency, or review text..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </div>

        <div className="filters-row">
          <div className="filter-group">
            <label><Globe size={13} /> Country</label>
            <select value={country} onChange={(e) => { setCountry(e.target.value); setPage(1); }}>
              <option value="">All Countries</option>
              {meta.countries.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label><Star size={13} /> Rating</label>
            <select value={minRating} onChange={(e) => { setMinRating(e.target.value); setPage(1); }}>
              <option value="">Any Rating</option>
              <option value="5.0">5.0 ⭐ Only</option>
              <option value="4.5">4.5+ ⭐</option>
              <option value="4.0">4.0+ ⭐</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results Subheader */}
      <div className="results-header">
        <div className="results-count">
          Found <strong>{total.toLocaleString()}</strong> verified client feedback reviews
        </div>
      </div>

      {/* Reviews Cards List */}
      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#94a3b8' }}>
          Searching client reviewer database...
        </div>
      ) : !reviews.length ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#94a3b8' }}>
          No client reviews matched your query. Try searching by reviewer name like "Tauhidul Islam" or "University".
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(450px, 1fr))', gap: '20px' }}>
          {reviews.map((r, idx) => {
            const location = [r.locality, r.country].filter(Boolean).join(', ') || 'Global';
            return (
              <div
                key={idx}
                className="agency-card"
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '16px',
                  padding: '20px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '12px',
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                    <div style={{ fontSize: '11px', textTransform: 'uppercase', color: '#3b82f6', fontWeight: 600, letterSpacing: '0.05em' }}>
                      <FileText size={12} style={{ display: 'inline', marginRight: '4px' }} /> Extracted Client Feedback
                    </div>
                    {r.review_rating && (
                      <span style={{ color: '#f59e0b', fontWeight: 700, fontSize: '13px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Star size={13} fill="#f59e0b" /> {r.review_rating} ⭐
                      </span>
                    )}
                  </div>

                  <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#f8fafc', marginBottom: '8px' }}>
                    {r.review_title || 'Client Project Feedback'}
                  </h3>

                  <div
                    style={{
                      background: 'rgba(11, 15, 25, 0.7)',
                      border: '1px solid rgba(255, 255, 255, 0.06)',
                      borderRadius: '10px',
                      padding: '12px 14px',
                      fontSize: '13px',
                      color: '#94a3b8',
                      fontStyle: 'italic',
                      lineHeight: '1.5',
                      marginBottom: '12px',
                    }}
                  >
                    "{r.review_body}"
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', fontWeight: 600, color: '#10b981' }}>
                    <User size={14} /> By: {r.reviewer_name || 'Verified Client Decision-Maker'}
                  </div>
                </div>

                <div style={{ paddingTop: '12px', borderTop: '1px solid rgba(255, 255, 255, 0.08)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Layers size={13} color="#3b82f6" /> {r.company_name}
                    </div>
                    <div style={{ fontSize: '12px', color: '#64748b', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <MapPin size={11} /> {location}
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '8px' }}>
                    {r.official_website && (
                      <a href={r.official_website} target="_blank" rel="noreferrer" className="btn btn-secondary btn-sm" title="Visit Agency Website">
                        <Globe size={13} />
                      </a>
                    )}
                    {r.phone && (
                      <a href={`tel:${r.phone}`} className="btn btn-secondary btn-sm" title="Call Agency Phone">
                        <Phone size={13} />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Pagination Bar */}
      <div className="pagination-bar">
        <button className="btn btn-secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>
          <ChevronLeft size={16} /> Previous
        </button>
        <span style={{ fontSize: '14px', color: '#94a3b8' }}>
          Page <strong>{page}</strong> of <strong>{totalPages}</strong>
        </span>
        <button className="btn btn-secondary" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
          Next <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
};
