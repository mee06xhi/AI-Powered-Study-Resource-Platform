import { useState } from "react"
import { generateStudyPlan } from "../api"

function StudyPlanner({ onBack }) {
  const [subject, setSubject] = useState("")
  const [examDate, setExamDate] = useState("")
  const [daysAvailable, setDaysAvailable] = useState(7)
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setPlan(null)
    try {
      const data = await generateStudyPlan({ subject, daysAvailable, examDate })
      setPlan(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto py-12 px-6 md:px-0">
      <button
        onClick={onBack}
        className="text-sm text-on-surface-variant hover:text-primary transition-colors mb-6 flex items-center gap-1"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Back to Search
      </button>

      <div className="glass-panel rounded-xl border-t-2 border-accent p-6 mb-8">
        <h1 className="font-display text-2xl font-semibold text-primary">Study Planner</h1>
        <p className="text-sm text-on-surface-variant mt-1">
          Get a day-by-day plan, weighted toward repeated PYQ topics when available.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="glass-panel rounded-xl p-6 flex flex-col gap-6 mb-8">
        <div className="flex flex-col gap-2">
          <label className="text-xs font-semibold uppercase tracking-wider text-on-surface-variant">Subject</label>
          <input
            type="text"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            placeholder="e.g., Database Management Systems"
            required
            className="bg-surface-container border-b border-outline-variant text-on-surface px-4 py-3 rounded-t-md text-sm focus:outline-none focus:border-info focus:ring-1 focus:ring-info/40"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-on-surface-variant">Days available</label>
            <input
              type="number"
              min={1}
              max={30}
              value={daysAvailable}
              onChange={(e) => setDaysAvailable(Number(e.target.value))}
              required
              className="bg-surface-container border-b border-outline-variant text-on-surface px-4 py-3 rounded-t-md text-sm focus:outline-none focus:border-info focus:ring-1 focus:ring-info/40"
            />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-on-surface-variant">Exam date (optional)</label>
            <input
              type="date"
              value={examDate}
              onChange={(e) => setExamDate(e.target.value)}
              className="bg-surface-container border-b border-outline-variant text-on-surface px-4 py-3 rounded-t-md text-sm focus:outline-none focus:border-info focus:ring-1 focus:ring-info/40"
            />
          </div>
        </div>

        {error && <p className="text-sm text-red-400">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="bg-accent hover:bg-accent-hover disabled:opacity-50 text-white font-semibold text-sm py-4 rounded-lg ai-glow transition-colors"
        >
          {loading ? "Generating…" : "Generate Plan"}
        </button>
      </form>

      {plan && (
        <div className="flex flex-col gap-4">
          {plan.days.map((d) => (
            <div key={d.day} className="glass-panel rounded-xl p-5 border-t border-white/5">
              <div className="flex items-baseline justify-between mb-2">
                <span className="font-display text-lg font-semibold text-primary">Day {d.day}</span>
                <span className="text-sm text-info">{d.focus}</span>
              </div>
              <ul className="list-disc list-inside text-sm text-on-surface-variant space-y-1">
                {d.tasks.map((t, i) => (
                  <li key={i}>{t}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default StudyPlanner