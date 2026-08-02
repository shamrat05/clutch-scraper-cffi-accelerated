import React from 'react';
import { Layers, Database, Bookmark, FileSpreadsheet } from 'lucide-react';

interface HeaderProps {
  totalCount: number;
  savedViewsCount: number;
  onOpenSavedViews: () => void;
  onOpenExport: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  totalCount,
  savedViewsCount,
  onOpenSavedViews,
  onOpenExport,
}) => {
  return (
    <header className="navbar">
      <div className="nav-brand">
        <div className="logo-icon">
          <Layers size={24} />
        </div>
        <div className="brand-text">
          <h1>Clutch Intelligence Hub</h1>
          <span className="subtitle">High-Speed Lead Gen & Outreach Platform</span>
        </div>
      </div>

      <div className="nav-stats">
        <div className="stat-badge">
          <Database size={15} color="#3b82f6" />
          <span>{totalCount.toLocaleString()} Companies Indexed</span>
        </div>
        <div className="stat-badge">
          <span className="dot"></span> DuckDB C-Engine
        </div>
      </div>

      <div className="nav-actions">
        <button className="btn btn-secondary" onClick={onOpenSavedViews}>
          <Bookmark size={16} /> Saved Views{' '}
          <span className="badge" style={{ background: '#3b82f6', color: '#fff', padding: '2px 7px', borderRadius: '10px', fontSize: '11px' }}>
            {savedViewsCount}
          </span>
        </button>
        <button className="btn btn-primary" onClick={onOpenExport}>
          <FileSpreadsheet size={16} /> Export Leads
        </button>
      </div>
    </header>
  );
};
