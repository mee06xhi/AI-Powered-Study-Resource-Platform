import { useState, useRef, useEffect } from "react"
import { askAgent } from "../api"

const TOOL_LABELS = {
  analyze_pyq: "Analyzed PYQ papers",
  search_resources: "Searched for resources",
}

const SUGGESTIONS = [
  "What are the most repeated DBMS topics?",
  "Find notes for BCS403",
  "Which topics should I prioritize for the DBMS exam?",
]

function AgentChat({ onBack }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading])

  async function sendMessage(text) {
    const trimmed = text.trim()
    if (!trimmed || loading) return

    setMessages((prev) => [...prev, { role: "user", text: trimmed }])
    setInput("")
    setLoading(true)
    setError(null)

    try {
      const result = await askAgent(trimmed)
      setMessages((prev) => [
        ...prev,
        { role: "agent", text: result.answer, toolUsed: result.tool_used },
      ])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function handleSubmit(e) {
    e.preventDefault()
    sendMessage(input)
  }

  return (
    <div className="max-w-3xl mx-auto py-12 px-6 md:px-0 flex flex-col min-h-[calc(100vh-5rem)]">
      <button
        onClick={onBack}
        className="text-sm text-on-surface-variant hover:text-primary transition-colors mb-6 flex items-center gap-1 self-start"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Back to Search
      </button>

      <div className="glass-panel rounded-xl border-t-2 border-accent p-6 mb-6">
        <h1 className="font-display text-2xl font-semibold text-primary">Ask SmartPrep</h1>
        <p className="text-sm text-on-surface-variant mt-1">
          Ask about repeated exam topics, or ask it to find study resources for a subject.
        </p>
      </div>

      <div className="flex-grow flex flex-col gap-4 mb-6">
        {messages.length === 0 && (
          <div className="flex flex-col gap-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => sendMessage(s)}
                className="glass-panel text-left rounded-xl p-4 text-sm text-on-surface-variant
                           hover:text-primary hover:border-info/40 border-t border-white/5 transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[85%] rounded-xl p-4 text-sm leading-relaxed whitespace-pre-wrap
                ${m.role === "user"
                  ? "bg-accent/90 text-white"
                  : "glass-panel border-t border-white/5 text-on-surface"}
              `}
            >
              {m.role === "agent" && m.toolUsed && (
                <span className="inline-block mb-2 text-xs font-semibold uppercase tracking-wider text-info bg-info/10 rounded-full px-2.5 py-1">
                  {TOOL_LABELS[m.toolUsed] || m.toolUsed}
                </span>
              )}
              {m.text}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="glass-panel rounded-xl p-4 text-sm text-on-surface-variant border-t border-white/5">
              Thinking…
            </div>
          </div>
        )}

        {error && <p className="text-sm text-red-400">{error}</p>}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="flex gap-3 sticky bottom-6">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about repeated topics or study resources…"
          className="flex-grow bg-surface-container border border-outline-variant text-on-surface px-4 py-3 rounded-lg text-sm
                     focus:outline-none focus:border-info focus:ring-1 focus:ring-info/40 transition-colors
                     placeholder:text-outline-variant"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-accent hover:bg-accent-hover disabled:opacity-50 disabled:cursor-not-allowed
                     text-white font-semibold text-sm px-6 rounded-lg ai-glow transition-colors"
        >
          Send
        </button>
      </form>
    </div>
  )
}

export default AgentChat