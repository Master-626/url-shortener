"""Unit tests for URL and short-code validation."""

import pytest

from url_shortener.core import (
    DEFAULT_BASE_URL,
    DEFAULT_CODE,
    build_short_url,
    normalize_base_url,
    normalize_code,
    normalize_target_url,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("https://github.com/Master-626", "https://github.com/Master-626"),
        ("https://github.com", "https://github.com"),
        ("https://example.com/a?b=1&c=2#frag", "https://example.com/a?b=1&c=2#frag"),
        ("https://example.com/docs/", "https://example.com/docs/"),
        ("http://localhost:8080/x", "http://localhost:8080/x"),
        ("http://127.0.0.1", "http://127.0.0.1"),
        ("http://[::1]:8080/path", "http://[::1]:8080/path"),
        ("https://user:pass@example.com/a", "https://user:pass@example.com/a"),
        ("HTTP://EXAMPLE.COM/A", "HTTP://EXAMPLE.COM/A"),
        ("https://example.com/path[0]", "https://example.com/path[0]"),
        ("https://例子.测试/a", "https://例子.测试/a"),
        ("https://example.com.", "https://example.com."),
        ("  https://example.com/docs/  ", "https://example.com/docs/"),
    ],
)
def test_normalize_target_url_accepts(raw, expected):
    assert normalize_target_url(raw) == expected


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ("", "must not be empty"),
        ("   ", "must not be empty"),
        ("javascript:alert(1)", "scheme must be http or https"),
        ("file:///etc/passwd", "scheme must be http or https"),
        ("data:text/html,hi", "scheme must be http or https"),
        ("ftp://example.com/a", "scheme must be http or https"),
        ("example.com", "scheme must be http or https"),
        ("/relative", "scheme must be http or https"),
        ("http://", "must include a host"),
        ("https://", "must include a host"),
        ("http://user@", "must include a host"),
        ("http://.", "must include a host"),
        ("http://..", "must include a host"),
        ("https://example.com:99999/x", "port is invalid"),
        ("https://example.com:abc/x", "port is invalid"),
        ("https://example.com/a b", "must not contain whitespace"),
        ("http://[::1", "not a valid URL"),
        (None, "must be a string"),
    ],
)
def test_normalize_target_url_rejects(raw, message):
    with pytest.raises(ValueError) as exc_info:
        normalize_target_url(raw)
    assert message in str(exc_info.value)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("gh", "gh"),
        (" gh ", "gh"),
        ("my-link", "my-link"),
        ("my_link", "my_link"),
        ("a.b", "a.b"),
        ("...", "..."),
        ("~", "~"),
        ("@me", "@me"),
        ("链接", "链接"),
        ("[bold]", "[bold]"),
        ("abc123", "abc123"),
    ],
)
def test_normalize_code_accepts(raw, expected):
    assert normalize_code(raw) == expected


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ("", "must not be empty"),
        ("   ", "must not be empty"),
        ("a/b", "must not contain"),
        ("a\\b", "must not contain"),
        ("a?b=1", "must not contain"),
        ("a#b", "must not contain"),
        ("a%2f", "must not contain"),
        (".", "must not be"),
        ("..", "must not be"),
        (" .. ", "must not be"),
        ("a b", "must not contain whitespace"),
        ("a\nb", "must not contain whitespace"),
        ("a\tb", "must not contain whitespace"),
        ("a\x00b", "control characters"),
        ("a\x7fb", "control characters"),
    ],
)
def test_normalize_code_rejects(raw, message):
    with pytest.raises(ValueError) as exc_info:
        normalize_code(raw)
    assert message in str(exc_info.value)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("https://my.url", "https://my.url"),
        ("https://my.url/", "https://my.url"),
        ("https://s.example/r/", "https://s.example/r"),
        ("  https://s.example/r///  ", "https://s.example/r"),
        ("http://[::1]:8080/s/", "http://[::1]:8080/s"),
        ("HTTPS://S.EXAMPLE", "HTTPS://S.EXAMPLE"),
    ],
)
def test_normalize_base_url_accepts(raw, expected):
    assert normalize_base_url(raw) == expected
    assert normalize_base_url(expected) == expected


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ("", "must not be empty"),
        ("   ", "must not be empty"),
        ("///", "must not be empty"),
        ("notaurl", "scheme must be http or https"),
        ("javascript:alert(1)", "scheme must be http or https"),
        ("https://example.com/s?q=1", "query or fragment"),
        ("https://example.com/s#f", "query or fragment"),
        ("https://example.com/foo/?", "query or fragment"),
        ("https://example.com:99999", "port is invalid"),
        ("http://", "must include a host"),
        ("https://example.com/a b", "must not contain whitespace"),
    ],
)
def test_normalize_base_url_rejects(raw, message):
    with pytest.raises(ValueError) as exc_info:
        normalize_base_url(raw)
    assert message in str(exc_info.value)


def test_build_short_url_uses_defaults_and_normalizes_base():
    assert build_short_url(DEFAULT_BASE_URL, DEFAULT_CODE) == "https://my.url/abc123"
    assert build_short_url("https://my.url/", " gh ") == "https://my.url/gh"


def test_build_short_url_rejects_unsafe_code():
    with pytest.raises(ValueError):
        build_short_url("https://my.url", "a/b")
