'use client'

import { cn } from '@/lib/utils'

const PROVIDERS = [
  { name: 'Google', tone: 'hover:border-destructive/50 hover:text-destructive' },
  { name: 'GitHub', tone: 'hover:border-foreground/40' },
  { name: 'Microsoft', tone: 'hover:border-primary/60 hover:text-primary' },
]

export function OAuthButtons() {
  return (
    <div className="grid grid-cols-3 gap-3">
      {PROVIDERS.map((p) => (
        <button
          key={p.name}
          type="button"
          className={cn(
            'flex h-11 items-center justify-center rounded-lg border border-border bg-background/60 text-sm font-medium text-muted-foreground transition-colors',
            p.tone,
          )}
        >
          {p.name}
        </button>
      ))}
    </div>
  )
}
