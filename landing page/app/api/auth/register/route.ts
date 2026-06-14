import { NextRequest, NextResponse } from 'next/server'
import { getDb } from '@/lib/mongodb'
import { hashPassword, setAuthCookie } from '@/lib/auth'

export async function POST(req: NextRequest) {
  try {
    const { username, email, password } = await req.json()

    // Validate
    if (!username?.trim() || !email?.trim() || !password)
      return NextResponse.json({ error: 'All fields are required.' }, { status: 400 })

    if (password.length < 6)
      return NextResponse.json({ error: 'Password must be at least 6 characters.' }, { status: 400 })

    const db = await getDb()
    const users = db.collection('users')

    // Check existing
    const existing = await users.findOne({
      $or: [{ email: email.toLowerCase() }, { username: username.toLowerCase() }],
    })
    if (existing) {
      const field = existing.email === email.toLowerCase() ? 'Email' : 'Username'
      return NextResponse.json({ error: `${field} is already taken.` }, { status: 409 })
    }

    // Create user
    const hashed = await hashPassword(password)
    const result = await users.insertOne({
      username:  username.trim(),
      email:     email.toLowerCase().trim(),
      password:  hashed,
      createdAt: new Date(),
      // Store preferences/session data that the main app can read
      preferences: {
        provider: 'groq',
        memories: [],
      },
    })

    await setAuthCookie({
      userId:   result.insertedId.toString(),
      email:    email.toLowerCase().trim(),
      username: username.trim(),
    })

    return NextResponse.json({ ok: true, username: username.trim() })
  } catch (err) {
    console.error('[register]', err)
    return NextResponse.json({ error: 'Server error. Please try again.' }, { status: 500 })
  }
}
