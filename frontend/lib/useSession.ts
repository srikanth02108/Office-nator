"use client"

import { useEffect, useState } from "react"

export type SessionUser = {
  userId:   string
  email:    string
  username: string
  isDemo?:  boolean
}

export function useSession() {
  const [user,    setUser]    = useState<SessionUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch("/api/session")
      .then(r => r.json())
      .then(data => {
        if (data.authenticated) {
          setUser({ userId: data.userId, email: data.email, username: data.username })
        } else if (data.devMode) {
          // Dev mode — no auth configured, show guest user
          setUser({ userId: "dev", email: "dev@local", username: "developer" })
        } else {
          setUser(null)
        }
      })
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [])

  const logout = async () => {
    // Clear cookie via landing page logout endpoint
    const landingUrl = process.env.NEXT_PUBLIC_LANDING_URL ?? "http://localhost:4000"
    await fetch(`${landingUrl}/api/auth/logout`, { method: "POST", credentials: "include" })
    window.location.href = landingUrl + "/login"
  }

  return { user, loading, logout }
}
