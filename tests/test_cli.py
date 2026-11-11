"""CLI tests for happy-path output, bug fixes, and --base-url."""

import pytest
from click.testing import CliRunner

from url_shortener import __version__
from url_shortener.cli import main, shorten_message, stats_message


@pytest.fixture(autouse=True)
def _no_base_url_env(monkeypatch):
    monkeypatch.delenv("SHORTEN_BASE_URL", raising=False)


@pytest.fixture
def runner():
    return CliRunner()


def test_shorten_message_keeps_brackets_as_text():
    url = "https://example.com/[link=https://evil.test]click[/link]"
    short_url = "https://my.url/abc123"
    assert shorten_message(url, short_url).plain == (
        f"✅ Shortened: {url} -> {short_url}"
    )


def test_stats_message_keeps_brackets_as_text():
    assert stats_message("[bold]").plain == "📊 Stats for [bold]: 42 clicks"
    assert stats_message("[/]").plain == "📊 Stats for [/]: 42 clicks"


def test_shorten_default_code_output(runner):
    result = runner.invoke(main, ["shorten", "https://github.com/Master-626"])
    assert result.exit_code == 0
    assert result.output == (
        "✅ Shortened: https://github.com/Master-626 -> https://my.url/abc123\n"
    )


def test_custom_code_output(runner):
    result = runner.invoke(main, ["shorten", "https://github.com", "-c", "gh"])
    assert result.exit_code == 0
    assert result.output == ("✅ Shortened: https://github.com -> https://my.url/gh\n")


def test_different_urls_still_use_the_sample_code(runner):
    first = runner.invoke(main, ["shorten", "https://example.com/one"])
    second = runner.invoke(main, ["shorten", "https://example.com/two"])
    assert "https://my.url/abc123" in first.output
    assert "https://my.url/abc123" in second.output


def test_surrounding_whitespace_is_stripped(runner):
    result = runner.invoke(main, ["shorten", "  https://github.com/Master-626  "])
    assert result.exit_code == 0
    assert result.output == (
        "✅ Shortened: https://github.com/Master-626 -> https://my.url/abc123\n"
    )


def test_padded_custom_code_is_stripped(runner):
    result = runner.invoke(main, ["shorten", "https://example.com", "-c", " gh "])
    assert result.exit_code == 0
    assert result.output == ("✅ Shortened: https://example.com -> https://my.url/gh\n")


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/[bold]x[/bold]",
        "https://example.com/[BOLD]x[/BOLD]",
        "https://example.com/[/]",
        "http://[::1]:8080/path",
        "https://example.com/path[0]",
    ],
)
def test_shorten_prints_url_literally(runner, url):
    result = runner.invoke(main, ["shorten", url])
    assert result.exit_code == 0
    assert result.exception is None
    assert result.output == f"✅ Shortened: {url} -> https://my.url/abc123\n"


def test_rich_link_markup_is_not_rewritten(runner):
    url = "https://example.com/[link=https://evil.test]click[/link]"
    result = runner.invoke(main, ["shorten", url])
    assert result.exit_code == 0
    assert result.exception is None
    assert result.output.replace("\n", "") == (
        f"✅ Shortened: {url} -> https://my.url/abc123"
    )


@pytest.mark.parametrize(
    ("url", "message"),
    [
        ("javascript:alert(1)", "scheme must be http or https"),
        ("file:///etc/passwd", "scheme must be http or https"),
        ("data:text/html,hi", "scheme must be http or https"),
        ("https://example.com:99999/x", "port is invalid"),
        ("http://", "must include a host"),
        ("https://example.com/a b", "must not contain whitespace"),
        ("", "must not be empty"),
    ],
)
def test_shorten_rejects_bad_urls(runner, url, message):
    result = runner.invoke(main, ["shorten", url])
    assert result.exit_code == 2
    assert message in result.output
    assert "Shortened" not in result.output


