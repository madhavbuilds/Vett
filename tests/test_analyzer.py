"""Tests for AI response normalization."""

from vett.analyzer import _sanitize_ai_result


def test_sanitize_coerces_suggestions_and_score():
    raw = {
        "project_summary": "  ok  ",
        "overall_score": "88",
        "grade": " B ",
        "strengths": [None, " x "],
        "critical_issues": "not a list",
        "suggestions": [
            {"title": "", "detail": "d1"},
            "plain text",
            {"unexpected": 1},
        ],
        "estimated_tech_debt": "Low",
        "one_line_roast": None,
    }
    out = _sanitize_ai_result(raw)
    assert out["overall_score"] == 88
    assert out["grade"] == "B"
    assert out["strengths"] == ["x"]
    assert out["critical_issues"] == []
    assert out["project_summary"] == "ok"
    assert len(out["suggestions"]) == 3
    assert out["suggestions"][0]["title"] == "Suggestion"
    assert out["suggestions"][1] == {"title": "Suggestion", "detail": "plain text"}
    assert out["suggestions"][2]["title"] == "Suggestion"


def test_sanitize_rejects_non_object():
    out = _sanitize_ai_result([])
    assert "non-object" in out["critical_issues"][0]
