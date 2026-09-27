"""
Pydantic models describing the shapes of data this API sends and receives.

Keeping these separate from main.py (the routes) and search_engine.py (the
logic) means the "what does this data look like" definition lives in one
place, and both other files can import it.
"""

from pydantic import BaseModel


class ResourceItem(BaseModel):
    """One search result — e.g. one link to a syllabus PDF, one YouTube video, etc."""
    title: str
    href: str
    body: str
    score: int


class SearchResponse(BaseModel):
    """The full shape of what GET /search returns."""
    department: str
    semester: str
    subject: str
    subject_code: str
    # keys are resource types ("syllabus", "notes", ...), values are ranked lists
    results: dict[str, list[ResourceItem]]


class PYQTopic(BaseModel):
    """One row of the repeated-question frequency table."""
    topic: str
    frequency: int
    percentage: int
    sample_question: str


class PYQAnalysisResponse(BaseModel):
    """The full shape of what GET /analyze-pyq returns."""
    total_questions_found: int
    topics: list[PYQTopic]
    # which .txt files on disk were combined to produce this analysis,
    source_files: list[str]

class AgentRequest(BaseModel):
    message: str

class AgentResponse(BaseModel):
    answer: str
    tool_used: str | None = None
    tool_result: dict | None = None

class StudyDay(BaseModel):
    day: int
    focus: str
    tasks: list[str]

class StudyPlanRequest(BaseModel):
    subject: str
    days_available: int
    exam_date: str | None = None

class StudyPlanResponse(BaseModel):
    subject: str
    exam_date: str | None
    days: list[StudyDay]