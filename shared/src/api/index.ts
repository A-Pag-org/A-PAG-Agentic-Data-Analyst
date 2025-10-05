// API request/response schemas

import {
  DataSource,
  Message,
  AnalysisResult,
  ForecastResult,
  AgentTask,
} from '../types';

// Chat API
export interface ChatRequest {
  message: string;
  context?: Message[];
  data_source_ids?: string[];
}

export interface ChatResponse {
  response: string;
  sources: Array<{
    content: string;
    score: number;
    metadata: Record<string, any>;
  }>;
  metadata: Record<string, any>;
}

// Data API
export interface UploadResponse {
  data_source_id: string;
  filename: string;
  status: string;
  message: string;
}

export interface DataSourceListResponse {
  data_sources: DataSource[];
  total: number;
}

// Analysis API
export interface ForecastRequest {
  data_source_id: string;
  date_column: string;
  value_column: string;
  periods?: number;
  model?: 'prophet' | 'arima' | 'sarima';
}

export interface AnalysisRequest {
  data_source_id: string;
  analysis_type: string;
  columns?: string[];
  parameters?: Record<string, any>;
}

export interface AnalysisResponse {
  results: Record<string, any>;
  visualizations: Array<{
    type: string;
    data: any;
    config: Record<string, any>;
  }>;
  insights: string[];
}

// Agent API
export interface AgentTaskRequest {
  description: string;
  data_source_ids?: string[];
  parameters?: Record<string, any>;
}

export interface AgentTaskResponse {
  task: AgentTask;
}

// Error Response
export interface ErrorResponse {
  detail: string;
  code?: string;
  timestamp?: string;
}