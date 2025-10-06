import { NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

function getBackendBaseUrl(): string {
  const url = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
  return url.replace(/\/$/, '');
}

export async function GET() {
  try {
    const backend = getBackendBaseUrl();
    const headers: Record<string, string> = {};
    const authToken = process.env.BACKEND_BEARER_TOKEN || process.env.NEXT_PUBLIC_BACKEND_BEARER_TOKEN;
    if (authToken) headers['authorization'] = `Bearer ${authToken}`;

    const res = await fetch(`${backend}/api/v1/health`, { headers, cache: 'no-store' });
    const contentType = res.headers.get('content-type') || '';
    const data = contentType.includes('application/json') ? await res.json() : await res.text();
    return NextResponse.json(data, { status: res.status });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ status: 'error', error: message }, { status: 500 });
  }
}
