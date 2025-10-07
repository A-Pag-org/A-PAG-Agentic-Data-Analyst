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

    const form = await req.formData();
    const file = form.get('file');
    const userIdEntry = form.get('user_id');
    const datasetIdEntry = form.get('dataset_id');

    if (!(file instanceof File) || typeof userIdEntry !== 'string' || userIdEntry.length === 0) {
      return NextResponse.json({ error: 'file and user_id are required' }, { status: 400 });
    }

    const forwardForm = new FormData();
    forwardForm.append('file', file);
    forwardForm.append('user_id', userIdEntry);
    if (typeof datasetIdEntry === 'string' && datasetIdEntry.length > 0) {
      forwardForm.append('dataset_id', datasetIdEntry);
    }

    const headers: Record<string, string> = {};
    const authToken = process.env.BACKEND_BEARER_TOKEN || process.env.NEXT_PUBLIC_BACKEND_BEARER_TOKEN;
    if (authToken) headers['authorization'] = `Bearer ${authToken}`;

    const res = await fetch(`${backend}/api/v1/ingest/upload`, {
      method: 'POST',
      headers,
      body: forwardForm,
      cache: 'no-store',
    });

    const contentType = res.headers.get('content-type') || '';
    if (!res.ok) {
      const errPayload = contentType.includes('application/json') ? await res.json() : { error: await res.text() };
      return NextResponse.json({ error: 'Upload failed', detail: errPayload }, { status: res.status });
    }

    const data = contentType.includes('application/json') ? await res.json() : await res.text();
    if (typeof data === 'string') {
      return new NextResponse(data, { status: 200 });
    }
    return NextResponse.json(data);
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
