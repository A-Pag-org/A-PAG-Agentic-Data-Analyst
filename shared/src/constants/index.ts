// Shared constants

export const API_ENDPOINTS = {
  HEALTH: '/health',
  CHAT: '/api/v1/chat',
  DATA_UPLOAD: '/api/v1/data/upload',
  DATA_SOURCES: '/api/v1/data/sources',
  ANALYSIS_FORECAST: '/api/v1/analysis/forecast',
  ANALYSIS_ANALYZE: '/api/v1/analysis/analyze',
  AGENT_TASK: '/api/v1/agent/task',
} as const;

export const FILE_LIMITS = {
  MAX_SIZE: 100 * 1024 * 1024, // 100MB
  ALLOWED_TYPES: ['.csv', '.xlsx', '.xls', '.json', '.pdf'],
} as const;

export const RAG_CONFIG = {
  CHUNK_SIZE: 1024,
  CHUNK_OVERLAP: 200,
  TOP_K: 5,
  SIMILARITY_THRESHOLD: 0.7,
} as const;

export const CHART_COLORS = [
  '#2196f3',
  '#4caf50',
  '#ff9800',
  '#f44336',
  '#9c27b0',
  '#00bcd4',
  '#ffeb3b',
  '#795548',
] as const;

export const DATE_FORMATS = {
  SHORT: 'MMM d, yyyy',
  LONG: 'MMMM d, yyyy HH:mm',
  ISO: "yyyy-MM-dd'T'HH:mm:ss",
} as const;