"""Validation helpers for the URL shortener CLI."""

from urllib.parse import ParseResult, urlparse

DEFAULT_CODE = "abc123"
DEFAULT_BASE_URL = "https://my.url"
_UNSAFE_CODE_CHARS = frozenset("/\\?#%")


def normalize_target_url(url: str) -> str:
    """Return a stripped absolute http(s) URL, or raise ValueError."""
    cleaned = _strip_required(url, "URL")
    _reject_internal_whitespace(cleaned, "URL")
    parsed = _parse_http_url(cleaned, "URL")
    _require_host(parsed, "URL")
    return cleaned


def normalize_base_url(base_url: str) -> str:
    """Return a base URL without a trailing slash, query, or fragment."""
    cleaned = _strip_required(base_url, "base URL")
    _reject_internal_whitespace(cleaned, "base URL")
    cleaned = cleaned.rstrip("/")
    if not cleaned:
        raise ValueError("base URL must not be empty")
    if "?" in cleaned or "#" in cleaned:
        raise ValueError("base URL must not include a query or fragment")
    parsed = _parse_http_url(cleaned, "base URL")
    _require_host(parsed, "base URL")
    return cleaned


def normalize_code(code: str) -> str:
    """Return a short code that stays a single URL path segment."""
    cleaned = _strip_required(code, "custom code")
    if any(character.isspace() for character in cleaned):
        raise ValueError("custom code must not contain whitespace")
    if any(not character.isprintable() for character in cleaned):
        raise ValueError("custom code must not contain control characters")
    if any(character in _UNSAFE_CODE_CHARS for character in cleaned):
        raise ValueError("custom code must not contain '/', '\\', '?', '#', or '%'")
    if cleaned in {".", ".."}:
        raise ValueError("custom code must not be '.' or '..'")
    return cleaned


def build_short_url(base_url: str, code: str) -> str:
    """Join a base URL and a short code into one short link."""
    return f"{normalize_base_url(base_url)}/{normalize_code(code)}"


def _strip_required(value: str, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{label} must not be empty")
    return cleaned


def _reject_internal_whitespace(value: str, label: str) -> None:
    if any(character.isspace() for character in value):
        raise ValueError(f"{label} must not contain whitespace")


def _parse_http_url(value: str, label: str) -> ParseResult:
    try:
        parsed = urlparse(value)
    except ValueError as exc:
        raise ValueError(f"{label} is not a valid URL") from exc
    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError(f"{label} scheme must be http or https")
    return parsed


def _require_host(parsed: ParseResult, label: str) -> None:
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError(f"{label} port is invalid") from exc
    if port is not None and not 0 <= port <= 65535:
        raise ValueError(f"{label} port is invalid")
    try:
        host = parsed.hostname
    except ValueError as exc:
        raise ValueError(f"{label} host is invalid") from exc
    if host is None or not host.strip("."):
        raise ValueError(f"{label} must include a host")
