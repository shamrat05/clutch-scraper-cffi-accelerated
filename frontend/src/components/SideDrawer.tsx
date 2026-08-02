import React from 'react';
import { X, Globe, Phone, MapPin, Building2, Tag, Calendar, Star, Users, Award, FileText, MessageCircle } from 'lucide-react';
import type { Company } from '../types';

interface SideDrawerProps {
  company: Company | null;
  onClose: () => void;
}

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
            <h2 style={{ fontSize: '20px', fontWeight: 700 }}>{company.company_name}</h2>
            <div style={{ display: 'flex', gap: '8px', marginTop: '6px' }}>
              <span className="lead-score-pill">Score: {company.lead_score}/100</span>
              <span style={{ fontSize: '13px', color: '#f59e0b', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Star size={13} fill="#f59e0b" />
                {company.rating ? `${company.rating} (${company.review_count || 0} Reviews)` : 'No Reviews'}
              </span>
            </div>
          </div>
          <button className="btn-icon-only btn-secondary" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="drawer-body">
          <div className="detail-section">
            <h4><Building2 size={13} /> Contact & Location</h4>
            <div className="detail-grid">
              <div className="detail-card">
                <div className="label">Official Website</div>
                <div className="value">
                  {company.official_website ? (
                    <a href={company.official_website} target="_blank" rel="noreferrer" style={{ color: '#3b82f6', textDecoration: 'none' }}>
                      <Globe size={13} /> {company.official_website}
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
                    <a href={`tel:${company.phone}`} style={{ color: '#3b82f6', textDecoration: 'none' }}>
                      <Phone size={13} /> {company.phone}
                    </a>
                  ) : (
                    'Not Listed'
                  )}
                </div>
              </div>

              <div className="detail-card" style={{ gridColumn: 'span 2' }}>
                <div className="label">Headquarters Address</div>
                <div className="value">
                  <MapPin size={13} color="#94a3b8" /> {location || 'Not Listed'}
                </div>
              </div>
            </div>
          </div>

          <div className="detail-section">
            <h4><Tag size={13} /> Firmographics & Pricing</h4>
            <div className="detail-grid">
              <div className="detail-card">
                <div className="label">Founding Year</div>
                <div className="value">
                  <Calendar size={13} /> {company.founding_year || 'Unknown'}
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
              <h4><Award size={13} /> Certifications</h4>
              <div style={{ fontSize: '13px', color: '#94a3b8' }}>{company.certifications}</div>
            </div>
          )}

          {company.team_leadership && (
            <div className="detail-section">
              <h4><Users size={13} /> Key Leadership</h4>
              <div style={{ fontSize: '13px', color: '#94a3b8' }}>{company.team_leadership}</div>
            </div>
          )}

          {company.description && (
            <div className="detail-section">
              <h4><FileText size={13} /> Company Overview</h4>
              <p style={{ fontSize: '13px', color: '#94a3b8', lineHeight: 1.6 }}>{company.description}</p>
            </div>
          )}

          {reviews.length > 0 && (
            <div className="detail-section">
              <h4><MessageCircle size={13} /> Extracted Client Feedback ({reviews.length})</h4>
              {reviews.map((r, idx) => (
                <div key={idx} className="review-item">
                  <div className="title">
                    <span>{r.title || 'Client Review'}</span>
                    <span style={{ color: '#f59e0b' }}>{r.rating ? `${r.rating} ⭐` : ''}</span>
                  </div>
                  <div className="body">"{r.body}"</div>
                  <div style={{ fontSize: '11px', color: '#64748b', marginTop: '4px' }}>
                    By: {r.author || 'Verified Client'}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </aside>
    </>
  );
};
