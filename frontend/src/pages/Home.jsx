import { useState } from "react"

const DEPARTMENTS = ["CSE", "ISE", "ECE", "EEE"]
const SEMESTERS = ["1", "2", "3", "4", "5", "6", "7", "8"]

const inputClass =
  "bg-surface-container border-b border-outline-variant text-on-surface px-4 py-3 rounded-t-md w-full text-sm " +
  "focus:outline-none focus:border-info focus:ring-1 focus:ring-info/40 transition-colors " +
  "placeholder:text-outline-variant appearance-none"

const labelClass = "text-xs font-semibold uppercase tracking-wider text-on-surface-variant"

function Home({ onSearch, loading, error }) {
  const [department, setDepartment] = useState("")
  const [semester, setSemester] = useState("")
  const [subject, setSubject] = useState("")
  const [subjectCode, setSubjectCode] = useState("")
  const [maxResults, setMaxResults] = useState(5)

  function handleSubmit(e) {
    e.preventDefault()
    onSearch({ department, semester, subject, subjectCode, maxResults })
  }

  return (
    <div className="relative">
      {/* Hero */}
      <section className="pt-24 pb-16 px-6 md:px-16 max-w-[1440px] mx-auto flex flex-col items-center text-center">
        <h1 className="font-display text-4xl md:text-5xl font-bold text-primary mb-6 max-w-3xl leading-tight">
          Your Engineering Journey,
          <br />
          Optimized by Intelligence.
        </h1>
        <p className="text-lg text-on-surface-variant max-w-2xl mb-14 leading-relaxed">
          The definitive source for VTU syllabus, notes, and previous year papers.
          Precision-engineered for academic focus.
        </p>

        {/* Glass search panel */}
        <form
          onSubmit={handleSubmit}
          className="glass-panel w-full max-w-3xl p-6 md:p-8 rounded-xl border-t-2 border-accent
                     shadow-[0_25px_50px_-12px_rgba(0,0,0,0.5)] relative z-10 flex flex-col gap-6 text-left"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex flex-col gap-2">
              <label className={labelClass}>Department</label>
              <select
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                required
                className={inputClass}
              >
                <option value="" disabled>Select Department</option>
                {DEPARTMENTS.map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>

            <div className="flex flex-col gap-2">
              <label className={labelClass}>Semester</label>
              <select
                value={semester}
                onChange={(e) => setSemester(e.target.value)}
                required
                className={inputClass}
              >
                <option value="" disabled>Select Semester</option>
                {SEMESTERS.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <label className={labelClass}>Subject</label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="e.g., Database Management Systems"
              required
              className={inputClass}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex flex-col gap-2">
              <label className={labelClass}>Subject Code</label>
              <input
                type="text"
                value={subjectCode}
                onChange={(e) => setSubjectCode(e.target.value)}
                placeholder="e.g., BCS403"
                required
                className={inputClass}
              />
            </div>

            <div className="flex flex-col gap-2">
              <label className={labelClass}>Max Results</label>
              <input
                type="number"
                min={1}
                max={10}
                value={maxResults}
                onChange={(e) => setMaxResults(Number(e.target.value))}
                className={inputClass}
              />
            </div>
          </div>

          {error && <p className="text-sm text-red-400">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="bg-accent hover:bg-accent-hover disabled:opacity-50 disabled:cursor-not-allowed
                       text-white font-semibold text-sm py-4 rounded-lg ai-glow transition-colors
                       flex items-center justify-center gap-2 mt-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="7" />
              <path strokeLinecap="round" d="M21 21l-4.3-4.3" />
            </svg>
            {loading ? "Searching…" : "Search Resources"}
          </button>
        </form>
      </section>

      {/* Value props */}
      <section className="py-20 px-6 md:px-16 max-w-[1440px] mx-auto border-t border-white/5">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              title: "Curated & Ranked",
              body: "Resources are algorithmically sorted based on domain trust and relevance to the current VTU scheme.",
            },
            {
              title: "All Resource Types",
              body: "Syllabus copies, notes, PYQs, lab manuals, reference books, and YouTube/NPTEL lectures — all in one place.",
            },
            {
              title: "Fast & Simple",
              body: "Find exact materials without the clutter of scattered forums or disorganized drive links.",
            },
          ].map((item) => (
            <div key={item.title} className="flex flex-col gap-3">
              <h3 className="font-display text-xl font-semibold text-primary">{item.title}</h3>
              <p className="text-on-surface-variant leading-relaxed">{item.body}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

export default Home