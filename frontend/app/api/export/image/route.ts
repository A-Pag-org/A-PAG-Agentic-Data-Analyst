import puppeteer from 'puppeteer';
import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const maxDuration = 60; // seconds

export async function POST(req: NextRequest) {
  let browser: puppeteer.Browser | null = null;
  try {
    const body = await req.json();
    const html: string | undefined = body?.html;
    const url: string | undefined = body?.url;
    const fileName: string = body?.fileName || 'chart.png';
    const type: 'png' | 'jpeg' | 'webp' = ['png','jpeg','webp'].includes(body?.type) ? body.type : 'png';
    const width: number | undefined = body?.width;
    const height: number | undefined = body?.height;
    const deviceScaleFactor: number = typeof body?.deviceScaleFactor === 'number' ? body.deviceScaleFactor : 2;
    const fullPage: boolean = Boolean(body?.fullPage);
    const waitForSelector: string | undefined = body?.waitForSelector;
    const timeoutMs: number = typeof body?.timeoutMs === 'number' ? body.timeoutMs : 30000;
    const clip: { x: number; y: number; width: number; height: number } | undefined = body?.clip;

    if (!html && !url) {
      return NextResponse.json({ error: 'Provide either html or url' }, { status: 400 });
    }

    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    const page = await browser.newPage();

    if (width || height || deviceScaleFactor) {
      await page.setViewport({
        width: Math.max(1, Math.floor(width || 1280)),
        height: Math.max(1, Math.floor(height || 720)),
        deviceScaleFactor,
      });
    }

    if (url) {
      await page.goto(url, { waitUntil: 'networkidle0', timeout: timeoutMs });
    } else if (html) {
      await page.setContent(html, { waitUntil: 'networkidle0', timeout: timeoutMs });
    }

    if (waitForSelector) {
      await page.waitForSelector(waitForSelector, { timeout: timeoutMs });
    }

    const buffer = await page.screenshot({
      type,
      fullPage,
      clip: clip ? { ...clip } : undefined,
      captureBeyondViewport: true,
      omitBackground: false,
    });

    const contentType = type === 'png' ? 'image/png' : type === 'jpeg' ? 'image/jpeg' : 'image/webp';
    const headers = new Headers({
      'Content-Type': contentType,
      'Content-Disposition': `attachment; filename="${fileName}"`,
      'Cache-Control': 'no-store',
    });

    return new NextResponse(buffer, { status: 200, headers });
  } catch (err: any) {
    return NextResponse.json({ error: String(err?.message || err) }, { status: 500 });
  } finally {
    if (browser) {
      try { await browser.close(); } catch { /* ignore */ }
    }
  }
}
