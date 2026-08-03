export const COUNTRY_NAMES: Record<string, string> = {
  US: 'United States 🇺🇸',
  GB: 'United Kingdom 🇬🇧',
  BD: 'Bangladesh 🇧🇩',
  CA: 'Canada 🇨🇦',
  AU: 'Australia 🇦🇺',
  DE: 'Germany 🇩🇪',
  FR: 'France 🇫🇷',
  IN: 'India 🇮🇳',
  AE: 'United Arab Emirates 🇦🇪',
  SG: 'Singapore 🇸🇬',
  NL: 'Netherlands 🇳🇱',
  ES: 'Spain 🇪🇸',
  IT: 'Italy 🇮🇹',
  BR: 'Brazil 🇧🇷',
  JP: 'Japan 🇯🇵',
  PK: 'Pakistan 🇵🇰',
  PL: 'Poland 🇵🇱',
  UA: 'Ukraine 🇺🇦',
  ZA: 'South Africa 🇿🇦',
  MX: 'Mexico 🇲🇽',
  SE: 'Sweden 🇸🇪',
  CH: 'Switzerland 🇨🇭',
  NZ: 'New Zealand 🇳🇿',
  IE: 'Ireland 🇮🇪',
  DK: 'Denmark 🇩🇰',
  NO: 'Norway 🇳🇴',
  FI: 'Finland 🇫🇮',
  AT: 'Austria 🇦🇹',
  BE: 'Belgium 🇧🇪',
  PT: 'Portugal 🇵🇹',
};

export function getCountryDisplayName(code: string): string {
  if (!code) return 'All Countries';
  return COUNTRY_NAMES[code.toUpperCase()] || `${code}`;
}
