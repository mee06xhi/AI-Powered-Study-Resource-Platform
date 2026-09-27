"""
Core search + ranking logic for VTU SmartPrep.

This module has NO knowledge of FastAPI, HTTP, or JSON responses.
It just takes plain Python arguments in, and returns plain Python
data structures (lists of dicts) out. That keeps it easy to test
on its own, and easy to reuse if the API layer ever changes.
"""

from ddgs import DDGS

TRUSTED_DOMAINS = [
    "vtu.ac.in",
    "nptel.ac.in",
    "youtube.com",
    "vtucircle.com",
    "vtusync.in",
    "vtuease.in",
    "vturesource.com",
    "vtunotes.org",
    "vtuwise.in",
    "vtuadda.com",
    "vtuquestionpapers.in",
    "vtubuddy.in",
    "azdocuments.in",
]

LOW_PRIORITY_DOMAINS = [
    "scribd.com",
    "studocu.com",
    "slideshare.net",
]

RESOURCE_TYPES = [
    "syllabus",
    "previous year question papers",
    "notes",
    "lab manual",
    "reference books",
    "youtube lectures",
    "nptel course",
]


# Walks through the TRUSTED_DOMAINS list in order and returns a score based on the first match.
def domain_score(url: str) -> int:
    """Higher score = more trusted. 0 = unknown/neutral. -1 = low priority."""
    for i, domain in enumerate(TRUSTED_DOMAINS):
        if domain in url:
            return len(TRUSTED_DOMAINS) - i
    for domain in LOW_PRIORITY_DOMAINS:
        if domain in url:
            return -1
    return 0


def rank_results(results: list[dict]) -> list[dict]:
    """Attach a trust score to each result and sort highest-first."""
    for r in results:
        r["score"] = domain_score(r["href"])
    return sorted(results, key=lambda r: r["score"], reverse=True)


def search_resource(
    department: str,
    semester: str,
    subject: str,
    subject_code: str,
    resource_type: str,
    max_results: int = 5,
) -> list[dict]:
    """Search DuckDuckGo for one resource type and return raw (unranked) results."""
    if resource_type == "reference books":
        query = f"{subject} textbook author VTU {subject_code}"
    elif resource_type == "nptel course":
        query = f"{subject} site:nptel.ac.in"
    else:
        query = f"{subject} {subject_code} VTU {resource_type}"

    try:
        results = DDGS().text(query, max_results=max_results)
        return results
    except Exception as e:
        print(f"  -> Search failed for '{query}': {e}")
        return []


def search_all_resources(
    department: str,
    semester: str,
    subject: str,
    subject_code: str,
    max_results: int = 5,
) -> dict[str, list[dict]]:
    """Search + rank every resource type for one subject. This is the function
    the API layer will call directly."""
    ranked_results = {}
    for resource_type in RESOURCE_TYPES:
        raw = search_resource(
            department, semester, subject, subject_code, resource_type, max_results
        )
        ranked_results[resource_type] = rank_results(raw)
    return ranked_results
