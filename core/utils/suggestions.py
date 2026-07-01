"""
Rule-based suggestion generation. Deliberately not LLM-generated, so
output is explainable, deterministic, and free of hallucination risk.
"""


def generate_suggestions(missing_skills, similarity_score, ats_score, ats_issues):
    suggestions = []

    if missing_skills:
        top_missing = missing_skills[:8]
        suggestions.append(
            "Consider adding or highlighting these skills if you have them: "
            + ", ".join(top_missing) + "."
        )

    if similarity_score < 40:
        suggestions.append(
            "Your resume's overall content has low overlap with this job description. "
            "Try mirroring key terms and responsibilities from the posting where they "
            "genuinely apply to your experience."
        )
    elif similarity_score < 70:
        suggestions.append(
            "There's moderate alignment with the job description — tailoring a few "
            "bullet points to match its language could improve your match score."
        )

    if ats_score < 70:
        suggestions.append(
            "Your resume may have ATS parsing issues. See the ATS issues list below "
            "and consider simplifying formatting (avoid tables, columns, and images)."
        )

    suggestions.extend(ats_issues)

    if not suggestions:
        suggestions.append("Strong match! Your resume aligns well with this job description.")

    return suggestions
