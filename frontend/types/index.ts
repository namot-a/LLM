// Database Models
export interface Document {
  id: string;
  notion_page_id: string;
  title: string;
  url: string;
  allowed_roles: string[];
  last_edited: string;
  created_at: string;
  updated_at: string;
}

export interface Chunk {
  id: string;
  document_id: string;
  chunk_index: number;
  heading_path: string | null;
  content: string;
  created_at: string;
  document?: Document;
}

export interface QueryLog {
  id: number;
  ts: string;
  telegram_user_id: number | null;
  question: string;
  answer: string;
  prompt_tokens: number | null;
  completion_tokens: number | null;
  model: string | null;
  cost_usd: number | null;
  processing_time_ms: number | null;
}

export interface Feedback {
  id: number;
  ts: string;
  telegram_user_id: number;
  message_id: number | null;
  query_log_id: number | null;
  rating: string;
  comment: string | null;
}

export interface TelegramUser {
  user_id: number;
  username: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface NotionPage {
  id: number;
  page_url: string;
  page_id: string;
  title: string;
  allowed_roles: string[];
  status: string;
  last_synced: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

// API Response Types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

