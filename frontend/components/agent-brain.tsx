"use client"

import { Brain, Database, Workflow } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import type { Step } from "@/lib/useBackend"

type Props = {
  executing: boolean
  plan: string
  steps: Step[]
  memories: string[]
}

const FALLBACK_MEMORIES = [
  "Prefers dark blue table headers",
  "Always use Arial font in documents",
  "Auto-save every 5 minutes",
  "Default language: Hindi → English",
  "Keep sidebar collapsed by default",
]

function JsonBlock({ steps }: { steps: Step[] }) {
  if (!steps.length) {
    return (
      <pre className="overflow-x-auto rounded-lg border border-border bg-background/60 p-3 font-mono text-xs leading-relaxed text-muted-foreground">
        {"// Waiting for command..."}
      </pre>
    )
  }

  return (
    <pre className="overflow-x-auto rounded-lg border border-border bg-background/60 p-3 font-mono text-xs leading-relaxed">
      <code>
        <span className="text-muted-foreground">{"["}</span>
        {steps.map((step, i) => (
          <div key={i} className="pl-3">
            <span className="text-muted-foreground">{"{ "}</span>
            <span className="text-primary">&quot;action&quot;</span>
            <span className="text-muted-foreground">: </span>
            <span className="text-chart-2">&quot;{step.action}&quot;</span>
            {step.keys && (
              <>
                <span className="text-muted-foreground">, </span>
                <span className="text-primary">&quot;keys&quot;</span>
                <span className="text-muted-foreground">: [</span>
                {step.keys.map((k, ki) => (
                  <span key={ki}>
                    <span className="text-chart-4">&quot;{k}&quot;</span>
                    {ki < step.keys!.length - 1 && (
                      <span className="text-muted-foreground">, </span>
                    )}
                  </span>
                ))}
                <span className="text-muted-foreground">]</span>
              </>
            )}
            {step.target && (
              <>
                <span className="text-muted-foreground">, </span>
                <span className="text-primary">&quot;target&quot;</span>
                <span className="text-muted-foreground">: </span>
                <span className="text-chart-4">&quot;{step.target}&quot;</span>
              </>
            )}
            {step.text && (
              <>
                <span className="text-muted-foreground">, </span>
                <span className="text-primary">&quot;text&quot;</span>
                <span className="text-muted-foreground">: </span>
                <span className="text-chart-4">&quot;{step.text}&quot;</span>
              </>
            )}
            {step.seconds !== undefined && (
              <>
                <span className="text-muted-foreground">, </span>
                <span className="text-primary">&quot;seconds&quot;</span>
                <span className="text-muted-foreground">: </span>
                <span className="text-chart-4">{step.seconds}</span>
              </>
            )}
            <span className="text-muted-foreground">
              {" }"}
              {i < steps.length - 1 ? "," : ""}
            </span>
          </div>
        ))}
        <span className="text-muted-foreground">{"]"}</span>
      </code>
    </pre>
  )
}

export function AgentBrain({ executing, plan, steps, memories }: Props) {
  const displayMemories = memories.length > 0 ? memories : FALLBACK_MEMORIES

  return (
    <div className="flex h-full flex-col gap-4">
      {/* Mem0 Context Store */}
      <section className="glass flex flex-1 flex-col overflow-hidden rounded-2xl">
        <header className="flex items-center justify-between border-b border-border px-4 py-3">
          <div className="flex items-center gap-2 text-sm font-medium">
            <Brain className="h-4 w-4 text-primary" />
            Mem0 Context Store
          </div>
          <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            {displayMemories.length} prefs
          </span>
        </header>
        <ul className="flex-1 space-y-2 overflow-y-auto p-4">
          <AnimatePresence>
            {displayMemories.map((m, i) => (
              <motion.li
                key={m}
                initial={{ opacity: 0, x: 12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.06 }}
                className="flex items-start gap-2 rounded-lg border border-border bg-secondary/30 px-3 py-2 text-sm"
              >
                <Database className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary/70" />
                <span className="text-muted-foreground">{m}</span>
              </motion.li>
            ))}
          </AnimatePresence>
        </ul>
      </section>

      {/* Execution Plan */}
      <section className="glass flex flex-1 flex-col overflow-hidden rounded-2xl">
        <header className="flex items-center justify-between border-b border-border px-4 py-3">
          <div className="flex items-center gap-2 text-sm font-medium">
            <Workflow className="h-4 w-4 text-primary" />
            Execution Plan
          </div>
          <span className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                executing ? "animate-pulse bg-chart-2" : "bg-muted-foreground"
              }`}
            />
            {executing ? "running" : steps.length ? "queued" : "idle"}
          </span>
        </header>
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {plan && (
            <p className="text-xs text-muted-foreground border-l-2 border-primary/40 pl-3 italic">
              {plan}
            </p>
          )}
          <JsonBlock steps={steps} />
        </div>
      </section>
    </div>
  )
}
