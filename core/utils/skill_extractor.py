"""
Skill extraction via spaCy's PhraseMatcher against a curated taxonomy.
The spaCy model is loaded once at module import time (singleton pattern)
since loading it is relatively expensive.
"""
import re
import spacy
from spacy.matcher import PhraseMatcher

from .skills_data import ALL_SKILLS

_NLP = None
_MATCHER = None


def _get_nlp():
    """Lazily load and cache the spaCy pipeline."""
    global _NLP, _MATCHER
    if _NLP is None:
        try:
            _NLP = spacy.load('en_core_web_sm')
        except OSError:
            # Model not downloaded yet -> fall back to a blank tokenizer-only pipeline.
            # Run: python -m spacy download en_core_web_sm
            _NLP = spacy.blank('en')
        _MATCHER = PhraseMatcher(_NLP.vocab, attr='LOWER')
        patterns = [_NLP.make_doc(skill) for skill in ALL_SKILLS]
        _MATCHER.add('SKILLS', patterns)
    return _NLP, _MATCHER


def extract_skills(text):
    """
    Return a sorted list of unique skills (lowercase, as they appear in
    the taxonomy) found in the given text.
    """
    if not text or not text.strip():
        return []

    nlp, matcher = _get_nlp()
    doc = nlp(text)
    matches = matcher(doc)

    found = set()
    for match_id, start, end in matches:
        span_text = doc[start:end].text.lower().strip()
        found.add(span_text)

    return sorted(found)


def clean_text(text):
    """Light normalization used before similarity scoring."""
    text = re.sub(r'\s+', ' ', text or '')
    return text.strip()
