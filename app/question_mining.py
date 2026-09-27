"""
Question Mining Agent - core logic.

Same philosophy as search_engine.py: plain Python in, plain Python out.
No FastAPI, no HTTP - just text processing, so it's easy to test on its own.
"""

import re

from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity

# Matches the START of a new question, e.g.:
#   "1 a."   "1a."   "b."   "2. a)"   "6. a)"   "Q1."
# The number and the letter can be separated by ". " or nothing at all -
# real papers are inconsistent about this, so we allow both.
QUESTION_START_RE = re.compile(
    r"^\s*(?:Q?\.?\s*\d+\s*[\.\)]?\s*)?[a-eA-E]\s*[\.\)]\s+"
)

# Lines that are just structural noise - not part of any question's text.
# e.g. "OR", "Module 2", "MODULE-3", "Module 4:"
NOISE_LINE_RE = re.compile(
    r"^\s*(?:OR|Module[\s\-]*\d+:?)\s*$",
    re.IGNORECASE,
)

# Matches a trailing marks annotation, e.g. "(10 Marks)", "(10M)", "[05]"
MARKS_RE = re.compile(
    r"[\(\[]\s*\d{1,2}\s*(?:marks?|m)?\s*[\)\]]\s*$",
    re.IGNORECASE,
)

# Exam "command words" that are common across nearly every question but say
# nothing about the topic - left in, they'd pollute keyword labels because
# they can be rare enough *relative to the topic words* to score high in
COMMAND_WORDS = {
    "explain", "discuss", "draw", "describe", "define", "write", "mention",
    "differentiate", "illustrate", "state", "give", "derive", "comment",
    "justify", "outline", "list", "example", "examples", "suitable", "brief",
    "briefly", "note", "notes",
}
STOP_WORDS = list(ENGLISH_STOP_WORDS.union(COMMAND_WORDS))

# Smart quotes / dashes that show up when text is copy-pasted from PDFs or
# Word docs. Normalizing these to plain ASCII keeps downstream regexes
# (MARKS_RE etc.) matching reliably instead of silently failing on a
# lookalike character.
_QUOTE_MAP = str.maketrans({
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-",
})


def clean_text(raw_text: str) -> str:
    """
    Light sanitizer for pasted question-paper text. This is NOT an OCR or
    PDF-extraction fixer - it deliberately does nothing clever with layout.
    It only normalizes things that are safe regardless of source:

    - Smart quotes/dashes -> plain ASCII, so MARKS_RE and friends still match.
    - Stray non-printable characters get dropped.
    - Repeated spaces/tabs (not newlines - line breaks still matter for
      question segmentation) get collapsed.

    NOTE: this intentionally does NOT try to re-infer line breaks from
    flattened/table-like text (e.g. "|" used as a column separator). That
    class of problem belongs to PDF extraction quality, not this cleanup
    step - fix it at the source (better copy-paste / proper OCR) rather
    than guessing here.
    """
    text = raw_text.translate(_QUOTE_MAP)
    # Drop non-printable / control characters (keep normal whitespace).
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E]", "", text)
    # Collapse runs of spaces/tabs (but not newlines) into a single space.
    text = re.sub(r"[ \t]+", " ", text)
    return text


def extract_questions(raw_text: str) -> list[str]:
    """
    Take a raw block of pasted question-paper text and return a list of
    individual question strings, with marks annotations stripped.

    Lines that don't start a new question (continuation lines) get merged
    into the current question. Structural noise lines ("OR", "Module 2")
    are dropped entirely rather than merged.
    """
    raw_text = clean_text(raw_text)
    lines = raw_text.splitlines()
    questions: list[str] = []
    current: list[str] = []

    def flush():
        """Save the question we've been building, if there is one."""
        if current:
            text = " ".join(current).strip()
            text = MARKS_RE.sub("", text).strip()
            if text:
                questions.append(text)

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue
        if NOISE_LINE_RE.match(stripped):
            continue

        if QUESTION_START_RE.match(stripped):
            flush()  # save the previous question before starting a new one
            current = [QUESTION_START_RE.sub("", stripped)]
        else:
            # continuation of the current question (wrapped line)
            if current:
                current.append(stripped)

    flush()  # don't forget the last question in the file
    return questions


