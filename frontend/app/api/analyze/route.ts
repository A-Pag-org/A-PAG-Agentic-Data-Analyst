import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const preferredRegion = ['iad1', 'cdg1'];

function getBackendBaseUrl(): string {
  const url = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
  return url.replace(/\/$/, '');
}

export async function POST(req: NextRequest) {
  try {
    const backend = getBackendBaseUrl();
    const body = await req.json();
    const ctx = (body && typeof body === 'object' ? (body.context || {}) : {}) as Record<string, unknown>;
    const payload = {
      user_id: (body.user_id ?? ctx.userId ?? ctx.user_id) as string | undefined,
      query: (body.query ?? '') as string,
      visualize: Boolean(body.visualize ?? ctx.visualize),
      forecast: Boolean(body.forecast ?? ctx.forecast),
      session_id: (body.session_id ?? ctx.sessionId ?? ctx.session_id) as string | undefined,
    };
    if (!payload.user_id || !payload.query) {
      return NextResponse.json({ error: 'user_id and query are required' }, { status: 400 });
    }
    const headers: Record<string, string> = {
      'content-type': 'application/json',
    };
    const authToken =
      process.env.BACKEND_BEARER_TOKEN ||
      process.env.BACKEND_AUTH_BEARER_TOKEN ||
      process.env.NEXT_PUBLIC_BACKEND_BEARER_TOKEN ||
      process.env.AUTH_BEARER_TOKEN ||
      process.env.NEXT_PUBLIC_AUTH_BEARER_TOKEN;
    if (authToken) headers['authorization'] = `Bearer ${authToken}`;

    const res = await fetch(`${backend}/api/v1/agents/analyze`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
      cache: 'no-store',
    });

    const contentType = res.headers.get('content-type') || '';
    if (!res.ok) {
      const errPayload = contentType.includes('application/json') ? await res.json() : { error: await res.text() };
      return NextResponse.json({ error: 'Analyze failed', detail: errPayload }, { status: res.status });
    }
    const data = contentType.includes('application/json') ? await res.json() : await res.text();
    return NextResponse.json(data);
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
