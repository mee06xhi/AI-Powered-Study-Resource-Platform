"""
Study Planner - core logic.

Given a subject, exam date, and days available, asks Gemini to produce a
day-by-day study plan. Optionally takes PYQ topic data (from
question_mining.py) so the plan can prioritize high-frequency topics
instead of guessing blind.
"""

import json
import os

from google import genai
from dotenv import load_dotenv

load_dotenv()
_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-3.1-flash-lite"

PLAN_PROMPT_TEMPLATE = """You are creating a day-by-day exam study plan.

Subject: {subject}
Days available before the exam: {days_available}
{topics_block}
Return ONLY a JSON object (no markdown fences, no commentary) with this exact shape:
{{
  "days": [
    {{"day": 1, "focus": "short focus title", "tasks": ["task 1", "task 2"]}}
  ]
}}

Rules:
- Produce exactly {days_available} day entries, numbered 1 to {days_available}.
- If repeated-topic data is given above, prioritize higher-frequency topics
  earlier, and dedicate the final 1-2 days to revision/PYQ practice.
- If no topic data is given, structure the plan around a sensible generic
  module-by-module breakdown for the subject.
- Keep each "tasks" list to 2-4 short, concrete items.
"""


def _build_topics_block(topics: list[dict] | None) -> str:
    if not topics:
        return "No repeated-question topic data available - plan generically.\n"
    lines = ["Repeated-question topics found in past papers (highest priority first):"]
    for t in topics:
        lines.append(f"- {t['topic']} (appeared {t['frequency']} times, {t['percentage']}%)")
    return "\n".join(lines) + "\n"


def generate_study_plan(
    subject: str,
    days_available: int,
    exam_date: str | None = None,
    topics: list[dict] | None = None,
) -> dict:
    """Ask Gemini for a day-by-day plan. Returns {subject, exam_date, days}."""
    prompt = PLAN_PROMPT_TEMPLATE.format(
        subject=subject,
        days_available=days_available,
        topics_block=_build_topics_block(topics),
    )

    response = _client.models.generate_content(model=MODEL, contents=prompt)

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    parsed = json.loads(raw)

    return {
        "subject": subject,
        "exam_date": exam_date,
        "days": parsed["days"],
    }


# Documentation-style schema (mirrors MINE_QUESTIONS_TOOL_SCHEMA in question_mining.py).
GENERATE_STUDY_PLAN_TOOL_SCHEMA = {
    "name": "generate_study_plan",
    "description": (
        "Create a day-by-day exam study plan for a subject, given how many "
        "days are available before the exam. Uses repeated PYQ topic data "
        "if available to prioritize high-frequency topics."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "subject": {"type": "string"},
            "days_available": {"type": "integer"},
            "exam_date": {"type": "string", "description": "Optional, e.g. '2026-10-05'."},
        },
        "required": ["subject", "days_available"],
    },
}