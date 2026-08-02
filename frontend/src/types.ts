export interface Review {
  title: string;
  author: string;
  rating: string | number;
  body: string;
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
  team_leadership: string;
  lead_score: number;
  total_reviews_extracted: number;
  description: string;
  reviews_sample: Review[];
}

export interface FilterState {
  search: string;
  country: string;
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
}
