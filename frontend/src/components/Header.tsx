import React from 'react';
import { Layers, Database, Bookmark, FileSpreadsheet, UserCheck, Building2 } from 'lucide-react';

interface HeaderProps {
  totalCount: number;
  savedViewsCount: number;
  activeTab: 'companies' | 'reviews';
  onTabChange: (tab: 'companies' | 'reviews') => void;
  onOpenSavedViews: () => void;
  onOpenExport: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  totalCount,
  savedViewsCount,
  activeTab,
  onTabChange,
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

      <div style={{ display: 'flex', background: 'rgba(11, 15, 25, 0.7)', padding: '4px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
        <button
          className={`toggle-btn ${activeTab === 'companies' ? 'active' : ''}`}
          onClick={() => onTabChange('companies')}
          style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 16px', fontSize: '13px', fontWeight: 600 }}
        >
          <Building2 size={15} /> Agencies Directory
        </button>
        <button
          className={`toggle-btn ${activeTab === 'reviews' ? 'active' : ''}`}
          onClick={() => onTabChange('reviews')}
          style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 16px', fontSize: '13px', fontWeight: 600 }}
        >
          <UserCheck size={15} /> Reviewer Leads Engine
        </button>
      </div>

      <div className="nav-stats">
        <div className="stat-badge">
          <Database size={15} color="#3b82f6" />
          <span>{totalCount.toLocaleString()} Companies</span>
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
