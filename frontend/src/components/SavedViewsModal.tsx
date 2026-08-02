import React from 'react';
import { X, Bookmark, Trash2 } from 'lucide-react';
import type { SavedView } from '../types';

interface SavedViewsModalProps {
  isOpen: boolean;
  savedViews: SavedView[];
  onClose: () => void;
  onApply: (view: SavedView) => void;
  onDelete: (id: number) => void;
}

export const SavedViewsModal: React.FC<SavedViewsModalProps> = ({
  isOpen,
  savedViews,
  onClose,
  onApply,
  onDelete,
}) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Bookmark size={18} color="#3b82f6" /> Saved Custom Lead Views
          </h3>
          <button className="btn-icon-only btn-secondary" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="modal-body">
          {!savedViews.length ? (
            <p style={{ textAlign: 'center', color: '#94a3b8', padding: '20px' }}>
              No custom lead views saved yet. Filter agencies and click the Save icon to keep views for 1-click access!
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {savedViews.map((v) => (
                <div
                  key={v.id}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '12px',
                    background: '#0b0f19',
                    borderRadius: '8px',
                    border: '1px solid rgba(255,255,255,0.08)',
                  }}
                >
                  <div>
                    <strong style={{ fontSize: '14px' }}>{v.name}</strong>
                    <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                      Country: {v.state.country || 'All'} | Min Rating: {v.state.min_rating || 'Any'}
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button className="btn btn-secondary btn-sm" onClick={() => onApply(v)}>
                      Apply
                    </button>
                    <button
                      className="btn btn-secondary btn-sm"
                      style={{ color: '#f43f5e' }}
                      onClick={() => onDelete(v.id)}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
