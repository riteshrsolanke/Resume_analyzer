"""
Resume <-> job description similarity scoring using TF-IDF + cosine similarity.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .skill_extractor import clean_text


def compute_similarity_score(resume_text, jd_text):
    """
    Returns a 0-100 similarity score between resume text and job description
    text based on TF-IDF cosine similarity.
    """
    resume_text = clean_text(resume_text)
    jd_text = clean_text(jd_text)

    if not resume_text or not jd_text:
        return 0.0

    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
    except ValueError:
        # e.g. both texts are entirely stop words / empty vocabulary
        return 0.0

    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(score) * 100, 2)


def compute_skill_overlap_score(matched_skills, required_skills):
    """
    Returns a 0-100 score representing the proportion of job-description
    skills that are present in the resume.
    """
    if not required_skills:
        return 0.0
    overlap = len(set(matched_skills) & set(required_skills))
    return round((overlap / len(required_skills)) * 100, 2)


def compute_overall_score(similarity_score, skill_overlap_score, ats_score,
                           weights=(0.4, 0.4, 0.2)):
    """
    Blend the three signals into one overall score (0-100).
    Default weighting: 40% semantic similarity, 40% skill overlap, 20% ATS friendliness.
    """
    w_sim, w_skill, w_ats = weights
    overall = (similarity_score * w_sim) + (skill_overlap_score * w_skill) + (ats_score * w_ats)
    return round(overall, 2)
