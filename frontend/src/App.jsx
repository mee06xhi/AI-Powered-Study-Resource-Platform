//frontend's central controller

import { useState, useEffect } from "react"
import Navbar from "./components/Navbar"
import Home from "./pages/Home"
import Results from "./pages/Results"
import { searchResources } from "./api"
import AgentChat from "./pages/AgentChat"
import StudyPlanner from "./pages/StudyPlanner"

function App() {
  const [view, setView] = useState("home") // "home" | "results" | "agent"
  const [searchData, setSearchData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [mousePos, setMousePos] = useState({ x: "50vw", y: "50vh" })

  useEffect(() => {
    function handleMouseMove(e) {
      setMousePos({ x: `${e.clientX}px`, y: `${e.clientY}px` })
    }
    window.addEventListener("mousemove", handleMouseMove)
    return () => window.removeEventListener("mousemove", handleMouseMove)
  }, [])

  async function handleSearch(formValues) {
    setLoading(true)
    setError(null)
    try {
      const data = await searchResources(formValues)
      setSearchData(data)
      setView("results")
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function handleBack() {
    setView("home")
    setSearchData(null)
    setError(null)
  }

  function goToAgent() {
  setView("agent")
  }

  function goToPlanner() {
  setView("planner")
}

  return (
    <div className="grid-texture min-h-screen flex flex-col relative">
      {/* radial violet glow that follows the cursor, matches the reference */}
      <div
        className="fixed inset-0 -z-10 pointer-events-none transition-colors duration-300"
        style={{
          background: `radial-gradient(circle 800px at ${mousePos.x} ${mousePos.y}, rgba(91,33,182,0.25), transparent 70%)`,
        }}
      />

      <Navbar 
        onAskAgent={goToAgent}
        onOpenPlanner={goToPlanner}
      />

      <main className="flex-grow">
        {view === "home" && <Home onSearch={handleSearch} loading={loading} error={error} />}
        {view === "results" && searchData && <Results data={searchData} onBack={handleBack} />}
        {view === "agent" && <AgentChat onBack={handleBack} />}
        {view === "planner" && <StudyPlanner onBack={handleBack} />}
      </main>
    </div>
  )
}

export default App