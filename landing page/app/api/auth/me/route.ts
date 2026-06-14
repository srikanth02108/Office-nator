import { NextResponse } from 'next/server'
import { getAuthCookie } from '@/lib/auth'
import { getDb } from '@/lib/mongodb'
import { ObjectId } from 'mongodb'

// Returns current user profile + stored preferences (provider, memories etc.)
export async function GET() {
  const payload = await getAuthCookie()
  if (!payload) return NextResponse.json({ error: 'Not authenticated' }, { status: 401 })

  try {
    const db = await getDb()
    const user = await db.collection('users').findOne(
      { _id: new ObjectId(payload.userId) },
      { projection: { password: 0 } },  // never return password hash
    )
    if (!user) return NextResponse.json({ error: 'User not found' }, { status: 404 })

    return NextResponse.json({
      userId:      payload.userId,
      email:       user.email,
      username:    user.username,
      isDemo:      user.isDemo ?? false,
      preferences: user.preferences ?? { provider: 'groq', memories: [] },
      createdAt:   user.createdAt,
    })
  } catch (err) {
    console.error('[me]', err)
    return NextResponse.json({ error: 'Server error' }, { status: 500 })
  }
}
