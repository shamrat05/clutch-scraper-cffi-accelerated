import React, { useState } from 'react';
import { X, FileSpreadsheet, Download, FileCode, Database, FileText } from 'lucide-react';
import type { FilterState } from '../types';

interface ExportModalProps {
  isOpen: boolean;
  filters: FilterState;
  onClose: () => void;
}

const AVAILABLE_COLUMNS = [
  { key: 'company_name', label: 'Company Name', defaultChecked: true },
  { key: 'official_website', label: 'Official Website', defaultChecked: true },
  { key: 'phone', label: 'Phone Number', defaultChecked: true },
  { key: 'locality', label: 'City / Locality', defaultChecked: true },
  { key: 'country', label: 'Country', defaultChecked: true },
  { key: 'rating', label: 'Overall Rating', defaultChecked: true },
  { key: 'review_count', label: 'Review Count', defaultChecked: true },
  { key: 'price_range', label: 'Hourly Rate Range', defaultChecked: true },
  { key: 'founding_year', label: 'Founding Year', defaultChecked: true },
  { key: 'services_offered', label: 'Services Offered', defaultChecked: true },
  { key: 'street_address', label: 'Street Address', defaultChecked: false },
  { key: 'region', label: 'State / Region', defaultChecked: false },
  { key: 'certifications', label: 'Certifications', defaultChecked: false },
  { key: 'team_leadership', label: 'Team Leadership', defaultChecked: false },
  { key: 'lead_score', label: 'Lead Quality Score', defaultChecked: true },
  { key: 'description', label: 'Company Description', defaultChecked: false },
];

export const ExportModal: React.FC<ExportModalProps> = ({ isOpen, filters, onClose }) => {
  const [format, setFormat] = useState<'csv' | 'json' | 'tsv' | 'jsonl'>('csv');
  const [selectedCols, setSelectedCols] = useState<string[]>(
    AVAILABLE_COLUMNS.filter((c) => c.defaultChecked).map((c) => c.key)
  );
  const [isExporting, setIsExporting] = useState(false);

  if (!isOpen) return null;

  const handleToggleCol = (key: string) => {
    setSelectedCols((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]
    );
  };

  const handleSelectAll = () => setSelectedCols(AVAILABLE_COLUMNS.map((c) => c.key));
  const handleDeselectAll = () => setSelectedCols([]);

  const handleDownload = async () => {
    setIsExporting(true);
    const payload = {
      search: filters.search,
      country: filters.country,
      price_range: filters.price_range,
      min_rating: filters.min_rating,
      min_reviews: filters.min_reviews,
      has_phone: filters.has_phone,
      has_website: filters.has_website,
      columns: selectedCols,
      format,
    };

    try {
      const res = await fetch('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `clutch_leads_export.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      onClose();
    } catch (err) {
      alert('Export failed: ' + (err as Error).message);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal modal-lg">
        <div className="modal-header">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileSpreadsheet size={20} color="#3b82f6" /> Custom Column & Export Manager
          </h3>
          <button className="btn-icon-only btn-secondary" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="modal-body">
          <div style={{ marginBottom: '20px' }}>
            <label style={{ fontSize: '12px', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase' }}>
              Select Export File Format:
            </label>
            <div className="radio-group">
              <label
                className={`radio-card ${format === 'csv' ? 'active' : ''}`}
                onClick={() => setFormat('csv')}
              >
                <FileSpreadsheet size={18} /> CSV File
              </label>

              <label
                className={`radio-card ${format === 'json' ? 'active' : ''}`}
                onClick={() => setFormat('json')}
              >
                <FileCode size={18} /> JSON Array
              </label>

              <label
                className={`radio-card ${format === 'tsv' ? 'active' : ''}`}
                onClick={() => setFormat('tsv')}
              >
                <FileText size={18} /> TSV File
              </label>

              <label
                className={`radio-card ${format === 'jsonl' ? 'active' : ''}`}
                onClick={() => setFormat('jsonl')}
              >
                <Database size={18} /> JSONL / NDJSON
              </label>
            </div>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <label style={{ fontSize: '12px', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase' }}>
                Select Included Columns ({selectedCols.length}/{AVAILABLE_COLUMNS.length}):
              </label>
              <div>
                <button className="btn-text" onClick={handleSelectAll}>
                  Select All
                </button>
                <button className="btn-text" onClick={handleDeselectAll} style={{ marginLeft: '10px' }}>
                  Deselect All
                </button>
              </div>
            </div>

            <div className="columns-grid">
              {AVAILABLE_COLUMNS.map((col) => (
                <label key={col.key} className="checkbox-card">
                  <input
                    type="checkbox"
                    checked={selectedCols.includes(col.key)}
                    onChange={() => handleToggleCol(col.key)}
                  />
                  {col.label}
                </label>
              ))}
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={handleDownload} disabled={isExporting}>
            {isExporting ? 'Generating Download...' : <><Download size={16} /> Download Export</>}
          </button>
        </div>
      </div>
    </div>
  );
};
