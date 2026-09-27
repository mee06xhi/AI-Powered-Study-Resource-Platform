"""
Question Mining + Resource Search - wrapped as Gemini-callable tools.

Each tool here is a thin wrapper around functions that already exist
elsewhere (question_mining.py, search_engine.py, pyq_data.py). The wrapper
just adapts arguments to what makes sense for an LLM to provide - e.g.
Gemini never sees raw PYQ text, it just asks for analysis and we load
the text ourselves.
"""

from google.genai import types

from app.pyq_data import load_pyq_text
from app.question_mining import mine_questions
from app.search_engine import search_all_resources
from app.study_planner import generate_study_plan

import inspect


def analyze_pyq_tool(threshold: float = 0.3, top_keywords: int = 3) -> dict:
    """Tool: analyze bundled previous-year papers, return repeated topics."""
    raw_text, source_files = load_pyq_text()
    if not raw_text.strip():
        return {"error": "No PYQ data available."}
    result = mine_questions(raw_text, threshold=threshold, top_keywords=top_keywords)
    result["source_files"] = source_files
    return result

def generate_study_plan_tool(subject: str, days_available: int, exam_date: str = None) -> dict:
    """Tool: build a day-by-day study plan, using PYQ topic frequency if available."""
    raw_text, _ = load_pyq_text()
    topics = mine_questions(raw_text)["topics"] if raw_text.strip() else None
    return generate_study_plan(
        subject=subject, days_available=days_available, exam_date=exam_date, topics=topics
    )


def search_resources_tool(subject: str, subject_code: str, department: str = "CSE", semester: str = "") -> dict:
    """Tool: search the web for study resources for one subject."""
    return search_all_resources(
        department=department,
        semester=semester,
        subject=subject,
        subject_code=subject_code,
        max_results=5,
    )


# name Gemini uses -> actual Python function that runs
TOOL_FUNCTIONS = {
    "analyze_pyq": analyze_pyq_tool,
    "search_resources": search_resources_tool,
    "generate_study_plan": generate_study_plan_tool,
}

# Gemini-facing descriptions. Gemini reads ONLY this - never the Python
# code above - to decide which tool fits the user's request.
TOOL_DECLARATIONS = [
    types.FunctionDeclaration(
        name="analyze_pyq",
        description=(
            "Analyze previous-year VTU question papers and return the most "
            "repeated topics with frequency counts and sample questions. "
            "Use this when the user asks about repeated questions, "
            "important topics, what to focus on for exam prep, or PYQ trends."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {
                "threshold": {
                    "type": "number",
                    "description": "Similarity threshold 0-1. Default 0.3."
                },
                "top_keywords": {
                    "type": "integer",
                    "description": "Keywords per topic label. Default 3."
                },
            },
            "additionalProperties": False,
        },
    ),

    types.FunctionDeclaration(
        name="search_resources",
        description=(
            "Search the web for study resources - syllabus, notes, previous "
            "year papers, lab manuals, reference books, YouTube lectures, "
            "and NPTEL courses - for a specific VTU subject. Use this when "
            "the user asks to find, search for, or get links/material for a subject."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "Subject name, e.g. 'Database Management Systems'"
                },
                "subject_code": {
                    "type": "string",
                    "description": "VTU subject code, e.g. 'BCS403'"
                },
                "department": {
                    "type": "string",
                    "description": "Department, e.g. 'CSE'. Default CSE if unspecified."
                },
                "semester": {
                    "type": "string",
                    "description": "Semester number, e.g. '4'"
                },
            },
            "required": ["subject", "subject_code"],
            "additionalProperties": False,
        },
    ),

    types.FunctionDeclaration(
        name="generate_study_plan",
        description=(
            "Create a day-by-day exam study plan for a subject, given how many "
            "days are available before the exam. Automatically factors in repeated "
            "PYQ topics when available. Use this when the user asks for a study plan, "
            "revision schedule, or how to organize their remaining prep days."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "Subject name, e.g. 'Database Management Systems'"
                },
                "days_available": {
                    "type": "integer",
                    "description": "Days available before the exam."
                },
                "exam_date": {
                    "type": "string",
                    "description": "Exam date if known, e.g. '2026-10-05'. Optional."
                },
            },
            "required": ["subject", "days_available"],
            "additionalProperties": False,
        },
    ),
]

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-3.1-flash-lite"

SYSTEM_INSTRUCTION = (
    "You are the VTU SmartPrep assistant. You help students find study "
    "resources and understand which exam topics repeat most often. "
    "Use the available tools whenever the user's request matches what a "
    "tool does. If no tool is relevant, just answer directly. "
    "When you get a tool result, summarize it clearly for the student - "
    "don't just dump the raw data."
)


def run_agent(user_message: str) -> dict:
    """
    One full agent turn:
      1. Send the message + tool descriptions to Gemini
      2. If Gemini requests a tool call, actually run it
      3. Send the real result back to Gemini
      4. Return Gemini's final natural-language answer
    """
    tools = [types.Tool(function_declarations=TOOL_DECLARATIONS)]
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        tools=tools,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    contents = [types.Content(role="user", parts=[types.Part.from_text(text=user_message)])]
    response = _client.models.generate_content(model=MODEL, contents=contents, config=config)

    if not response.function_calls:
        return {"answer": response.text, "tool_used": None, "tool_result": None}

    call = response.function_calls[0]
    tool_fn = TOOL_FUNCTIONS.get(call.name)
    if tool_fn is None:
        return {"answer": f"Unknown tool requested: {call.name}", "tool_used": None, "tool_result": None}

    # Gemini can still hand back arguments the tool doesn't accept (e.g. a
    # stray "subject" because the message mentioned a subject name). Never
    # trust model output blindly - filter to only what the function declares.
    accepted_params = set(inspect.signature(tool_fn).parameters)
    safe_args = {k: v for k, v in (call.args or {}).items() if k in accepted_params}

    tool_result = tool_fn(**safe_args)

    # Feed the model's function-call turn + our real result back in, so the
    # final answer is grounded in actual data, not a guess.
    contents.append(response.candidates[0].content)
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_function_response(name=call.name, response=tool_result)],
        )
    )

    final_response = _client.models.generate_content(model=MODEL, contents=contents, config=config)

    return {"answer": final_response.text, "tool_used": call.name, "tool_result": tool_result}