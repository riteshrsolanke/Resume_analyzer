"""
Rule-based ATS (Applicant Tracking System) compatibility checker.
This does NOT use ML - it's a deterministic rubric, since ATS parsing
issues are structural/textual, not semantic.
"""
import re

SECTION_HEADERS = [
    'experience', 'work experience', 'employment history',
    'education', 'skills', 'projects', 'certifications', 'summary',
]

EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_RE = re.compile(r'(\+?\d[\d\-\s().]{8,}\d)')


def check_ats_compatibility(text, page_count=1):
    """
    Returns (score 0-100, list_of_issue_strings) based on a simple rubric.
    Each check is worth a fixed number of points; deduct when failed.
    """
    issues = []
    score = 100
    lower = (text or '').lower()

    # 1. Standard section headers present (15 pts)
    found_sections = [h for h in SECTION_HEADERS if h in lower]
    if len(found_sections) < 3:
        score -= 15
        issues.append(
            "Resume is missing common section headers (e.g. Experience, "
            "Education, Skills). ATS systems rely on these to categorize content."
        )

    # 2. Contact info detectable (15 pts)
    if not EMAIL_RE.search(text or ''):
        score -= 10
        issues.append("No email address detected — make sure it's plain text, not an image.")
    if not PHONE_RE.search(text or ''):
        score -= 5
        issues.append("No phone number detected in plain text.")

    # 3. Text density / extraction sanity (20 pts)
    word_count = len((text or '').split())
    if word_count < 150:
        score -= 20
        issues.append(
            "Very little text was extracted from the PDF. This often means the "
            "resume uses images, columns, or text boxes that ATS parsers can't read."
        )
    elif word_count > 1200:
        score -= 5
        issues.append("Resume text is unusually long; consider trimming to 1-2 pages.")

    # 4. Page count (10 pts)
    if page_count and page_count > 2:
        score -= 10
        issues.append("Resume is longer than 2 pages — ATS and recruiters often favor 1-2 pages.")

    # 5. Special characters / bullet symbols that sometimes break parsers (10 pts)
    weird_chars = re.findall(r'[^\x00-\x7F]', text or '')
    if len(weird_chars) > 30:
        score -= 10
        issues.append(
            "Resume contains many non-standard characters or symbols (e.g. decorative "
            "bullets, icons), which can confuse some ATS parsers."
        )

    # 6. Repeated whitespace / garbled extraction (10 pts) — proxy for tables/columns
    if text:
        lines = [l for l in text.split('\n') if l.strip()]
        very_short_lines = sum(1 for l in lines if len(l.strip()) <= 2)
        if lines and (very_short_lines / len(lines)) > 0.3:
            score -= 10
            issues.append(
                "Many very short lines were detected after extraction — this often "
                "indicates a multi-column layout or table that ATS systems misread."
            )

    # 7. Contains a dedicated Skills section explicitly (10 pts)
    if 'skill' not in lower:
        score -= 10
        issues.append("No explicit 'Skills' section found — add one to help keyword matching.")

    score = max(0, min(100, score))
    return round(score, 2), issues
