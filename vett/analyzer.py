import json
import urllib.parse
import urllib.request

import anthropic

DEFAULT_MODELS = {
    "anthropic": "claude-3-5-sonnet-latest",
    "openai": "gpt-4o-mini",
    "gemini": "gemini-1.5-flash",
    "openrouter": "openai/gpt-4o-mini",
}

ANTHROPIC_MODEL_FALLBACKS = [
    "claude-3-5-sonnet-latest",
]


def _build_prompt(files, security, todos, large, complex_fns):
    file_summary = "\n".join(
        f"- {f['path']} ({f['language']}, {f['lines']} lines)" for f in files[:20]
    )
    sample_files = sorted(files, key=lambda x: x["lines"], reverse=True)[:3]
    code_samples = ""
    for f in sample_files:
        snippet = "\n".join(f["content"].splitlines()[:60])
        code_samples += f"\n\n### {f['path']} ({f['language']})\n```\n{snippet}\n```"

    return f"""You are Vett, an expert AI code reviewer. Analyze this codebase and give a structured health report.

## Project Files
{file_summary}

## Pre-scanned Issues
- Security issues: {len(security)}
- TODO/FIXME comments: {len(todos)}
- Large files (>300 lines): {len(large)}
- Complex functions (>50 lines): {len(complex_fns)}

## Code Samples
{code_samples}

Respond ONLY with a valid JSON object:
{{
  "project_summary": "2-3 sentence description of what this project does",
  "overall_score": 72,
  "grade": "B",
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "critical_issues": ["issue 1", "issue 2"],
  "suggestions": [
    {{"title": "Suggestion title", "detail": "Detailed explanation"}},
    {{"title": "Suggestion title", "detail": "Detailed explanation"}}
  ],
  "estimated_tech_debt": "Low / Medium / High",
  "one_line_roast": "A funny but constructive one-liner about the codebase"
}}"""


def _extract_json(raw):
    raw = (raw or "").strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


def _fallback_error(message):
    return {
        "project_summary": "Could not complete AI analysis.",
        "overall_score": 0,
        "grade": "?",
        "strengths": [],
        "critical_issues": [message],
        "suggestions": [],
        "estimated_tech_debt": "Unknown",
        "one_line_roast": "",
    }


def _sanitize_ai_result(data):
    """Coerce parsed JSON into the shapes the CLI and reporter expect."""
    if not isinstance(data, dict):
        return _fallback_error("AI returned a non-object JSON payload.")
    out = dict(data)
    try:
        out["overall_score"] = int(out.get("overall_score", 0))
    except (TypeError, ValueError):
        out["overall_score"] = 0
    grade = out.get("grade")
    out["grade"] = str(grade).strip()[:8] if grade is not None else "?"

    for key in ("strengths", "critical_issues"):
        raw_list = out.get(key)
        if not isinstance(raw_list, list):
            out[key] = []
        else:
            out[key] = [str(x).strip() for x in raw_list if x is not None and str(x).strip()]

    raw_suggestions = out.get("suggestions")
    suggestions = []
    if isinstance(raw_suggestions, list):
        for item in raw_suggestions:
            if isinstance(item, dict):
                title = str(item.get("title") or "Suggestion").strip() or "Suggestion"
                detail = str(item.get("detail") or "").strip()
                suggestions.append({"title": title, "detail": detail})
            elif isinstance(item, str) and item.strip():
                suggestions.append({"title": "Suggestion", "detail": item.strip()})
    out["suggestions"] = suggestions

    for key in ("project_summary", "estimated_tech_debt", "one_line_roast"):
        val = out.get(key)
        out[key] = str(val).strip() if val is not None else ""

    return out


def _post_json(url, payload, headers):
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def _analyze_anthropic(prompt, api_key, model):
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _is_model_not_found_error(exc):
    msg = str(exc).lower()
    return "not_found_error" in msg or ("model" in msg and "not found" in msg)


def _analyze_openai_compatible(prompt, api_key, model, base_url):
    response = _post_json(
        f"{base_url.rstrip('/')}/chat/completions",
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        },
        {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    return response["choices"][0]["message"]["content"]


def _analyze_gemini(prompt, api_key, model):
    encoded_model = urllib.parse.quote(model, safe="")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{encoded_model}:generateContent?key={api_key}"
    )
    response = _post_json(
        url,
        {"contents": [{"parts": [{"text": prompt}]}]},
        {"Content-Type": "application/json"},
    )
    candidates = response.get("candidates", [])
    if not candidates:
        return ""
    parts = candidates[0].get("content", {}).get("parts", [])
    texts = [p.get("text", "") for p in parts if p.get("text")]
    return "\n".join(texts).strip()


def analyze_with_ai(files, security, todos, large, complex_fns, provider, api_key, model=None):
    provider = (provider or "anthropic").lower()
    explicit_model = bool(model)
    model = model or DEFAULT_MODELS.get(provider, DEFAULT_MODELS["anthropic"])
    prompt = _build_prompt(files, security, todos, large, complex_fns)
    try:
        if provider == "anthropic":
            try_models = [model]
            if not explicit_model:
                try_models.extend(m for m in ANTHROPIC_MODEL_FALLBACKS if m != model)

            last_exc = None
            raw = None
            for candidate_model in try_models:
                try:
                    raw = _analyze_anthropic(prompt, api_key, candidate_model)
                    break
                except Exception as exc:
                    last_exc = exc
                    if not _is_model_not_found_error(exc):
                        raise
            if raw is None and last_exc is not None:
                raise last_exc
        elif provider == "openai":
            raw = _analyze_openai_compatible(prompt, api_key, model, "https://api.openai.com/v1")
        elif provider == "openrouter":
            raw = _analyze_openai_compatible(prompt, api_key, model, "https://openrouter.ai/api/v1")
        elif provider == "gemini":
            raw = _analyze_gemini(prompt, api_key, model)
        else:
            return _fallback_error(f"Unsupported provider '{provider}'.")
    except Exception as exc:
        return _fallback_error(f"Failed to get AI analysis from {provider}: {exc}")

    try:
        parsed = json.loads(_extract_json(raw))
    except Exception:
        return _fallback_error(f"Could not parse AI response from {provider}.")
    return _sanitize_ai_result(parsed)
