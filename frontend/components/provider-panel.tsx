"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Zap, Eye, EyeOff, Check, ChevronDown, Plus } from "lucide-react"
import { cn } from "@/lib/utils"
import type { ProviderName, ProviderUsage } from "@/lib/useBackend"

const PROVIDERS: { id: ProviderName; label: string; model: string; limit: string; color: string }[] = [
  { id: "groq",   label: "Groq",   model: "Llama 3.3 70B",    limit: "14,400 req/day", color: "text-chart-4"  },
  { id: "gemini", label: "Gemini", model: "2.5 Flash",         limit: "1,500 req/day",  color: "text-primary"  },
  { id: "openai", label: "OpenAI", model: "GPT-4o-mini",       limit: "paid",           color: "text-chart-2"  },
  { id: "custom", label: "Custom", model: "any OpenAI-compat", limit: "varies",         color: "text-chart-5"  },
]

type Props = {
  provider:  ProviderName
  keysSet:   Record<string, boolean>
  usage:     Record<string, ProviderUsage>
  onSetProvider: (p: ProviderName) => void
  onSetKey:      (p: ProviderName, k: string) => void
  onSetCustom:   (url: string, model: string, key: string) => void
}

function UsageBar({ pct, color }: { pct: number; color: string }) {
  const safe  = Math.min(100, Math.max(0, pct))
  const clr   = safe > 80 ? "bg-destructive" : safe > 50 ? "bg-chart-4" : "bg-chart-2"
  return (
    <div className="mt-1 h-1 w-full rounded-full bg-secondary/50">
      <motion.div
        className={cn("h-1 rounded-full", clr)}
        initial={{ width: 0 }}
        animate={{ width: `${safe}%` }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      />
    </div>
  )
}

function KeyInput({
  provider, label, hasKey, onSave,
}: {
  provider: ProviderName
  label: string
  hasKey: boolean
  onSave: (k: string) => void
}) {
  const [editing, setEditing] = useState(false)
  const [val, setVal]         = useState("")
  const [show, setShow]       = useState(false)

  if (!editing) {
    return (
      <button
        onClick={() => setEditing(true)}
        className={cn(
          "flex items-center gap-1.5 rounded-md border px-2 py-1 font-mono text-[10px] uppercase tracking-widest transition-colors",
          hasKey
            ? "border-chart-2/30 bg-chart-2/10 text-chart-2"
            : "border-border bg-secondary/30 text-muted-foreground hover:border-primary/30 hover:text-foreground",
        )}
      >
        {hasKey ? <Check className="h-3 w-3" /> : <Plus className="h-3 w-3" />}
        {hasKey ? "key set" : "add key"}
      </button>
    )
  }

  return (
    <div className="flex items-center gap-1">
      <div className="relative flex-1">
        <input
          autoFocus
          type={show ? "text" : "password"}
          value={val}
          onChange={e => setVal(e.target.value)}
          onKeyDown={e => {
            if (e.key === "Enter" && val.trim()) { onSave(val.trim()); setEditing(false); setVal("") }
            if (e.key === "Escape") { setEditing(false); setVal("") }
          }}
          placeholder={`${label} API key…`}
          className="w-full rounded-md border border-primary/40 bg-background/60 px-2 py-1 font-mono text-[10px] text-foreground outline-none placeholder:text-muted-foreground"
        />
        <button
          onClick={() => setShow(s => !s)}
          className="absolute right-1.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
        >
          {show ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
        </button>
      </div>
      <button
        onClick={() => { if (val.trim()) { onSave(val.trim()); setEditing(false); setVal("") } }}
        className="rounded-md bg-primary/20 px-2 py-1 font-mono text-[10px] text-primary hover:bg-primary/30"
      >
        save
      </button>
    </div>
  )
}

export function ProviderPanel({ provider, keysSet, usage, onSetProvider, onSetKey, onSetCustom }: Props) {
  const [open,        setOpen]        = useState(false)
  const [customUrl,   setCustomUrl]   = useState("")
  const [customModel, setCustomModel] = useState("")
  const [customKey,   setCustomKey]   = useState("")

  const active = PROVIDERS.find(p => p.id === provider) ?? PROVIDERS[0]
  const activeUsage = usage[provider] ?? { requests: 0, tokens_in: 0, tokens_out: 0, daily_request_limit: 0, usage_pct: 0 }

  return (
    <div className="relative">
      {/* Trigger button */}
      <button
        onClick={() => setOpen(o => !o)}
        className="flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1.5 font-mono text-[10px] uppercase tracking-widest text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground"
      >
        <Zap className={cn("h-3 w-3", active.color)} />
        <span className={active.color}>{active.label}</span>
        <span className="text-muted-foreground/60">·</span>
        <span>{activeUsage.usage_pct.toFixed(0)}%</span>
        <ChevronDown className={cn("h-3 w-3 transition-transform", open && "rotate-180")} />
      </button>

      {/* Dropdown panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.97 }}
            transition={{ duration: 0.15 }}
            className="glass absolute right-0 top-10 z-50 w-80 rounded-2xl p-4 shadow-2xl"
          >
            <p className="mb-3 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              Brain Provider
            </p>

            <div className="space-y-2">
              {PROVIDERS.map(p => {
                const u    = usage[p.id] ?? { requests: 0, usage_pct: 0, daily_request_limit: 0, tokens_in: 0, tokens_out: 0 }
                const isActive = p.id === provider

                return (
                  <div
                    key={p.id}
                    className={cn(
                      "rounded-xl border p-3 transition-colors",
                      isActive
                        ? "border-primary/40 bg-primary/5"
                        : "border-border bg-secondary/20 hover:border-border/80",
                    )}
                  >
                    {/* Provider row */}
                    <div className="flex items-center justify-between">
                      <button
                        onClick={() => { onSetProvider(p.id); }}
                        className="flex items-center gap-2"
                      >
                        <span className={cn(
                          "h-2 w-2 rounded-full border-2",
                          isActive ? "border-primary bg-primary" : "border-muted-foreground",
                        )} />
                        <span className={cn("text-sm font-medium", p.color)}>{p.label}</span>
                        <span className="font-mono text-[10px] text-muted-foreground">{p.model}</span>
                      </button>

                      <KeyInput
                        provider={p.id}
                        label={p.label}
                        hasKey={keysSet[p.id] ?? false}
                        onSave={key => onSetKey(p.id, key)}
                      />
                    </div>

                    {/* Usage bar (only if has key) */}
                    {(keysSet[p.id] || isActive) && (
                      <div className="mt-2">
                        <div className="flex items-center justify-between font-mono text-[9px] text-muted-foreground">
                          <span>{u.requests} req today</span>
                          <span>{u.usage_pct.toFixed(1)}% of {p.limit}</span>
                        </div>
                        <UsageBar pct={u.usage_pct} color={p.color} />
                        {u.tokens_in + u.tokens_out > 0 && (
                          <p className="mt-0.5 font-mono text-[9px] text-muted-foreground">
                            {(u.tokens_in + u.tokens_out).toLocaleString()} tokens total
                          </p>
                        )}
                      </div>
                    )}

                    {/* Custom provider extra fields */}
                    {p.id === "custom" && isActive && (
                      <div className="mt-3 space-y-2 border-t border-border pt-3">
                        <input
                          value={customUrl}
                          onChange={e => setCustomUrl(e.target.value)}
                          placeholder="Base URL (e.g. http://localhost:11434/v1)"
                          className="w-full rounded-md border border-border bg-background/60 px-2 py-1 font-mono text-[10px] text-foreground outline-none placeholder:text-muted-foreground"
                        />
                        <input
                          value={customModel}
                          onChange={e => setCustomModel(e.target.value)}
                          placeholder="Model name (e.g. llama3.2)"
                          className="w-full rounded-md border border-border bg-background/60 px-2 py-1 font-mono text-[10px] text-foreground outline-none placeholder:text-muted-foreground"
                        />
                        <button
                          onClick={() => { if (customUrl && customModel) { onSetCustom(customUrl, customModel, customKey) } }}
                          className="w-full rounded-md bg-primary/20 py-1 font-mono text-[10px] text-primary hover:bg-primary/30"
                        >
                          apply custom provider
                        </button>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>

            <p className="mt-3 font-mono text-[9px] text-muted-foreground/60">
              Keys saved in memory only — not persisted to disk.
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
