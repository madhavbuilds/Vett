import anthropic
import json

def analyze_with_claude(files, security, todos, large, complex_fns, api_key):
    client = anthropic.Anthropic(api_key=api_key)

    file_summary = "\n".join(
        f"- {f['path']} ({f['language']}, {f['lines']} lines)"
        for f in files[:20]
    )
    sample_files = sorted(files, key=lambda x: x["lines"], reverse=True)[:3]
    code_samples = ""
    for f in sample_files:
        snippet = "\n".join(f["content"].splitlines()[:60])
        code_samples += f"\n\n### {f['path']} ({f['language']})\n```\n{snippet}\n```"

    prompt = f"""You are Vett, an expert AI code reviewer. Analyze this codebase and give a structured health report.

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

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except:
        return {
            "project_summary": "Could not parse AI response.",
            "overall_score": 0, "grade": "?",
            "strengths": [], "critical_issues": ["Failed to get AI analysis — check your API key."],
            "suggestions": [], "estimated_tech_debt": "Unknown",
            "one_line_roast": "Your code broke the AI. Impressive.",
        }