def _fit_and_group(questions: list[str], threshold: float):
    """
    Shared TF-IDF + union-find clustering step used by both cluster_questions()
    and build_frequency_table(), so the clustering logic lives in exactly one
    place instead of being duplicated.

    Returns (vectorizer, matrix, groups) where groups is a dict mapping an
    arbitrary group id -> list of question indices in that group.
    """
    vectorizer = TfidfVectorizer(stop_words=STOP_WORDS)
    matrix = vectorizer.fit_transform(questions)
    similarity = cosine_similarity(matrix)

    n = len(questions)
    parent = list(range(n))  # union-find: parent[i] = which group i currently points to

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        root_i, root_j = find(i), find(j)
        if root_i != root_j:
            parent[root_j] = root_i

    for i in range(n):
        for j in range(i + 1, n):
            if similarity[i][j] >= threshold:
                union(i, j)

    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)

    return vectorizer, matrix, groups


def cluster_questions(questions: list[str], threshold: float = 0.3) -> list[dict]:
    """
    Group similar questions together using TF-IDF + cosine similarity.

    Returns a list of clusters, each a dict with:
      - representative: the shortest question string among members (a full sentence)
      - members: all the original question strings in this cluster
      - frequency: how many questions fell into this cluster
    Sorted by frequency, highest first. Useful when you want the *actual wording*
    of a cluster, not just a keyword label (e.g. for later inspection/debugging).
    """
    if not questions:
        return []

    _, _, groups = _fit_and_group(questions, threshold)

    clusters = [
        {
            "representative": min((questions[i] for i in indices), key=len),
            "members": [questions[i] for i in indices],
            "frequency": len(indices),
        }
        for indices in groups.values()
    ]
    clusters.sort(key=lambda c: c["frequency"], reverse=True)
    return clusters


def build_frequency_table(questions: list[str], threshold: float = 0.3, top_keywords: int = 3) -> list[dict]:
    """
    Full pipeline: cluster similar questions, then label each cluster with
    short topic keywords (instead of a full sentence) and a frequency count.
    This is the "Question | Frequency" table the rest of the app will use
    (heat map, prediction agent, etc.).

    Returns a list of dicts sorted by frequency (highest first):
      - topic: short keyword-based label, e.g. "normalization, concept, 2nf"
      - frequency: how many times this topic appeared
      - percentage: frequency as % of total questions (rounded)
      - sample_question: one real question from this cluster, for context
    """
    if not questions:
        return []

    vectorizer, matrix, groups = _fit_and_group(questions, threshold)
    feature_names = vectorizer.get_feature_names_out()
    total = len(questions)

    table = []
    for indices in groups.values():
        # sum the TF-IDF row for every question in this cluster -> one combined
        # score per word, so words that matter across the whole cluster rise up
        combined_scores = sum(matrix[i] for i in indices).toarray().flatten()
        top_indices = combined_scores.argsort()[::-1][:top_keywords]
        keywords = [feature_names[i] for i in top_indices if combined_scores[i] > 0]

        members = [questions[i] for i in indices]
        table.append({
            "topic": ", ".join(keywords) if keywords else "misc",
            "frequency": len(members),
            "percentage": round(100 * len(members) / total),
            "sample_question": min(members, key=len),
        })

    table.sort(key=lambda row: row["frequency"], reverse=True)
    return table

def mine_questions(raw_text: str, threshold: float = 0.3, top_keywords: int = 3) -> dict:
    """
    The single entry point an LLM agent will call as a tool. Combines
    extraction + frequency-table building into one call, and returns a
    plain dict (JSON-serializable) - no custom objects, so it can be
    handed straight back to an LLM as a tool result.
    """
    questions = extract_questions(raw_text)
    table = build_frequency_table(questions, threshold=threshold, top_keywords=top_keywords)
    return {
        "total_questions_found": len(questions),
        "topics": table,
    }


# Schema describing mine_questions() in Gemini's function-calling format.
# This is what gets passed to the Gemini API alongside the prompt, so the
# model knows this tool exists, what it does, and what arguments to send.
MINE_QUESTIONS_TOOL_SCHEMA = {
    "name": "mine_questions",
    "description": (
        "Extracts individual exam questions from raw previous-year question "
        "paper text, clusters questions that cover the same underlying topic "
        "even if worded differently, and returns each topic's frequency of "
        "appearance. Use this whenever the user provides or references "
        "previous-year question paper text and wants to know which topics "
        "are repeated or most frequently examined."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "raw_text": {
                "type": "string",
                "description": (
                    "The raw text of one or more question papers, pasted "
                    "together. Can include multiple years concatenated."
                ),
            },
        },
        "required": ["raw_text"],
    },
}