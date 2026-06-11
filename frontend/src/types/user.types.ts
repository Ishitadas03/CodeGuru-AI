export interface Profile {
  id: string;
  user_id: string;
  first_name?: string | null;
  last_name?: string | null;
  avatar_url?: string | null;
  bio?: string | null;
  skills: string[];
}

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  subscription_tier: string;
  stripe_customer_id?: string | null;
  stripe_subscription_id?: string | null;
  profile?: Profile | null;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
