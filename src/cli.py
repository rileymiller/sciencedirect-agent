"""
CLI interface for the ScienceDirect research agent.
"""

import asyncio
import os
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from dotenv import load_dotenv
from .agent import answer_research_question, chat_with_agent
from .sciencedirect import ScienceDirectClient

load_dotenv()

app = typer.Typer()
console = Console()


@app.command()
def chat(
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="Elsevier API key"),
    inst_token: Optional[str] = typer.Option(None, "--inst-token", "-t", help="Institutional token")
):
    """
    Start an interactive chat session with the research agent.
    """
    console.print(Panel.fit(
        "[bold cyan]Scientific Research Assistant[/bold cyan]\n"
        "Ask any scientific question and I'll search the literature for you.",
        title="Welcome",
        border_style="cyan"
    ))
    
    # Use provided keys or fall back to environment variables
    api_key = api_key or os.getenv("ELSEVIER_API_KEY")
    inst_token = inst_token or os.getenv("ELSEVIER_INST_TOKEN")
    
    if not api_key:
        console.print("[red]Error: Elsevier API key is required.[/red]")
        console.print("Set ELSEVIER_API_KEY in .env or use --api-key option")
        raise typer.Exit(1)
    
    try:
        asyncio.run(chat_with_agent(api_key, inst_token))
    except KeyboardInterrupt:
        console.print("\n[yellow]Chat session ended.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query for articles"),
    limit: int = typer.Option(5, "--limit", "-l", help="Maximum number of results"),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="Elsevier API key"),
    inst_token: Optional[str] = typer.Option(None, "--inst-token", "-t", help="Institutional token")
):
    """
    Search for scientific articles on ScienceDirect.
    """
    api_key = api_key or os.getenv("ELSEVIER_API_KEY")
    inst_token = inst_token or os.getenv("ELSEVIER_INST_TOKEN")
    
    if not api_key:
        console.print("[red]Error: Elsevier API key is required.[/red]")
        raise typer.Exit(1)
    
    async def run_search():
        client = ScienceDirectClient(api_key, inst_token)
        
        with console.status("[cyan]Searching articles...[/cyan]"):
            try:
                articles = await client.search_articles(query, limit)
                
                if not articles:
                    console.print("[yellow]No articles found.[/yellow]")
                    return
                
                # Create a table for results
                table = Table(title=f"Search Results for: {query}")
                table.add_column("No.", style="cyan", width=4)
                table.add_column("Title", style="white", width=50)
                table.add_column("Authors", style="green", width=30)
                table.add_column("Journal", style="blue", width=25)
                table.add_column("Year", style="yellow", width=10)
                
                for i, article in enumerate(articles, 1):
                    authors = ", ".join(article.authors[:2]) if article.authors else "N/A"
                    if len(article.authors) > 2:
                        authors += f" et al."
                    
                    year = article.publication_date[:4] if article.publication_date else "N/A"
                    journal = article.publication_name or "N/A"
                    
                    # Truncate long titles
                    title = article.title
                    if len(title) > 47:
                        title = title[:47] + "..."
                    
                    table.add_row(
                        str(i),
                        title,
                        authors,
                        journal[:25],
                        year
                    )
                
                console.print(table)
                
                # Show abstracts if available
                console.print("\n[bold]Abstracts:[/bold]")
                for i, article in enumerate(articles, 1):
                    if article.abstract:
                        console.print(f"\n[cyan]{i}. {article.title}[/cyan]")
                        console.print(Panel(
                            article.abstract[:500] + ("..." if len(article.abstract) > 500 else ""),
                            border_style="dim"
                        ))
                
            except Exception as e:
                console.print(f"[red]Search failed: {e}[/red]")
    
    asyncio.run(run_search())


@app.command()
def ask(
    question: str = typer.Argument(..., help="Research question to answer"),
    max_articles: int = typer.Option(5, "--max-articles", "-m", help="Maximum articles to analyze"),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="Elsevier API key"),
    inst_token: Optional[str] = typer.Option(None, "--inst-token", "-t", help="Institutional token")
):
    """
    Ask a research question and get an AI-powered answer with citations.
    """
    api_key = api_key or os.getenv("ELSEVIER_API_KEY")
    inst_token = inst_token or os.getenv("ELSEVIER_INST_TOKEN")
    
    if not api_key:
        console.print("[red]Error: Elsevier API key is required.[/red]")
        raise typer.Exit(1)
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]Error: OpenAI API key is required for AI responses.[/red]")
        console.print("Set OPENAI_API_KEY in .env file")
        raise typer.Exit(1)
    
    async def run_research():
        with console.status("[cyan]Researching your question...[/cyan]", spinner="dots"):
            try:
                response = await answer_research_question(
                    question,
                    max_articles,
                    api_key,
                    inst_token
                )
                
                # Display the answer
                console.print(Panel(
                    Markdown(f"# Answer\n\n{response.answer}"),
                    title="Research Finding",
                    border_style="green"
                ))
                
                # Display articles
                if response.articles:
                    console.print("\n[bold cyan]Referenced Articles:[/bold cyan]")
                    for i, article in enumerate(response.articles, 1):
                        console.print(f"\n[yellow]{i}.[/yellow] [white]{article.title}[/white]")
                        if article.authors:
                            console.print(f"   [green]Authors:[/green] {', '.join(article.authors[:3])}")
                        if article.publication_name:
                            console.print(f"   [blue]Journal:[/blue] {article.publication_name}")
                        if article.publication_date:
                            console.print(f"   [magenta]Date:[/magenta] {article.publication_date}")
                        if article.doi:
                            console.print(f"   [cyan]DOI:[/cyan] {article.doi}")
                
                # Display summary
                if response.summary:
                    console.print(Panel(
                        response.summary,
                        title="Summary",
                        border_style="blue"
                    ))
                
            except Exception as e:
                console.print(f"[red]Research failed: {e}[/red]")
    
    asyncio.run(run_research())


@app.command()
def config():
    """
    Show current configuration and API key status.
    """
    console.print(Panel.fit("[bold]Configuration Status[/bold]", border_style="cyan"))
    
    # Check Elsevier API key
    elsevier_key = os.getenv("ELSEVIER_API_KEY")
    if elsevier_key:
        masked_key = elsevier_key[:8] + "..." + elsevier_key[-4:] if len(elsevier_key) > 12 else "***"
        console.print(f"[green]+[/green] Elsevier API Key: {masked_key}")
    else:
        console.print("[red]X[/red] Elsevier API Key: Not set")
    
    # Check institutional token
    inst_token = os.getenv("ELSEVIER_INST_TOKEN")
    if inst_token:
        console.print(f"[green]+[/green] Institutional Token: Set")
    else:
        console.print("[yellow]o[/yellow] Institutional Token: Not set (optional)")
    
    # Check OpenAI API key
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        masked_key = openai_key[:8] + "..." + openai_key[-4:] if len(openai_key) > 12 else "***"
        console.print(f"[green]+[/green] OpenAI API Key: {masked_key}")
    else:
        console.print("[red]X[/red] OpenAI API Key: Not set")
    
    # Check default model
    model = os.getenv("DEFAULT_MODEL", "openai:gpt-4o-mini")
    console.print(f"[blue]i[/blue] Default Model: {model}")
    
    console.print("\n[dim]Edit .env file to update configuration[/dim]")


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()