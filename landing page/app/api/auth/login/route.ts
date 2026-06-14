import { NextRequest, NextResponse } from 'next/server'
import { getDb } from '@/lib/mongodb'
import { verifyPassword, setAuthCookie } from '@/lib/auth'

const DEMO_EMAIL = process.env.DEMO_EMAIL ?? 'demo@officenator.ai'
const DEMO_PASSWORD = process.env.DEMO_PASSWORD ?? 'demo1234'

export async function POST(req: NextRequest) {
  try {
    const { email, password, demo } = await req.json()

    const db = await getDb()
    const users = db.collection('users')

    // ── Demo login ────────────────────────────────────────────────────
    if (demo === true) {
      // Find or auto-create the demo account
      let demoUser = await users.findOne({ email: DEMO_EMAIL })

      if (!demoUser) {
        const { hashPassword } = await import('@/lib/auth')
        const hashed = await hashPassword(DEMO_PASSWORD)
        const result = await users.insertOne({
          username:    'demo',
          email:       DEMO_EMAIL,
          password:    hashed,
          isDemo:      true,
          createdAt:   new Date(),
          preferences: { provider: 'groq', memories: [] },
        })
        demoUser = { _id: result.insertedId, username: 'demo', email: DEMO_EMAIL }
      }

      await setAuthCookie({
        userId:   demoUser._id.toString(),
        email:    DEMO_EMAIL,
        username: 'demo',
      })

      return NextResponse.json({ ok: true, username: 'demo', isDemo: true })
    }

    // ── Normal login ──────────────────────────────────────────────────
    if (!email?.trim() || !password)
      return NextResponse.json({ error: 'Email and password are required.' }, { status: 400 })

    const user = await users.findOne({ email: email.toLowerCase().trim() })
    if (!user)
      return NextResponse.json({ error: 'No account found with that email.' }, { status: 401 })

    const valid = await verifyPassword(password, user.password)
    if (!valid)
      return NextResponse.json({ error: 'Incorrect password.' }, { status: 401 })

    await setAuthCookie({
      userId:   user._id.toString(),
      email:    user.email,
      username: user.username,
    })

    return NextResponse.json({ ok: true, username: user.username })
  } catch (err) {
    console.error('[login]', err)
    return NextResponse.json({ error: 'Server error. Please try again.' }, { status: 500 })
  }
}
