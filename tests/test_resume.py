from __future__ import annotations

from backend.api.ai import ResumeScoreRequest
from backend.services.resume_builder import _parse_bullets


def test_parse_bullets_json_input():
    raw = '["Implemented a caching layer reducing API latency by 35 percent across core endpoints."]'
    out = _parse_bullets(raw)
    assert len(out) == 1


def test_parse_bullets_fallback_lines():
    raw = "- Built scalable auth service with JWT rotation and cookie support"
    out = _parse_bullets(raw)
    assert len(out) == 1


def test_parse_bullets_length_filtering():
    raw = '["short", "' + ('a' * 230) + '", "Implemented robust logging and rate limiting for production APIs."]'
    out = _parse_bullets(raw)
    assert len(out) == 1


def test_parse_bullets_empty():
    assert _parse_bullets("") == []


def test_resume_score_request_model():
    req = ResumeScoreRequest(resume_text="A", job_description="B")
    assert req.resume_text == "A"
    assert req.job_description == "B"
