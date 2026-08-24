import anthropic

from app.config import settings

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else None


def call_claude(prompt: str, timeout_seconds: int = 15) -> str | None:
    """Returns None on any failure (no key configured, timeout, API error) —
    callers must handle this gracefully per FR-20, never block on it.
    """
    if _client is None:
        return None
    try:
        response = _client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
            timeout=timeout_seconds,
        )
        return response.content[0].text
    except Exception:
        return None
