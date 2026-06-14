import { NextRequest, NextResponse } from 'next/server'
import jwt from 'jsonwebtoken'

// The main app reads the same JWT cookie the landing page set.
// This endpoint validates it and returns the user identity.

const JWT_SECRET = process.env.JWT_SECRET ?? ''
const COOKIE_NAME = 'officenator_token'

export async function GET(req: NextRequest) {
  if (!JWT_SECRET) {
    // If no JWT_SECRET configured, allow access (dev mode without auth)
    return NextResponse.json({ authenticated: false, devMode: true })
  }

  const token = req.cookies.get(COOKIE_NAME)?.value
  if (!token) {
    return NextResponse.json({ authenticated: false }, { status: 401 })
  }

  try {
    const payload = jwt.verify(token, JWT_SECRET) as {
      userId: string; email: string; username: string
    }
    return NextResponse.json({
      authenticated: true,
      userId:   payload.userId,
      email:    payload.email,
      username: payload.username,
    })
  } catch {
    return NextResponse.json({ authenticated: false }, { status: 401 })
  }
}
