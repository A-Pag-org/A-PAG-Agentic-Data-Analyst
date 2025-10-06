import { NextResponse, NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Authentication disabled - allow all requests
  return NextResponse.next();
}

export const config = {
  matcher: [],
};
