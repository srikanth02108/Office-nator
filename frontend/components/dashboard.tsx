"use client"

import { useCallback, useEffect, useState } from "react"
import { Cpu, Sparkles, Undo2, Wifi, WifiOff } from "lucide-react"
import { motion } from "framer-motion"
import { VoiceInterface } from "./voice-interface"
import { TranscriptTerminal, type TranscriptLine } from "./transcript-terminal"
import { AgentBrain } from "./agent-brain"
import { useBackend } from "@/lib/useBackend"
import type { AgentState } from "./voice-interface"

export function Dashboard() {
  const { connected, state, lastEvent, startListening, stopListening, triggerUndo } =
    useBackend()

  // Map backend status → AgentState type the child components expect
  const agentState: AgentState = state.status as AgentState

  // Convert backend transcript entries → TranscriptLine shape
  const transcriptLines: TranscriptLine[] = state.transcript.map((entry) => ({
    id: entry.id,
    hindi: entry.hindi,
    english: entry.english,
    time: entry.time,
  }))

  // Notification toast for events
  const [toast, setToast] = useState<string | null>(null)

  useEffect(() => {
    if (!lastEvent) return
    if (lastEvent.type === "error") {
      setToast(`⚠ ${lastEvent.message}`)
      setTimeout(() => setToast(null), 4000)
    } else if (lastEvent.type === "done") {
      setToast(`✓ ${lastEvent.plan}`)
      setTimeout(() => setToast(null), 3000)
    } else if (lastEvent.type === "confirm_required") {
      setToast(`❓ Confirm: "${lastEvent.plan}" — say Yes or No`)
      setTimeout(() => setToast(null), 8000)
    } else if (lastEvent.type === "aborted") {
      setToast(`✕ ${lastEvent.reason}`)
      setTimeout(() => setToast(null), 3000)
    } else if (lastEvent.type === "undo") {
      setToast(`↩ ${lastEvent.message}`)
      setTimeout(() => setToast(null), 2000)
    }
  }, [lastEvent])

  const handleToggle = useCallback(() => {
    if (agentState === "idle") {
      startListening()
    } else {
      stopListening()
    }
  }, [agentState, startListening, stopListening])

  const handleKill = useCallback(() => {
    stopListening()
    triggerUndo()
  }, [stopListening, triggerUndo])

  return (
    <main className="grid-bg relative min-h-svh overflow-hidden">
      {/* ambient neon glows */}
      <div className="pointer-events-none absolute -top-32 left-1/2 h-96 w-96 -translate-x-1/2 rounded-full bg-primary/10 blur-[120px]" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-80 w-80 rounded-full bg-chart-2/10 blur-[120px]" />

      {/* top bar */}
      <header className="relative z-10 flex items-center justify-between border-b border-border px-4 py-4 sm:px-8">
        <div className="flex items-center gap-3">
          <div className="glass flex h-9 w-9 items-center justify-center rounded-lg ring-1 ring-primary/40">
            <Sparkles className="h-4 w-4 text-primary" />
          </div>
          <div className="leading-tight">
            <h1 className="text-sm font-semibold tracking-tight">
              Project Sutra
            </h1>
            <p className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              Autonomous Desktop Agent
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* backend connection badge */}
          <div
            className={`flex items-center gap-1.5 rounded-full border px-3 py-1.5 font-mono text-[10px] uppercase tracking-widest transition-colors ${
              connected
                ? "border-chart-2/40 bg-chart-2/10 text-chart-2"
                : "border-destructive/40 bg-destructive/10 text-destructive"
            }`}
          >
            {connected ? (
              <Wifi className="h-3 w-3" />
            ) : (
              <WifiOff className="h-3 w-3" />
            )}
            {connected ? "backend connected" : "backend offline"}
          </div>

          <div className="flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1.5 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            <Cpu className="h-3.5 w-3.5 text-primary" />
            {state.command_count} cmds · {connected ? "online" : "offline"}
          </div>
        </div>
      </header>

      {/* three-section layout */}
      <div className="relative z-10 grid grid-cols-1 gap-4 p-4 sm:p-6 lg:grid-cols-[1fr_1.4fr_1fr] lg:gap-6">
        <div className="order-2 h-[420px] lg:order-1 lg:h-[calc(100svh-9rem)]">
          <TranscriptTerminal lines={transcriptLines} />
        </div>

        <div className="order-1 lg:order-2">
          <div className="glass h-full rounded-2xl">
            <VoiceInterface
              state={agentState}
              onToggle={handleToggle}
              connected={connected}
              lastEnglish={state.last_english}
            />
          </div>
        </div>

        <div className="order-3 h-[520px] lg:h-[calc(100svh-9rem)]">
          <AgentBrain
            executing={agentState === "executing"}
            plan={state.last_plan}
            steps={state.last_steps}
            memories={state.memories}
          />
        </div>
      </div>

      {/* kill switch FAB */}
      <motion.button
        type="button"
        onClick={handleKill}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.92 }}
        className="fixed bottom-6 right-6 z-50 flex items-center gap-2 rounded-full bg-destructive px-5 py-3.5 font-medium text-white shadow-lg"
        style={{ boxShadow: "0 0 32px -6px var(--destructive)" }}
        aria-label="Kill switch and undo last action"
      >
        <Undo2 className="h-5 w-5" />
        <span className="hidden text-sm sm:inline">Kill Switch / Undo</span>
      </motion.button>

      {/* toast notification */}
      {toast && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          className="fixed bottom-24 right-6 z-50 max-w-sm rounded-xl border border-border bg-card px-4 py-3 font-mono text-sm text-foreground shadow-xl"
        >
          {toast}
        </motion.div>
      )}
    </main>
  )
}
