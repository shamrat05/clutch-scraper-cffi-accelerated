export interface Review {
  title: string;
  author: string;
  rating: string | number;
  body: string;
}

export interface ReviewLead {
  reviewer_name: string;
  reviewer_company: string;
  review_title: string;
  review_date?: string;
  review_rating: number | null;
  review_body: string;
  vendor_agency_name: string;
  vendor_profile_url: string;
  vendor_website: string;
  vendor_phone: string;
  vendor_locality: string;
  vendor_country: string;
}

export interface Company {
  company_name: string;
  profile_url: string;
  official_website: string;
  phone: string;
  founding_year: string;
  price_range: string;
  rating: number | null;
  review_count: number | null;
  street_address: string;
  locality: string;
  region: string;
  postcode: string;
  country: string;
  services_offered: string;
  certifications: string;
  cert_count?: number;
  team_leadership: string;
  lead_score: number;
  total_reviews_extracted: number;
  description: string;
  reviews_sample: Review[];
}

export interface FilterState {
  search: string;
  country: string;
  city: string;
  price_range: string;
  min_rating: string;
  min_reviews: string;
  has_phone: boolean;
  has_website: boolean;
  sort_by: string;
  sort_order: 'ASC' | 'DESC';
  page: number;
  limit: number;
  viewMode: 'card' | 'list';
  activeTab: 'companies' | 'reviews';
}

export interface SavedView {
  id: number;
  name: string;
  state: FilterState;
}

export interface MetaData {
  total_companies: number;
  countries: string[];
  price_ranges: string[];
  cities?: string[];
}
