const API_BASE = "http://127.0.0.1:8000"

export async function searchResources({ department, semester, subject, subjectCode, maxResults }) {
  const params = new URLSearchParams({
    department,
    semester,
    subject,
    subject_code: subjectCode,
    max_results: maxResults,
  })

  const response = await fetch(`${API_BASE}/search?${params.toString()}`)

  if (!response.ok) {
    throw new Error(`Search failed (${response.status})`)
  }

  return response.json()
}

export async function analyzePyq({ threshold, topKeywords } = {}) {
  const params = new URLSearchParams()
  if (threshold !== undefined) params.set("threshold", threshold)
  if (topKeywords !== undefined) params.set("top_keywords", topKeywords)

  const query = params.toString()
  const response = await fetch(`${API_BASE}/analyze-pyq${query ? `?${query}` : ""}`)

  if (!response.ok) {
    const detail = await response.json().catch(() => null)
    throw new Error(detail?.detail || `PYQ analysis failed (${response.status})`)
  }

  return response.json()
}

export async function askAgent(message) {
  const response = await fetch(`${API_BASE}/agent`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  })

  if (!response.ok) {
    const detail = await response.json().catch(() => null)
    throw new Error(detail?.detail || `Agent request failed (${response.status})`)
  }

  return response.json()
}

export async function generateStudyPlan({ subject, daysAvailable, examDate }) {
  const response = await fetch(`${API_BASE}/study-plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      subject,
      days_available: daysAvailable,
      exam_date: examDate || null,
    }),
  })

  if (!response.ok) {
    const detail = await response.json().catch(() => null)
    throw new Error(detail?.detail || `Study plan failed (${response.status})`)
  }

  return response.json()
}