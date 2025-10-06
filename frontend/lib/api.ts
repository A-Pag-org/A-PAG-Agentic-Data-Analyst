export type SourceNode = {
  score?: number | null;
  text?: string | null;
  metadata?: Record<string, any>;
};

export type AgentAnalyzeResponse = {
  answer: string;
  explanation?: string | null;
  sources: SourceNode[];
  visualization_spec?: Record<string, any> | null;
  forecast?: string | null;
  session_id?: string | null;
};

function getBackendBaseUrl(): string {
  // Try env first; otherwise assume same origin with /api/v1
  if (typeof process !== 'undefined') {
    const envUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
    if (envUrl) return envUrl.replace(/\/$/, '') + '/api/v1';
  }
  if (typeof window !== 'undefined') {
    return `${window.location.origin}/api/v1`;
  }
  // Fallback
  return '/api/v1';
}

export async function analyzeQuery(params: {
  userId: string;
  query: string;
  visualize?: boolean;
  forecast?: boolean;
  sessionId?: string | null;
}): Promise<AgentAnalyzeResponse> {
  const base = getBackendBaseUrl();
  const res = await fetch(`${base}/agents/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: params.userId,
      query: params.query,
      visualize: Boolean(params.visualize),
      forecast: Boolean(params.forecast),
      session_id: params.sessionId ?? null,
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return (await res.json()) as AgentAnalyzeResponse;
}

export async function searchQuery(params: {
  userId: string;
  q: string;
}): Promise<{ answer: string; source_nodes: SourceNode[] }>{
  const base = getBackendBaseUrl();
  const url = new URL(`${base}/search/query`);
  url.searchParams.set('user_id', params.userId);
  url.searchParams.set('q', params.q);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Search failed: ${res.status}`);
  return res.json();
}
