export const preferredRegion = ['iad1', 'cdg1'];

// Lazy import to reduce cold start
type Browser = import('puppeteer').Browser;
type PDFOptions = import('puppeteer').PDFOptions;
import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const maxDuration = 60; // seconds

type PdfRequestBody = {
  html?: string;
  url?: string;
  fileName?: string;
  format?: PDFOptions['format'];
  landscape?: boolean;
  emulateMediaType?: 'screen' | 'print';
  margin?: {
    top?: string | number;
    right?: string | number;
    bottom?: string | number;
    left?: string | number;
  };
  waitForSelector?: string;
  timeoutMs?: number;
};

export async function POST(req: NextRequest) {
  let browser: Browser | null = null;
  try {
    const puppeteer = await import('puppeteer');
    const body = (await req.json()) as Partial<PdfRequestBody>;
    const html: string | undefined = body.html;
    const url: string | undefined = body.url;
    const fileName: string = body.fileName ?? 'report.pdf';
    const format: PDFOptions['format'] = body.format ?? 'A4';
    const landscape: boolean = Boolean(body.landscape);
    const emulateMediaType: 'screen' | 'print' = body.emulateMediaType === 'print' ? 'print' : 'screen';
    const margin = body.margin ?? {};
    const waitForSelector: string | undefined = body.waitForSelector;
    const timeoutMs: number = typeof body.timeoutMs === 'number' ? body.timeoutMs : 30000;

    if (!html && !url) {
      return NextResponse.json({ error: 'Provide either html or url' }, { status: 400 });
    }

    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    const page = await browser.newPage();

    if (url) {
      await page.goto(url, { waitUntil: 'networkidle0', timeout: timeoutMs });
    } else if (html) {
      await page.setContent(html, { waitUntil: 'networkidle0', timeout: timeoutMs });
    }

    await page.emulateMediaType(emulateMediaType);

    if (waitForSelector) {
      await page.waitForSelector(waitForSelector, { timeout: timeoutMs });
    }

    const pdfBuffer = await page.pdf({
      format,
      landscape,
      printBackground: true,
      margin: {
        top: margin.top ?? '0.4in',
        right: margin.right ?? '0.4in',
        bottom: margin.bottom ?? '0.4in',
        left: margin.left ?? '0.4in',
      },
    });

    const headers = new Headers({
      'Content-Type': 'application/pdf',
      'Content-Disposition': `attachment; filename="${fileName}"`,
      'Cache-Control': 'no-store',
    });

    const ab = new ArrayBuffer(pdfBuffer.length);
    new Uint8Array(ab).set(pdfBuffer);
    return new NextResponse(ab, { status: 200, headers });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message }, { status: 500 });
  } finally {
    if (browser) {
      try { await browser.close(); } catch { /* ignore */ }
    }
  }
}
