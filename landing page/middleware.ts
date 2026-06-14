import { NextRequest, NextResponse } from 'next/server'
import { verifyToken } from '@/lib/auth'

const MAIN_APP_URL = process.env.MAIN_APP_URL ?? 'http://localhost:3000'
const COOKIE_NAME  = 'officenator_token'

// Routes that need authentication
const PROTECTED = ['/dashboard']
// Routes only for guests (redirect to app if already logged in)
const GUEST_ONLY = ['/login', '/register']

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl
  const token = req.cookies.get(COOKIE_NAME)?.value
  const user  = token ? verifyToken(token) : null

  // Already logged in + hitting /login or /register → send to main app
  if (user && GUEST_ONLY.some(p => pathname.startsWith(p))) {
    return NextResponse.redirect(MAIN_APP_URL)
  }

  // Not logged in + hitting protected route → send to login
  if (!user && PROTECTED.some(p => pathname.startsWith(p))) {
    return NextResponse.redirect(new URL('/login', req.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/login', '/register', '/dashboard/:path*'],
}
