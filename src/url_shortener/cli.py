"""CLI interface."""
import click
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
@click.version_option(version="0.1.0")
def main():
    """URL Shortener - Shorten and manage your URLs."""
    pass

@main.command()
@click.argument("url")
@click.option("--custom", "-c", help="Custom short code")
def shorten(url, custom):
    """Shorten a URL."""
    code = custom or "abc123"
    console.print(f"✅ Shortened: [bold green]{url}[/bold green] -> [cyan]https://my.url/{code}[/cyan]")

@main.command()
def list():
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
    console.print(f"📊 Stats for {code}: 42 clicks")

if __name__ == "__main__":
    main()
