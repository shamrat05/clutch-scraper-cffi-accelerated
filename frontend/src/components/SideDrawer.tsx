import React from 'react';
import { X, Globe, Phone, MapPin, Building2, Tag, Calendar, Star, Users, Award, FileText, MessageCircle, ExternalLink, User } from 'lucide-react';
import type { Company } from '../types';

interface SideDrawerProps {
  company: Company | null;
  onClose: () => void;
}

const LinkedinIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
    <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/>
  </svg>
);

export const SideDrawer: React.FC<SideDrawerProps> = ({ company, onClose }) => {
  if (!company) return null;

  const location = [company.street_address, company.locality, company.region, company.country]
    .filter(Boolean)
    .join(', ');

  const reviews = company.reviews_sample || [];

  return (
    <>
      <div className="drawer-overlay" onClick={onClose} />
      <aside className="drawer open">
        <div className="drawer-header">
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-main)' }}>{company.company_name}</h2>
            <div style={{ display: 'flex', gap: '8px', marginTop: '6px' }}>
              <span className="lead-score-pill">Score: {company.lead_score}/100</span>
              <span style={{ fontSize: '12px', color: 'var(--amber-text)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Star size={12} fill="var(--amber-text)" />
                {company.rating ? `${company.rating} (${company.review_count || 0} Reviews)` : 'No Reviews'}
              </span>
            </div>
          </div>
          <button className="btn-icon-only btn-secondary" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="drawer-body">
          <div className="detail-section">
            <h4><Building2 size={12} /> Contact & Location</h4>
            <div className="detail-grid">
              <div className="detail-card">
                <div className="label">Official Website</div>
                <div className="value">
                  {company.official_website ? (
                    <a href={company.official_website} target="_blank" rel="noreferrer" style={{ color: '#6366f1', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                      <Globe size={12} /> {company.official_website}
                    </a>
                  ) : (
                    'Not Listed'
                  )}
                </div>
              </div>

              <div className="detail-card">
                <div className="label">Direct Phone</div>
                <div className="value">
                  {company.phone ? (
                    <a href={`tel:${company.phone}`} style={{ color: '#6366f1', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                      <Phone size={12} /> {company.phone}
                    </a>
                  ) : (
                    'Not Listed'
                  )}
                </div>
              </div>

              <div className="detail-card" style={{ gridColumn: 'span 2' }}>
                <div className="label">Headquarters Address</div>
                <div className="value">
                  <MapPin size={12} color="var(--text-dim)" /> {location || 'Not Listed'}
                </div>
              </div>
            </div>
          </div>

          <div className="detail-section">
            <h4><Tag size={12} /> Firmographics & Pricing</h4>
            <div className="detail-grid">
              <div className="detail-card">
                <div className="label">Founding Year</div>
                <div className="value">
                  <Calendar size={12} /> {company.founding_year || 'Unknown'}
                </div>
              </div>
              <div className="detail-card">
                <div className="label">Hourly Rate Range</div>
                <div className="value">{company.price_range || 'Undisclosed'}</div>
              </div>
            </div>
          </div>

          {company.services_offered && (
            <div className="detail-section">
              <h4>Services Offered Catalog</h4>
              <div className="card-services">
                {company.services_offered.split(',').map((s, i) => (
                  <span key={i} className="service-tag">
                    {s.trim()}
                  </span>
                ))}
              </div>
            </div>
          )}

          {company.certifications && (
            <div className="detail-section">
              <h4><Award size={12} /> Certifications</h4>
              <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{company.certifications}</div>
            </div>
          )}

          {company.team_leadership && (
            <div className="detail-section">
              <h4><Users size={12} /> Key Leadership</h4>
              <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{company.team_leadership}</div>
            </div>
          )}

          {company.description && (
            <div className="detail-section">
              <h4><FileText size={12} /> Company Overview</h4>
              <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.6 }}>{company.description}</p>
            </div>
          )}

          {reviews.length > 0 && (
            <div className="detail-section">
              <h4><MessageCircle size={12} /> Extracted Client Feedback ({reviews.length})</h4>
              {reviews.map((r, idx) => {
                const reviewerName = r.author || 'Verified Decision-Maker';
                const googleSearchUrl = `https://www.google.com/search?q=${encodeURIComponent(`"${reviewerName}" "${company.company_name}"`)}`;
                const linkedinSearchUrl = `https://www.google.com/search?q=${encodeURIComponent(`site:linkedin.com/in/ "${reviewerName}" "${company.company_name}"`)}`;

                return (
                  <div key={idx} className="review-item" style={{ background: '#14161b', padding: '16px', borderRadius: '12px', marginBottom: '12px', border: '1px solid var(--border-color)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontWeight: 600, fontSize: '13px', color: '#f1f5f9' }}>{r.title || 'Client Project Feedback'}</span>
                      {r.rating && (
                        <span style={{ color: 'var(--amber-text)', fontWeight: 600, fontSize: '12px', display: 'flex', alignItems: 'center', gap: '3px' }}>
                          <Star size={12} fill="var(--amber-text)" /> {r.rating} ⭐
                        </span>
                      )}
                    </div>

                    <div style={{ fontSize: '13px', color: 'var(--text-muted)', fontStyle: 'italic', marginBottom: '12px', lineHeight: '1.5' }}>"{r.body}"</div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '10px', borderTop: '1px solid var(--border-color)' }}>
                      <div style={{ fontSize: '12px', color: 'var(--emerald-text)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <User size={13} /> By: {reviewerName}
                      </div>

                      <div style={{ display: 'flex', gap: '8px' }}>
                        <a
                          href={googleSearchUrl}
                          target="_blank"
                          rel="noreferrer"
                          className="btn btn-secondary btn-sm"
                          style={{ fontSize: '11px', padding: '5px 10px', background: 'var(--accent-soft)', color: '#818cf8', border: '1px solid rgba(99, 102, 241, 0.3)', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                          title="Search Reviewer on Google"
                        >
                          <Globe size={12} /> Google Web Search <ExternalLink size={10} />
                        </a>
                        <a
                          href={linkedinSearchUrl}
                          target="_blank"
                          rel="noreferrer"
                          className="btn btn-secondary btn-sm"
                          style={{ fontSize: '11px', padding: '5px 10px', background: 'rgba(10, 102, 194, 0.2)', color: '#38bdf8', border: '1px solid rgba(10, 102, 194, 0.4)', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                          title="Search Reviewer on LinkedIn"
                        >
                          <LinkedinIcon /> LinkedIn Search <ExternalLink size={10} />
                        </a>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </aside>
    </>
  );
};
