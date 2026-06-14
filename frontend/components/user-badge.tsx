"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { LogOut, User, ChevronDown, Zap } from "lucide-react"
import { cn } from "@/lib/utils"
import type { SessionUser } from "@/lib/useSession"

type Props = {
  user:    SessionUser
  logout:  () => void
}

export function UserBadge({ user, logout }: Props) {
  const [open, setOpen] = useState(false)

  const initials = user.username.slice(0, 2).toUpperCase()

  return (
    <div className="relative">
      {/* Trigger */}
      <button
        onClick={() => setOpen(o => !o)}
        className="flex items-center gap-2 rounded-full border border-border bg-card px-2.5 py-1.5 transition-colors hover:border-primary/40"
      >
        {/* Avatar circle */}
        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/20 font-mono text-[10px] font-bold text-primary">
          {initials}
        </span>
        <span className="hidden font-mono text-[11px] text-muted-foreground sm:block">
          {user.username}
        </span>
        {user.isDemo && (
          <span className="hidden rounded-full border border-chart-4/30 bg-chart-4/10 px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-widest text-chart-4 sm:block">
            demo
          </span>
        )}
        <ChevronDown className={cn("h-3 w-3 text-muted-foreground transition-transform", open && "rotate-180")} />
      </button>

      {/* Backdrop */}
      <AnimatePresence>
        {open && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
            <motion.div
              initial={{ opacity: 0, y: -6, scale: 0.97 }}
              animate={{ opacity: 1, y: 0,  scale: 1    }}
              exit={{    opacity: 0, y: -6, scale: 0.97 }}
              transition={{ duration: 0.13 }}
              className="fixed right-4 top-[68px] z-50 w-56 rounded-2xl border border-border bg-[oklch(0.18_0.014_240)] p-3 shadow-2xl"
              style={{ boxShadow: "0 8px 40px -4px rgba(0,0,0,0.8)" }}
            >
              {/* User info */}
              <div className="mb-3 border-b border-border pb-3">
                <div className="flex items-center gap-2.5">
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/20 font-mono text-sm font-bold text-primary">
                    {initials}
                  </span>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">{user.username}</p>
                    <p className="truncate font-mono text-[10px] text-muted-foreground">{user.email}</p>
                  </div>
                </div>
                {user.isDemo && (
                  <div className="mt-2 flex items-center gap-1.5 rounded-lg border border-chart-4/20 bg-chart-4/10 px-2.5 py-1.5">
                    <Zap className="h-3 w-3 shrink-0 text-chart-4" />
                    <p className="font-mono text-[10px] text-chart-4">Demo account — register to save data</p>
                  </div>
                )}
              </div>

              {/* Menu items */}
              <div className="space-y-0.5">
                <a
                  href={process.env.NEXT_PUBLIC_LANDING_URL ?? "http://localhost:4000"}
                  className="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm text-muted-foreground transition-colors hover:bg-secondary/40 hover:text-foreground"
                >
                  <User className="h-3.5 w-3.5" />
                  Account
                </a>
                <button
                  onClick={() => { setOpen(false); logout() }}
                  className="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm text-destructive transition-colors hover:bg-destructive/10"
                >
                  <LogOut className="h-3.5 w-3.5" />
                  Sign out
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
