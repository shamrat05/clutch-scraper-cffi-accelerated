import React from 'react';
import { MapPin, Star, Tag, Calendar, Globe, Phone, ArrowRight } from 'lucide-react';
import type { Company } from '../types';

interface CardViewProps {
  items: Company[];
  onSelect: (company: Company) => void;
}

export const CardView: React.FC<CardViewProps> = ({ items, onSelect }) => {
  if (!items.length) {
    return (
      <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-muted)' }}>
        No agencies matched your search and filter criteria. Try adjusting filters.
      </div>
    );
  }

  return (
    <div className="cards-grid">
      {items.map((item, idx) => {
        const location = [item.locality, item.country].filter(Boolean).join(', ') || 'Global';
        const services = (item.services_offered || '').split(',').slice(0, 3).filter(Boolean);

        return (
          <div key={item.profile_url || idx} className="agency-card">
            <div>
              <div className="card-header">
                <div className="card-title-group">
                  <h3>{item.company_name}</h3>
                  <div className="card-location">
                    <MapPin size={13} color="#94a3b8" /> {location}
                  </div>
                </div>
                <span className="lead-score-pill" title="Lead Quality Score">
                  Score: {item.lead_score}
                </span>
              </div>

              <div className="card-metrics">
                <div className="metric-item rating">
                  <Star size={13} fill="#f59e0b" color="#f59e0b" />
                  {item.rating ? `${item.rating} (${item.review_count || 0})` : 'Unrated'}
                </div>
                {item.price_range && (
                  <div className="metric-item">
                    <Tag size={13} /> {item.price_range}
                  </div>
                )}
                {item.founding_year && (
                  <div className="metric-item">
                    <Calendar size={13} /> {item.founding_year}
                  </div>
                )}
              </div>

              <div className="card-services">
                {services.map((s, i) => (
                  <span key={i} className="service-tag">
                    {s.trim()}
                  </span>
                ))}
              </div>
            </div>

            <div className="card-footer">
              <div className="card-actions">
                {item.official_website && (
                  <a href={item.official_website} target="_blank" rel="noreferrer" title="Visit Website">
                    <Globe size={16} />
                  </a>
                )}
                {item.phone && (
                  <a href={`tel:${item.phone}`} title="Call Phone">
                    <Phone size={16} />
                  </a>
                )}
              </div>

              <button className="btn btn-secondary btn-sm" onClick={() => onSelect(item)}>
                Inspect <ArrowRight size={14} />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
};
