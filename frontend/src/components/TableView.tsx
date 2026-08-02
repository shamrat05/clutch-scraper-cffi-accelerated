import React from 'react';
import { Globe, Phone, ExternalLink } from 'lucide-react';
import type { Company } from '../types';

interface TableViewProps {
  items: Company[];
  onSelect: (company: Company) => void;
}

export const TableView: React.FC<TableViewProps> = ({ items, onSelect }) => {
  if (!items.length) {
    return (
      <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
        No agencies found.
      </div>
    );
  }

  return (
    <div className="table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Company Name</th>
            <th>Location</th>
            <th>Rating</th>
            <th>Reviews</th>
            <th>Rate Range</th>
            <th>Lead Score</th>
            <th>Links</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, idx) => {
            const location = [item.locality, item.country].filter(Boolean).join(', ') || '-';
            return (
              <tr key={item.profile_url || idx}>
                <td>
                  <strong>{item.company_name}</strong>
                </td>
                <td>{location}</td>
                <td>
                  <span style={{ color: '#f59e0b', fontWeight: 600 }}>
                    {item.rating ? `${item.rating} ⭐` : '-'}
                  </span>
                </td>
                <td>{item.review_count || 0}</td>
                <td>{item.price_range || '-'}</td>
                <td>
                  <span className="lead-score-pill">Score: {item.lead_score}</span>
                </td>
                <td>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    {item.official_website && (
                      <a href={item.official_website} target="_blank" rel="noreferrer" title="Website">
                        <Globe size={15} color="#94a3b8" />
                      </a>
                    )}
                    {item.phone && (
                      <a href={`tel:${item.phone}`} title="Call Phone">
                        <Phone size={15} color="#94a3b8" />
                      </a>
                    )}
                  </div>
                </td>
                <td>
                  <button className="btn btn-secondary btn-sm" onClick={() => onSelect(item)}>
                    Inspect <ExternalLink size={13} />
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
