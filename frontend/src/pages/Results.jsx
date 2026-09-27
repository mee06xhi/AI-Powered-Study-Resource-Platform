import { useState, useEffect } from "react"
import { analyzePyq } from "../api"

const RESOURCE_TYPES = [
  "syllabus",
  "previous year question papers",
  "notes",
  "lab manual",
  "reference books",
  "youtube lectures",
  "nptel course",
]

const PYQ_ANALYSIS_TAB = "pyq-analysis"

// Tabs shown in the UI: resource types plus the analysis tab, inserted
// right after "previous year question papers" since that's where it's
// contextually relevant.
const TABS = [
  "syllabus",
  "previous year question papers",
  PYQ_ANALYSIS_TAB,
  "notes",
  "lab manual",
  "reference books",
  "youtube lectures",
  "nptel course",
]

const TAB_LABELS = {
  "syllabus": "Syllabus",
  "previous year question papers": "PYQ Papers",
  [PYQ_ANALYSIS_TAB]: "PYQ Analysis",
  "notes": "Notes",
  "lab manual": "Lab Manuals",
  "reference books": "Reference Books",
  "youtube lectures": "YouTube Lectures",
  "nptel course": "NPTEL",
}

function scoreBadge(score) {
  if (score >= 8) return "bg-emerald-400/10 text-emerald-300"
  if (score >= 4) return "bg-info/10 text-info"
  if (score >= 1) return "bg-accent/10 text-accent"
  return "bg-white/5 text-on-surface-variant"
}

function PyqAnalysisPanel() {
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    analyzePyq()
      .then((data) => {
        if (!cancelled) setAnalysis(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  if (loading) {
    return (
      <div className="glass-panel rounded-xl p-10 text-center text-on-surface-variant text-sm">
        Analyzing previous-year question papers…
      </div>
    )
  }

  if (error) {
    return (
      <div className="glass-panel rounded-xl p-10 text-center text-sm">
        <p className="text-red-400">{error}</p>
      </div>
    )
  }

  if (!analysis || analysis.topics.length === 0) {
    return (
      <div className="glass-panel rounded-xl p-10 text-center text-on-surface-variant text-sm">
        No repeated-question data available yet.
      </div>
    )
  }

  const maxFrequency = Math.max(...analysis.topics.map((t) => t.frequency))

  return (
    <div className="flex flex-col gap-6">
      <div className="glass-panel rounded-xl p-5 flex flex-wrap items-center gap-x-8 gap-y-2 border-t border-white/5">
        <div>
          <p className="text-xs uppercase tracking-wider text-on-surface-variant">Questions analysed</p>
          <p className="text-lg font-semibold text-primary">{analysis.total_questions_found}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wider text-on-surface-variant">Source files</p>
          <p className="text-sm text-on-surface">{analysis.source_files.join(", ")}</p>
        </div>
      </div>

      <div className="glass-panel rounded-xl p-6 border-t border-white/5">
        <h2 className="font-display text-lg font-semibold text-primary mb-5">Most Repeated Topics</h2>
        <div className="flex flex-col gap-4">
          {analysis.topics.map((topic, i) => (
            <div key={i} className="flex flex-col gap-1.5">
              <div className="flex items-baseline justify-between gap-4">
                <span className="text-sm font-medium text-on-surface capitalize truncate">{topic.topic}</span>
                <span className="text-xs text-on-surface-variant shrink-0">
                  {topic.frequency}× · {topic.percentage}%
                </span>
              </div>
              <div className="h-2 rounded-full bg-white/5 overflow-hidden">
                <div
                  className="h-full rounded-full bg-accent ai-glow"
                  style={{ width: `${Math.max(6, (topic.frequency / maxFrequency) * 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <h2 className="font-display text-lg font-semibold text-primary">Repeated Questions</h2>
        {analysis.topics.map((topic, i) => (
          <div
            key={i}
            className="glass-panel rounded-xl p-5 flex items-start justify-between gap-4 border-t border-white/5"
          >
            <div className="min-w-0">
              <p className="text-sm text-on-surface leading-relaxed">{topic.sample_question}</p>
              <p className="text-xs text-on-surface-variant mt-2 capitalize">Topic: {topic.topic}</p>
            </div>
            <span className={`shrink-0 text-xs font-semibold px-2.5 py-1 rounded-full ${scoreBadge(topic.frequency)}`}>
              {topic.frequency}×
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

function Results({ data, onBack }) {
  const [activeTab, setActiveTab] = useState(TABS[0])
  const activeResults = data.results[activeTab] || []

  return (
    <div className="max-w-4xl mx-auto py-12 px-6 md:px-0">
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
        <h1 className="font-display text-2xl font-semibold text-primary">
          {data.subject} <span className="text-on-surface-variant font-body text-lg">({data.subject_code})</span>
        </h1>
        <p className="text-sm text-on-surface-variant mt-1">
          {data.department} · Semester {data.semester}
        </p>
      </div>

      <div className="flex flex-wrap gap-2 border-b border-white/10 mb-6">
        {TABS.map((type) => (
          <button
            key={type}
            onClick={() => setActiveTab(type)}
            className={`px-4 py-2 text-xs font-semibold uppercase tracking-wider border-b-2 -mb-px transition-colors
              ${activeTab === type
                ? "border-info text-info"
                : "border-transparent text-on-surface-variant hover:text-primary"}
            `}
          >
            {TAB_LABELS[type]}
          </button>
        ))}
      </div>

      {activeTab === PYQ_ANALYSIS_TAB ? (
        <PyqAnalysisPanel />
      ) : (
        <div className="flex flex-col gap-3">
          {activeResults.length === 0 && (
            <div className="glass-panel rounded-xl p-10 text-center text-on-surface-variant text-sm">
              No results found for this category. Try different keywords or check the subject code.
            </div>
          )}

          {activeResults.map((item, i) => (
            <a
              key={i}
              href={item.href}
              target="_blank"
              rel="noopener noreferrer"
              className="glass-panel rounded-xl p-5 flex items-start justify-between gap-4
                         border-t border-white/5 hover:border-info/40 transition-colors group"
            >
              <div className="min-w-0">
                <p className="font-medium text-on-surface truncate group-hover:text-primary transition-colors">
                  {item.title}
                </p>
                <p className="text-sm text-on-surface-variant line-clamp-2 mt-1 leading-relaxed">
                  {item.body}
                </p>
              </div>
              <span className={`shrink-0 text-xs font-semibold px-2.5 py-1 rounded-full ${scoreBadge(item.score)}`}>
                {item.score}
              </span>
            </a>
          ))}
        </div>
      )}
    </div>
  )
}

export default Results