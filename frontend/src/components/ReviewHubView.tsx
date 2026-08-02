import React, { useState, useEffect } from 'react';
import { Search, Star, Globe, Phone, MapPin, User, Building, FileText, Download, ChevronLeft, ChevronRight, Layers, Filter, ExternalLink } from 'lucide-react';
import type { ReviewLead, MetaData } from '../types';

interface ReviewHubViewProps {
  meta: MetaData;
}

const LinkedinIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
    <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/>
  </svg>
);

export const ReviewHubView: React.FC<ReviewHubViewProps> = ({ meta }) => {
  const [search, setSearch] = useState('');
  const [reviewerCompany, setReviewerCompany] = useState('');
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
      reviewer_company: reviewerCompany,
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
      .catch((err) => console.error('Error fetching reviewer leads:', err))
      .finally(() => setIsLoading(false));
  }, [search, reviewerCompany, country, minRating, page, limit]);

  const handleExportReviews = async () => {
    const payload = {
      search,
      reviewer_company: reviewerCompany,
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
      a.download = 'clutch_client_buyer_leads.csv';
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      alert('Export failed: ' + (err as Error).message);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Reviewer Lead Search Panel */}
      <div className="toolbar-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <User size={20} color="#3b82f6" /> Client Buyer Lead Intelligence & Web Search
            </h2>
            <span style={{ fontSize: '12px', color: '#94a3b8' }}>
              Search decision-makers and launch 1-click Google & LinkedIn web searches for instant outreach
            </span>
          </div>
          <button className="btn btn-primary" onClick={handleExportReviews}>
            <Download size={15} /> Export Buyer Leads
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
          <div className="search-box">
            <Search className="search-icon" size={18} />
            <input
              type="text"
              placeholder="Search Reviewer Person Name (e.g. 'Tauhidul Islam') or feedback..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </div>

          <div className="search-box">
            <Building className="search-icon" size={18} color="#10b981" />
            <input
              type="text"
              placeholder="Search Reviewer's Company / Org (e.g. 'University', 'SaaS', 'Retailer')..."
              value={reviewerCompany}
              onChange={(e) => {
                setReviewerCompany(e.target.value);
                setPage(1);
              }}
            />
          </div>
        </div>

        <div className="filters-row">
          <div className="filter-group">
            <label><Globe size={13} /> Vendor Country</label>
            <select value={country} onChange={(e) => { setCountry(e.target.value); setPage(1); }}>
              <option value="">All Countries</option>
              {meta.countries.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label><Star size={13} /> Star Rating</label>
            <select value={minRating} onChange={(e) => { setMinRating(e.target.value); setPage(1); }}>
              <option value="">Any Rating</option>
              <option value="5.0">5.0 ⭐ Only</option>
              <option value="4.5">4.5+ ⭐</option>
              <option value="4.0">4.0+ ⭐</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', paddingTop: '18px' }}>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => {
                setSearch('');
                setReviewerCompany('');
                setCountry('');
                setMinRating('');
                setPage(1);
              }}
            >
              <Filter size={13} /> Clear Search Filters
            </button>
          </div>
        </div>
      </div>

      {/* Results Header */}
      <div className="results-header">
        <div className="results-count">
          Found <strong>{total.toLocaleString()}</strong> verified client decision-maker leads
        </div>
      </div>

      {/* Reviewer Buyer Leads Grid */}
      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#94a3b8' }}>
          Searching client reviewer lead database...
        </div>
      ) : !reviews.length ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#94a3b8' }}>
          No reviewer leads matched your query. Try searching reviewer name like "Tauhidul Islam" or company like "University".
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(460px, 1fr))', gap: '20px' }}>
          {reviews.map((r, idx) => {
            const vendorLoc = [r.vendor_locality, r.vendor_country].filter(Boolean).join(', ') || 'Global';
            const reviewerName = r.reviewer_name || 'Verified Decision-Maker';
            const reviewerCompany = r.reviewer_company || 'Organization Buyer';

            const googleSearchUrl = `https://www.google.com/search?q=${encodeURIComponent(`"${reviewerName}" "${reviewerCompany}"`)}`;
            const linkedinSearchUrl = `https://www.google.com/search?q=${encodeURIComponent(`site:linkedin.com/in/ "${reviewerName}" "${reviewerCompany}"`)}`;

            return (
              <div
                key={idx}
                className="agency-card"
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '16px',
                  padding: '22px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '14px',
                }}
              >
                <div>
                  {/* Header: Reviewer Person Name & Buyer Company */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                    <div>
                      <div style={{ fontSize: '16px', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <User size={18} color="#3b82f6" /> {reviewerName}
                      </div>
                      <div style={{ fontSize: '13px', color: '#10b981', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px', marginTop: '2px' }}>
                        <Building size={14} /> Client Org: {reviewerCompany}
                      </div>
                    </div>
                    {r.review_rating && (
                      <span style={{ color: '#f59e0b', fontWeight: 700, fontSize: '13px', display: 'flex', alignItems: 'center', gap: '4px', background: 'rgba(245,158,11,0.1)', padding: '4px 8px', borderRadius: '6px' }}>
                        <Star size={13} fill="#f59e0b" /> {r.review_rating} ⭐
                      </span>
                    )}
                  </div>

                  {/* 1-Click Live Web Search Action Buttons */}
                  <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
                    <a
                      href={googleSearchUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="btn btn-secondary btn-sm"
                      style={{ fontSize: '11px', padding: '6px 10px', background: 'rgba(59, 130, 246, 0.1)', color: '#3b82f6', border: '1px solid rgba(59, 130, 246, 0.3)', display: 'inline-flex', alignItems: 'center', gap: '5px' }}
                    >
                      <Globe size={12} /> Google Web Search <ExternalLink size={10} />
                    </a>
                    <a
                      href={linkedinSearchUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="btn btn-secondary btn-sm"
                      style={{ fontSize: '11px', padding: '6px 10px', background: 'rgba(10, 102, 194, 0.15)', color: '#0a66c2', border: '1px solid rgba(10, 102, 194, 0.3)', display: 'inline-flex', alignItems: 'center', gap: '5px' }}
                    >
                      <LinkedinIcon /> LinkedIn Search <ExternalLink size={10} />
                    </a>
                  </div>

                  {/* Project Title */}
                  <h4 style={{ fontSize: '14px', fontWeight: 600, color: '#e2e8f0', marginBottom: '8px' }}>
                    <FileText size={13} style={{ display: 'inline', marginRight: '6px', color: '#94a3b8' }} />
                    {r.review_title || 'Client Project Feedback'}
                  </h4>

                  {/* Feedback Quote Body */}
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
                    }}
                  >
                    "{r.review_body}"
                  </div>
                </div>

                {/* Footer: Hired Vendor Agency Details */}
                <div style={{ paddingTop: '12px', borderTop: '1px solid rgba(255, 255, 255, 0.08)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: '11px', textTransform: 'uppercase', color: '#64748b', fontWeight: 600, letterSpacing: '0.04em' }}>
                      Vendor Agency Hired:
                    </div>
                    <div style={{ fontSize: '13px', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '6px', marginTop: '2px' }}>
                      <Layers size={13} color="#3b82f6" /> {r.vendor_agency_name}
                    </div>
                    <div style={{ fontSize: '12px', color: '#64748b', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <MapPin size={11} /> {vendorLoc}
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '8px' }}>
                    {r.vendor_website && (
                      <a href={r.vendor_website} target="_blank" rel="noreferrer" className="btn btn-secondary btn-sm" title="Visit Agency Website">
                        <Globe size={13} />
                      </a>
                    )}
                    {r.vendor_phone && (
                      <a href={`tel:${r.vendor_phone}`} className="btn btn-secondary btn-sm" title="Call Agency Phone">
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
