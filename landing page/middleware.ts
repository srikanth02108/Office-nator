import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// No auth logic — pass all requests through
export function middleware(request: NextRequest) {
  return NextResponse.next()
}

export const config = {
  matcher: [],  // empty — no routes intercepted
}
