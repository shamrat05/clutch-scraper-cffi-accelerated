import React, { useState, useEffect, useRef } from 'react';
import { Search } from 'lucide-react';

interface AutocompleteInputProps {
  value: string;
  onChange: (val: string) => void;
  placeholder: string;
  type: 'company' | 'city' | 'reviewer' | 'vendor' | 'buyer_company';
  country?: string;
  icon?: React.ReactNode;
  style?: React.CSSProperties;
}

export const AutocompleteInput: React.FC<AutocompleteInputProps> = ({
  value,
  onChange,
  placeholder,
  type,
  country = '',
  icon,
  style,
}) => {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!value || value.trim().length < 1) {
      setSuggestions([]);
      setIsOpen(false);
      return;
    }

    const timer = setTimeout(() => {
      const params = new URLSearchParams({
        q: value,
        type,
        country,
      });

      fetch(`/api/suggestions?${params.toString()}`)
        .then((res) => res.json())
        .then((data) => {
          if (Array.isArray(data)) {
            setSuggestions(data);
            setIsOpen(data.length > 0);
          }
        })
        .catch(() => {
          setSuggestions([]);
          setIsOpen(false);
        });
    }, 150);

    return () => clearTimeout(timer);
  }, [value, type, country]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (item: string) => {
    onChange(item);
    setIsOpen(false);
  };

  return (
    <div ref={containerRef} style={{ position: 'relative', width: '100%', ...style }}>
      <div className="search-box">
        {icon || <Search className="search-icon" size={18} />}
        <input
          type="text"
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => {
            if (suggestions.length > 0) setIsOpen(true);
          }}
        />
      </div>

      {isOpen && suggestions.length > 0 && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            marginTop: '4px',
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-md)',
            boxShadow: 'var(--shadow-card)',
            zIndex: 999,
            maxHeight: '220px',
            overflowY: 'auto',
          }}
        >
          {suggestions.map((item, idx) => (
            <div
              key={idx}
              onClick={() => handleSelect(item)}
              style={{
                padding: '10px 14px',
                fontSize: '13px',
                color: 'var(--text-main)',
                cursor: 'pointer',
                borderBottom: idx < suggestions.length - 1 ? '1px solid var(--border-color)' : 'none',
                transition: 'background 0.15s ease',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.background = 'var(--bg-card-hover)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.background = 'transparent';
              }}
            >
              {item}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
