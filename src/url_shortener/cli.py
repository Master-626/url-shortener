"""CLI interface."""

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

from url_shortener import __version__
from url_shortener.core import (
    DEFAULT_BASE_URL,
    DEFAULT_CODE,
    build_short_url,
    normalize_base_url,
    normalize_code,
    normalize_target_url,
)

console = Console()


def _validated(parse):
    def callback(_ctx, _param, value):
        if value is None:
            return None
        try:
            return parse(value)
        except ValueError as exc:
            raise click.BadParameter(str(exc)) from exc

    return callback


def shorten_message(url, short_url):
    """Build the shorten line without parsing user text as Rich markup."""
    return Text.assemble(
        "✅ Shortened: ",
        (url, "bold green"),
        " -> ",
        (short_url, "cyan"),
    )


def stats_message(code):
    """Build the stats line without parsing the code as Rich markup."""
    return Text.assemble("📊 Stats for ", code, ": 42 clicks")


@click.group()
@click.version_option(version=__version__)
def main():
    """URL Shortener - Shorten and manage your URLs."""


@main.command()
@click.argument("url", callback=_validated(normalize_target_url))
@click.option(
    "--custom",
    "-c",
    callback=_validated(normalize_code),
    help="Custom short code used instead of abc123.",
)
@click.option(
    "--base-url",
    "-b",
    default=DEFAULT_BASE_URL,
    show_default=True,
    show_envvar=True,
    envvar="SHORTEN_BASE_URL",
    callback=_validated(normalize_base_url),
    help="Prefix for the short link.",
)
def shorten(url, custom, base_url):
    """Shorten a URL."""
    code = DEFAULT_CODE if custom is None else custom
    console.print(shorten_message(url, build_short_url(base_url, code)))


@main.command("list")
def list_urls():
    """List all shortened URLs."""
    table = Table(title="URLs")
    table.add_column("Code", style="cyan")
    table.add_column("URL", style="green")
    table.add_column("Clicks")
    table.add_row("abc123", "https://github.com", "42")
    console.print(table)


@main.command()
@click.argument("code")
def stats(code):
    """View statistics for a shortened URL."""
    console.print(stats_message(code))


if __name__ == "__main__":
    main()
