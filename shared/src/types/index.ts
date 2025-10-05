// Common types shared between frontend and backend

export interface DataSource {
  id: string;
  name: string;
  type: DataSourceType;
  status: DataSourceStatus;
  created_at: string;
  updated_at?: string;
  row_count?: number;
  column_count?: number;
  file_size?: number;
  metadata?: Record<string, any>;
}

export enum DataSourceType {
  CSV = 'csv',
  EXCEL = 'excel',
  JSON = 'json',
  API = 'api',
  DATABASE = 'database',
}

export enum DataSourceStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  READY = 'ready',
  ERROR = 'error',
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  sources?: Source[];
  metadata?: Record<string, any>;
}

export interface Source {
  id: string;
  content: string;
  score: number;
  metadata: Record<string, any>;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  created_at: string;
  updated_at: string;
}

export interface AnalysisResult {
  id: string;
  type: AnalysisType;
  data_source_id: string;
  results: Record<string, any>;
  visualizations?: Visualization[];
  insights?: string[];
  created_at: string;
}

export enum AnalysisType {
  DESCRIPTIVE = 'descriptive',
  CORRELATION = 'correlation',
  CLUSTERING = 'clustering',
  CLASSIFICATION = 'classification',
  REGRESSION = 'regression',
  TIMESERIES = 'timeseries',
  ANOMALY_DETECTION = 'anomaly_detection',
}

export interface Visualization {
  id: string;
  type: VisualizationType;
  data: any;
  config: Record<string, any>;
}

export enum VisualizationType {
  LINE_CHART = 'line_chart',
  BAR_CHART = 'bar_chart',
  SCATTER_PLOT = 'scatter_plot',
  HEATMAP = 'heatmap',
  PIE_CHART = 'pie_chart',
  MAP = 'map',
  TABLE = 'table',
}

export interface ForecastResult {
  predictions: ForecastPrediction[];
  metrics: ForecastMetrics;
  model_info: Record<string, any>;
}

export interface ForecastPrediction {
  date: string;
  value: number;
  lower_bound?: number;
  upper_bound?: number;
}

export interface ForecastMetrics {
  mae?: number;
  rmse?: number;
  mape?: number;
  r2_score?: number;
}

export interface AgentTask {
  id: string;
  description: string;
  status: AgentTaskStatus;
  steps: AgentStep[];
  result?: any;
  error?: string;
  created_at: string;
  completed_at?: string;
}

export enum AgentTaskStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface AgentStep {
  id: string;
  description: string;
  action: string;
  status: AgentTaskStatus;
  result?: any;
  error?: string;
}