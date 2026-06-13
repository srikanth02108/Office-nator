"use client"

import { useCallback, useEffect, useRef, useState } from "react"

const WS_URL = (process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000") + "/ws"
const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000"

export type AgentStatus = "idle" | "listening" | "processing" | "executing"

export type TranscriptEntry = {
  id: number
  hindi: string
  english: string
  plan: string
  steps: Step[]
  success: boolean
  time: string
}

export type Step = {
  action: string
  keys?: string[]
  target?: string
  text?: string
  seconds?: number
}

export type BackendState = {
  status: AgentStatus
  command_count: number
  last_hindi: string
  last_english: string
  last_plan: string
  last_steps: Step[]
  memories: string[]
  transcript: TranscriptEntry[]
}

export type BackendEvent =
  | { type: "state" } & BackendState
  | { type: "status"; status: AgentStatus }
  | { type: "plan"; plan: string; steps: Step[]; requires_confirmation: boolean }
  | { type: "transcript_entry"; entry: TranscriptEntry }
  | { type: "transcript_partial"; english: string }
  | { type: "confirm_required"; plan: string }
  | { type: "done"; plan: string }
  | { type: "undo"; message: string }
  | { type: "aborted"; reason: string }
  | { type: "error"; message: string }

const DEFAULT_STATE: BackendState = {
  status: "idle",
  command_count: 0,
  last_hindi: "",
  last_english: "",
  last_plan: "",
  last_steps: [],
  memories: [],
  transcript: [],
}

export function useBackend() {
  const [connected, setConnected] = useState(false)
  const [backendState, setBackendState] = useState<BackendState>(DEFAULT_STATE)
  const [lastEvent, setLastEvent] = useState<BackendEvent | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
    }

    ws.onclose = () => {
      setConnected(false)
      // Reconnect after 2 seconds
      reconnectTimer.current = setTimeout(connect, 2000)
    }

    ws.onerror = () => {
      ws.close()
    }

    ws.onmessage = (e) => {
      try {
        const msg: BackendEvent = JSON.parse(e.data)
        setLastEvent(msg)

        if (msg.type === "state") {
          // Full state snapshot on connect
          setBackendState({
            status: msg.status,
            command_count: msg.command_count,
            last_hindi: msg.last_hindi,
            last_english: msg.last_english,
            last_plan: msg.last_plan,
            last_steps: msg.last_steps,
            memories: msg.memories,
            transcript: msg.transcript,
          })
        } else if (msg.type === "status") {
          setBackendState((prev) => ({ ...prev, status: msg.status }))
        } else if (msg.type === "plan") {
          setBackendState((prev) => ({
            ...prev,
            last_plan: msg.plan,
            last_steps: msg.steps,
          }))
        } else if (msg.type === "transcript_entry") {
          setBackendState((prev) => ({
            ...prev,
            transcript: [...prev.transcript, msg.entry],
            last_hindi: msg.entry.hindi,
            last_english: msg.entry.english,
          }))
        } else if (msg.type === "transcript_partial") {
          setBackendState((prev) => ({
            ...prev,
            last_english: msg.english,
          }))
        }
      } catch {
        // ignore malformed messages
      }
    }
  }, [])

  useEffect(() => {
    connect()
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
      wsRef.current?.close()
    }
  }, [connect])

  const sendCommand = useCallback((command: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ command }))
    }
  }, [])

  const startListening = useCallback(async () => {
    // Try WebSocket first, fall back to REST
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      sendCommand("start")
    } else {
      await fetch(`${API_URL}/start`, { method: "POST" })
    }
  }, [sendCommand])

  const stopListening = useCallback(async () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      sendCommand("stop")
    } else {
      await fetch(`${API_URL}/stop`, { method: "POST" })
    }
  }, [sendCommand])

  const triggerUndo = useCallback(async () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      sendCommand("undo")
    } else {
      await fetch(`${API_URL}/undo`, { method: "POST" })
    }
  }, [sendCommand])

  return {
    connected,
    state: backendState,
    lastEvent,
    startListening,
    stopListening,
    triggerUndo,
  }
}
