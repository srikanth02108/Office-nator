"use client"

import { useEffect, useRef } from "react"
import { Terminal } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

export type TranscriptLine = {
  id: number
  hindi: string
  english: string
  time: string
  plan?: string
}

export function TranscriptTerminal({ lines }: { lines: TranscriptLine[] }) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    })
  }, [lines])

  return (
    <div className="glass flex h-full flex-col overflow-hidden rounded-2xl">
      {/* title bar */}
      <header className="flex items-center gap-2 border-b border-border px-4 py-3">
        <div className="flex gap-1.5">
          <span className="h-3 w-3 rounded-full bg-destructive/70" />
          <span className="h-3 w-3 rounded-full bg-chart-4/70" />
          <span className="h-3 w-3 rounded-full bg-chart-2/70" />
        </div>
        <div className="ml-2 flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-muted-foreground">
          <Terminal className="h-3.5 w-3.5 text-primary" />
          live_transcript.log
        </div>
      </header>

      <div
        ref={scrollRef}
        className="flex-1 space-y-4 overflow-y-auto p-4 font-mono text-sm"
      >
        <p className="text-xs text-muted-foreground">
          {"> sutra-agent --listen --lang=hi --translate=en"}
        </p>
        <AnimatePresence initial={false}>
          {lines.map((line) => (
            <motion.div
              key={line.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="space-y-1.5"
            >
              {/* user input */}
              <div className="flex flex-col gap-1 rounded-lg border border-border bg-secondary/40 px-3 py-2">
                <span className="text-[10px] uppercase tracking-widest text-muted-foreground">
                  {line.time} · user · hi-IN
                </span>
                <span className="text-foreground">{line.hindi}</span>
              </div>
              {/* translated output */}
              <div className="ml-4 flex flex-col gap-1 rounded-lg border border-primary/30 bg-primary/5 px-3 py-2">
                <span className="text-[10px] uppercase tracking-widest text-primary/70">
                  translated · en-US
                </span>
                <span className="text-primary text-glow">
                  {"→ "}
                  {line.english}
                </span>
                {line.plan && (
                  <span className="text-[10px] text-muted-foreground mt-1 pl-3 border-l border-primary/20">
                    ⚡ {line.plan}
                  </span>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* blinking cursor */}
        <div className="flex items-center gap-1 text-primary">
          <span>{"> "}</span>
          <motion.span
            className="inline-block h-4 w-2 bg-primary"
            animate={{ opacity: [1, 0, 1] }}
            transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY }}
          />
        </div>
      </div>
    </div>
  )
}
