"""
Entry point for the backend.

Run this with:
    python -m uvicorn app.main:app --reload

Then open http://127.0.0.1:8000/docs in a browser — FastAPI auto-generates
an interactive page there where you can try endpoints without writing any
frontend code.
"""

from app.pyq_data import load_pyq_text

from fastapi import FastAPI
from app.search_engine import search_all_resources
from app.question_mining import mine_questions
from app.models import SearchResponse, PYQAnalysisResponse, AgentRequest, AgentResponse
from app.agent import run_agent
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Query
from app.study_planner import generate_study_plan
from app.models import StudyPlanRequest, StudyPlanResponse
from app.question_mining import mine_questions

app = FastAPI(title="VTU SmartPrep API")

app.add_middleware(
    #Cross-Origin Resource Sharing. Security system used by web browsers to let a web page ask for data from a different domain, website, or server.
    CORSMiddleware,
    allow_origins=[
        # React dev server and fast api docs are on different ports, so we need to allow both for local development. 
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",    
    ],
    # Allow requests using any HTTP method- get, put, post, delete etc.
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Just confirms the server is alive/ Health check"""
    return {"message": "VTU SmartPrep API is running"}


@app.get("/hello/{name}")
def hello(name: str):
    """An example of a path parameter."""
    return {"greeting": f"Hello, {name}!"}


#Real endpoint
@app.get("/search", response_model=SearchResponse)      #"Create a GET API endpoint at /search."
def search(
    # Parameters frontend needs to provide.
    # ... means the parameter is required.
    department: str = Query(..., min_length=1, description="e.g. CSE"),
    semester: str = Query(..., min_length=1, description="e.g. 4"),
    subject: str = Query(..., min_length=1, description="e.g. Database Management Systems"),
    subject_code: str = Query(..., min_length=1, description="e.g. BCS403"),
    max_results: int = Query(5, ge=1, le=10, description="Results per resource type (1-10)"),
):
    """
    Search for every resource type (syllabus, PYQs, notes, lab manual,
    reference books, YouTube lectures, NPTEL course) for one subject,
    ranked by domain trust.

    """
    try:
        results = search_all_resources(
            department=department,
            semester=semester,
            subject=subject,
            subject_code=subject_code,
            max_results=max_results,
        )
    except Exception as e:
        # search_resource() already catches per-resource-type failures and
        # returns []. This outer catch is a safety net for anything truly
        raise HTTPException(
            status_code=502,
            detail=f"Search failed unexpectedly: {e}",
        )

    # Pydantic model that handles data validation
    return SearchResponse(
        department=department,
        semester=semester,
        subject=subject,
        subject_code=subject_code,
        results=results,
    )


@app.get("/analyze-pyq", response_model=PYQAnalysisResponse)
def analyze_pyq(
    # To check whether two questions are similar enough to be considered the same topic/question
    threshold: float = Query(0.3, ge=0.0, le=1.0, description="Similarity threshold for clustering (0-1)"),
    top_keywords: int = Query(3, ge=1, le=10, description="Keywords per topic label"),
):
    """
    Analyze the bundled previous-year question papers and return a
    frequency table of repeated topics.

    """
    raw_text, source_files = load_pyq_text()

    if not raw_text.strip():
        raise HTTPException(
            status_code=404,
            detail=(
                "No PYQ data found."
            ),
        )

    try:
        result = mine_questions(raw_text, threshold=threshold, top_keywords=top_keywords)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"PYQ analysis failed unexpectedly: {e}",
        )

    return PYQAnalysisResponse(
        total_questions_found=result["total_questions_found"],
        topics=result["topics"],
        source_files=source_files,
    )

@app.post("/study-plan", response_model=StudyPlanResponse)
def study_plan(request: StudyPlanRequest):
    """Generate a day-by-day study plan, using PYQ topic frequency as a
    prioritization signal when it's available."""
    raw_text, _ = load_pyq_text()
    topics = None
    if raw_text.strip():
        topics = mine_questions(raw_text)["topics"]

    try:
        result = generate_study_plan(
            subject=request.subject,
            days_available=request.days_available,
            exam_date=request.exam_date,
            topics=topics,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Study plan generation failed: {e}")

    return StudyPlanResponse(**result)

@app.post("/agent", response_model=AgentResponse)
def agent_chat(request: AgentRequest):
    """Single-turn chat backed by the Gemini agent - decides whether to
    call analyze_pyq, search_resources, or just answer directly."""
    try:
        result = run_agent(request.message)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Agent failed unexpectedly: {e}")
    return AgentResponse(**result)
    # run_agent returns a dict. ** unpacks the dict.