@pytest.mark.parametrize(
    ("code", "message"),
    [
        ("", "must not be empty"),
        ("   ", "must not be empty"),
        ("a/b", "must not contain"),
        ("a?b=1", "must not contain"),
        ("a#b", "must not contain"),
        ("a%2f", "must not contain"),
        ("..", "must not be"),
        (".", "must not be"),
        ("my code", "must not contain whitespace"),
    ],
)
def test_shorten_rejects_bad_custom_codes(runner, code, message):
    result = runner.invoke(main, ["shorten", "https://example.com", "-c", code])
    assert result.exit_code == 2
    assert message in result.output
    assert "Shortened" not in result.output


def test_list_prints_sample_row(runner):
    result = runner.invoke(main, ["list"])
    assert result.exit_code == 0
    assert "abc123" in result.output
    assert "https://github.com" in result.output
    assert "42" in result.output
    assert "Code" in result.output
    assert "Clicks" in result.output


def test_shorten_does_not_change_sample_list(runner):
    before = runner.invoke(main, ["list"])
    created = runner.invoke(main, ["shorten", "https://example.com/new"])
    after = runner.invoke(main, ["list"])
    assert created.exit_code == 0
    assert after.output == before.output


def test_stats_sample_count(runner):
    result = runner.invoke(main, ["stats", "gh"])
    assert result.exit_code == 0
    assert result.output == "📊 Stats for gh: 42 clicks\n"


@pytest.mark.parametrize("code", ["[bold]", "[/]", "a/b", "anything-else"])
def test_stats_prints_code_literally(runner, code):
    result = runner.invoke(main, ["stats", code])
    assert result.exit_code == 0
    assert result.exception is None
    assert result.output == f"📊 Stats for {code}: 42 clicks\n"


def test_version(runner):
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_help_lists_commands_and_base_url(runner):
    root = runner.invoke(main, ["--help"])
    shorten_help = runner.invoke(main, ["shorten", "--help"])
    assert root.exit_code == 0
    assert "list" in root.output
    assert "shorten" in root.output
    assert "stats" in root.output
    assert shorten_help.exit_code == 0
    assert "--custom" in shorten_help.output
    assert "--base-url" in shorten_help.output
    assert "SHORTEN_BASE_URL" in shorten_help.output
    assert "https://my.url" in shorten_help.output


def test_missing_url_is_usage_error(runner):
    result = runner.invoke(main, ["shorten"])
    assert result.exit_code == 2
    assert "Missing argument" in result.output


def test_base_url_option(runner):
    result = runner.invoke(
        main,
        ["shorten", "https://github.com", "-c", "gh", "-b", "https://s.example/r/"],
    )
    assert result.exit_code == 0
    assert result.output == (
        "✅ Shortened: https://github.com -> https://s.example/r/gh\n"
    )


def test_explicit_default_base_matches_builtin(runner):
    default = runner.invoke(main, ["shorten", "https://github.com"])
    explicit = runner.invoke(
        main,
        ["shorten", "https://github.com", "--base-url", "https://my.url/"],
    )
    assert explicit.exit_code == 0
    assert explicit.output == default.output


def test_base_url_env_and_cli_override(runner):
    from_env = runner.invoke(
        main,
        ["shorten", "https://github.com"],
        env={"SHORTEN_BASE_URL": "https://cdn.example/s/"},
    )
    overridden = runner.invoke(
        main,
        ["shorten", "https://github.com", "--base-url", "https://a.example"],
        env={"SHORTEN_BASE_URL": "https://b.example"},
    )
    assert from_env.exit_code == 0
    assert from_env.output == (
        "✅ Shortened: https://github.com -> https://cdn.example/s/abc123\n"
    )
    assert overridden.exit_code == 0
    assert overridden.output == (
        "✅ Shortened: https://github.com -> https://a.example/abc123\n"
    )


def test_invalid_base_url(runner):
    result = runner.invoke(
        main,
        ["shorten", "https://github.com", "-b", "https://example.com/s?q=1"],
    )
    assert result.exit_code == 2
    assert "query or fragment" in result.output
    assert "Shortened" not in result.output
