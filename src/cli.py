"""
Givondo Growth Engine CLI

A powerful command-line interface for operating the autonomous
opportunity discovery and application system.

Usage:
    growth-engine discover [--type TYPE] [--limit LIMIT]
    growth-engine apply OPPORTUNITY_ID [--type TYPE]
    growth-engine daily [--full]
    growth-engine analytics [--days DAYS] [--export FORMAT]
    growth-engine profile [--update]
    growth-engine learn [--auto-adjust]
    growth-engine serve [--port PORT]
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.markdown import Markdown

# Initialize CLI app
app = typer.Typer(
    name="growth-engine",
    help="🚀 Givondo Growth Engine - Autonomous Opportunity Discovery & Application System",
    add_completion=True,
)

# Rich console for beautiful output
console = Console()

# Sub-applications
discover_app = typer.Typer(help="Opportunity discovery commands")
apply_app = typer.Typer(help="Application generation commands")
analytics_app = typer.Typer(help="Analytics and insights")
profile_app = typer.Typer(help="Profile management")

app.add_typer(discover_app, name="discover")
app.add_typer(apply_app, name="apply")
app.add_typer(analytics_app, name="analytics")
app.add_typer(profile_app, name="profile")


def print_banner():
    """Print the Growth Engine banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🚀 GIVONDO GROWTH ENGINE                                   ║
║                                                              ║
║   Autonomous Opportunity Discovery & Application System      ║
║   Powered by Google ADK • Multi-Model AI Architecture       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


@app.callback()
def main_callback(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to config file"),
):
    """
    Givondo Growth Engine - Your Career on Autopilot
    
    An autonomous multi-agent system that discovers opportunities,
    generates applications, and learns from outcomes.
    """
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)


@app.command()
def version():
    """Show version information."""
    from importlib.metadata import version as get_version
    
    try:
        ver = get_version("givondo-growth-engine")
    except Exception:
        ver = "0.1.0"
    
    console.print(f"\n🚀 Givondo Growth Engine v{ver}")
    console.print("   Powered by Google ADK")
    console.print("   Multi-Model: Gemini • Claude Opus 4.5 • GPT-4\n")


@app.command()
def init(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config"),
):
    """Initialize the Growth Engine with your profile."""
    print_banner()
    
    console.print("\n📋 Let's set up your Growth Engine!\n", style="bold green")
    
    # Check for existing config
    config_path = Path(".env")
    if config_path.exists() and not force:
        console.print("⚠️  Configuration already exists. Use --force to overwrite.", style="yellow")
        raise typer.Exit(1)
    
    # Gather API keys
    console.print("🔑 API Keys (press Enter to skip optional ones):\n")
    
    gemini_key = typer.prompt("Google AI API Key (required)", hide_input=True)
    anthropic_key = typer.prompt("Anthropic API Key (for Claude)", default="", hide_input=True)
    openai_key = typer.prompt("OpenAI API Key (fallback)", default="", hide_input=True)
    
    console.print("\n🗄️  Database Configuration:\n")
    db_url = typer.prompt(
        "PostgreSQL URL",
        default="postgresql+asyncpg://localhost:5432/growth_engine"
    )
    
    # Write .env file
    env_content = f"""# Givondo Growth Engine Configuration
# Generated on {datetime.utcnow().isoformat()}

# API Keys
GOOGLE_API_KEY={gemini_key}
ANTHROPIC_API_KEY={anthropic_key}
OPENAI_API_KEY={openai_key}

# Database
DATABASE_URL={db_url}

# Model Configuration
ORCHESTRATOR_MODEL=gemini-2.0-flash
WRITING_MODEL=claude-opus-4-5-20250514
DISCOVERY_MODEL=gemini-2.0-flash

# Optional: Pinecone for vector search
PINECONE_API_KEY=
PINECONE_ENVIRONMENT=
PINECONE_INDEX=growth-engine
"""
    
    config_path.write_text(env_content)
    console.print("\n✅ Configuration saved to .env", style="green")
    
    # Initialize database
    if typer.confirm("\n🗄️  Initialize database tables?", default=True):
        console.print("\nInitializing database...", style="dim")
        asyncio.run(_init_database())
        console.print("✅ Database initialized!", style="green")
    
    console.print("\n🎉 Setup complete! Run 'growth-engine daily' to start.\n", style="bold green")


async def _init_database():
    """Initialize database tables."""
    from src.data.database import init_db
    await init_db()


# ==================== DISCOVER COMMANDS ====================

@discover_app.command("run")
def discover_run(
    query: str = typer.Argument(..., help="Search query for opportunities"),
    type: str = typer.Option("all", "--type", "-t", help="Opportunity type (job, fellowship, grant, etc.)"),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum opportunities to discover"),
    score: bool = typer.Option(True, "--score/--no-score", help="Score opportunities after discovery"),
):
    """Discover opportunities matching a query."""
    print_banner()
    
    console.print(f"\n🔍 Discovering opportunities: '{query}'", style="bold")
    console.print(f"   Type: {type} | Limit: {limit} | Scoring: {'✅' if score else '❌'}\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Searching...", total=None)
        
        results = asyncio.run(_discover_opportunities(query, type, limit, score))
        
        progress.update(task, completed=True, description="Search complete!")
    
    # Display results
    _display_opportunities(results)


async def _discover_opportunities(query: str, opp_type: str, limit: int, score: bool):
    """Run opportunity discovery."""
    from src.orchestrator.engine import growth_engine
    
    response = await growth_engine.discover_opportunities(
        query=query,
        opportunity_type=opp_type,
    )
    
    # Parse and return opportunities (simplified for CLI)
    return {
        "query": query,
        "type": opp_type,
        "count": limit,
        "response": response,
    }


def _display_opportunities(results: dict):
    """Display discovered opportunities in a table."""
    console.print(f"\n📊 Results for: '{results['query']}'\n")
    console.print(Markdown(results.get("response", "No results found.")))


@discover_app.command("daily")
def discover_daily(
    full: bool = typer.Option(False, "--full", "-f", help="Run full pipeline including applications"),
):
    """Run the daily discovery loop."""
    print_banner()
    
    console.print("\n🌅 Starting Daily Discovery Loop\n", style="bold green")
    console.print(f"   Mode: {'Full Pipeline' if full else 'Discovery Only'}")
    console.print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running daily loop...", total=None)
        
        if full:
            results = asyncio.run(_run_full_pipeline())
        else:
            results = asyncio.run(_run_daily_loop())
        
        progress.update(task, completed=True, description="Daily loop complete!")
    
    # Display summary
    _display_daily_summary(results)


async def _run_daily_loop():
    """Run the daily discovery loop."""
    from src.orchestrator.engine import growth_engine
    return await growth_engine.run_daily_loop()


async def _run_full_pipeline():
    """Run the full pipeline with intelligence layer."""
    from src.orchestrator.engine import growth_engine
    return await growth_engine.run_full_pipeline()


def _display_daily_summary(results: dict):
    """Display daily loop summary."""
    console.print("\n" + "=" * 60)
    console.print("📊 DAILY SUMMARY", style="bold cyan")
    console.print("=" * 60 + "\n")
    
    if "daily_summary" in results:
        console.print(Markdown(results["daily_summary"].get("summary", "")))
    elif "summary" in results:
        console.print(Markdown(results["summary"]))
    else:
        console.print(json.dumps(results, indent=2, default=str))


# ==================== APPLY COMMANDS ====================

@apply_app.command("generate")
def apply_generate(
    opportunity_id: str = typer.Argument(..., help="Opportunity ID to apply for"),
    type: str = typer.Option("cover_letter", "--type", "-t", help="Content type (essay, cover_letter, proposal)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Generate application content for an opportunity."""
    print_banner()
    
    console.print(f"\n✍️  Generating {type} for opportunity: {opportunity_id}\n", style="bold")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating content...", total=None)
        
        result = asyncio.run(_generate_application(opportunity_id, type))
        
        progress.update(task, completed=True, description="Content generated!")
    
    # Display or save result
    if output:
        output.write_text(result)
        console.print(f"\n✅ Saved to: {output}", style="green")
    else:
        console.print("\n" + "=" * 60)
        console.print(Markdown(result))


async def _generate_application(opportunity_id: str, content_type: str):
    """Generate application content."""
    from src.orchestrator.engine import growth_engine
    return await growth_engine.generate_application(
        opportunity_id=opportunity_id,
        content_type=content_type,
    )


@apply_app.command("outreach")
def apply_outreach(
    name: str = typer.Argument(..., help="Recipient name"),
    title: str = typer.Option(..., "--title", "-t", help="Recipient's job title"),
    company: str = typer.Option(..., "--company", "-c", help="Recipient's company"),
    opportunity: str = typer.Option("", "--opportunity", "-o", help="Related opportunity title"),
    type: str = typer.Option("cold_email", "--type", help="Message type (cold_email, linkedin)"),
):
    """Generate outreach message for a contact."""
    print_banner()
    
    console.print(f"\n📧 Generating {type} for: {name} at {company}\n", style="bold")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Crafting message...", total=None)
        
        result = asyncio.run(_create_outreach(name, title, company, opportunity, type))
        
        progress.update(task, completed=True, description="Message ready!")
    
    console.print("\n" + "=" * 60)
    console.print(Markdown(result))


async def _create_outreach(name: str, title: str, company: str, opportunity: str, msg_type: str):
    """Create outreach message."""
    from src.orchestrator.engine import growth_engine
    return await growth_engine.create_outreach(
        recipient_name=name,
        recipient_title=title,
        company=company,
        opportunity_title=opportunity,
        outreach_type=msg_type,
    )


# ==================== ANALYTICS COMMANDS ====================

@analytics_app.command("dashboard")
def analytics_dashboard(
    days: int = typer.Option(30, "--days", "-d", help="Number of days to analyze"),
    export: Optional[str] = typer.Option(None, "--export", "-e", help="Export format (json, csv)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output path"),
):
    """View analytics dashboard."""
    print_banner()
    
    console.print(f"\n📊 Analytics Dashboard ({days} days)\n", style="bold")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Loading analytics...", total=None)
        
        dashboard = asyncio.run(_get_dashboard(days))
        
        progress.update(task, completed=True, description="Analytics loaded!")
    
    if export:
        asyncio.run(_export_analytics(output or Path(f"analytics.{export}"), export, days))
        console.print(f"\n✅ Exported to: {output or f'analytics.{export}'}", style="green")
    else:
        _display_dashboard(dashboard)


async def _get_dashboard(days: int):
    """Get analytics dashboard."""
    from src.intelligence.analytics import get_dashboard
    return await get_dashboard(days)


async def _export_analytics(output: Path, format: str, days: int):
    """Export analytics data."""
    from src.intelligence.analytics import export_analytics
    await export_analytics(str(output.stem), format, days)


def _display_dashboard(dashboard):
    """Display analytics dashboard."""
    from src.intelligence.analytics import AnalyticsExporter, AnalyticsEngine
    
    engine = AnalyticsEngine()
    exporter = AnalyticsExporter(engine)
    
    console.print(exporter.format_for_display(dashboard))


@analytics_app.command("report")
def analytics_report(
    type: str = typer.Option("performance", "--type", "-t", help="Report type (performance, learning, roi)"),
):
    """Generate detailed analytics report."""
    print_banner()
    
    console.print(f"\n📈 Generating {type} report...\n", style="bold")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing data...", total=None)
        
        if type == "learning":
            report = asyncio.run(_get_learning_report())
        else:
            report = asyncio.run(_get_performance_report())
        
        progress.update(task, completed=True, description="Report ready!")
    
    console.print(json.dumps(report, indent=2, default=str))


async def _get_performance_report():
    """Get performance report."""
    from src.intelligence.learning import LearningAgent
    agent = LearningAgent()
    report = await agent.generate_performance_report(days=90)
    return report.model_dump()


async def _get_learning_report():
    """Get learning cycle report."""
    from src.orchestrator.engine import growth_engine
    return await growth_engine.run_learning_cycle(auto_adjust_weights=False)


# ==================== PROFILE COMMANDS ====================

@profile_app.command("show")
def profile_show():
    """Show current profile."""
    print_banner()
    
    console.print("\n👤 Your Profile\n", style="bold")
    
    # Load and display profile
    profile_data = asyncio.run(_get_profile())
    
    if profile_data:
        console.print(json.dumps(profile_data, indent=2, default=str))
    else:
        console.print("⚠️  No profile found. Run 'growth-engine profile create' to set up.", style="yellow")


async def _get_profile():
    """Get current profile."""
    from src.data.database import get_db_session
    from src.data.models import ProfileRecord
    from sqlalchemy import select
    
    async with get_db_session() as session:
        result = await session.execute(
            select(ProfileRecord).limit(1)
        )
        profile = result.scalar_one_or_none()
        if profile:
            return profile.profile_data
    return None


@profile_app.command("update")
def profile_update(
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="JSON file with profile data"),
):
    """Update your profile."""
    print_banner()
    
    if file:
        if not file.exists():
            console.print(f"❌ File not found: {file}", style="red")
            raise typer.Exit(1)
        
        profile_data = json.loads(file.read_text())
        console.print(f"\n📝 Updating profile from: {file}\n")
    else:
        console.print("\n📝 Interactive Profile Update\n", style="bold")
        console.print("(Press Enter to keep current value)\n")
        
        # Interactive profile update
        name = typer.prompt("Full Name", default="")
        title = typer.prompt("Current Title", default="")
        skills = typer.prompt("Key Skills (comma-separated)", default="")
        
        profile_data = {
            "name": name or None,
            "title": title or None,
            "skills": [s.strip() for s in skills.split(",")] if skills else None,
        }
        # Remove None values
        profile_data = {k: v for k, v in profile_data.items() if v}
    
    if profile_data:
        asyncio.run(_update_profile(profile_data))
        console.print("\n✅ Profile updated!", style="green")
    else:
        console.print("\n⚠️  No changes made.", style="yellow")


async def _update_profile(profile_data: dict):
    """Update profile in database."""
    from src.data.database import get_db_session
    from src.data.models import ProfileRecord
    from sqlalchemy import select
    
    async with get_db_session() as session:
        result = await session.execute(
            select(ProfileRecord).limit(1)
        )
        profile = result.scalar_one_or_none()
        
        if profile:
            # Merge with existing data
            existing = profile.profile_data or {}
            existing.update(profile_data)
            profile.profile_data = existing
        else:
            # Create new profile
            profile = ProfileRecord(
                user_id="default",
                profile_data=profile_data,
            )
            session.add(profile)
        
        await session.commit()


# ==================== LEARN COMMANDS ====================

@app.command()
def learn(
    auto_adjust: bool = typer.Option(False, "--auto-adjust", "-a", help="Auto-apply weight adjustments"),
    days: int = typer.Option(90, "--days", "-d", help="Analysis window in days"),
):
    """Run learning cycle to optimize scoring."""
    print_banner()
    
    console.print("\n🧠 Running Learning Cycle\n", style="bold")
    console.print(f"   Analysis Window: {days} days")
    console.print(f"   Auto-Adjust Weights: {'✅' if auto_adjust else '❌'}\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing outcomes...", total=None)
        
        results = asyncio.run(_run_learning(auto_adjust))
        
        progress.update(task, completed=True, description="Learning complete!")
    
    # Display results
    console.print("\n" + "=" * 60)
    console.print("📊 LEARNING RESULTS", style="bold cyan")
    console.print("=" * 60 + "\n")
    
    console.print(f"📈 Outcomes Analyzed: {results.get('outcomes_analyzed', 0)}")
    console.print(f"🎯 Acceptance Rate: {results.get('acceptance_rate', 0):.1%}")
    console.print(f"📊 Trend: {results.get('trend', 'N/A')}")
    console.print(f"🔍 Patterns Found: {results.get('patterns_found', 0)}")
    
    if results.get('weight_adjustments'):
        console.print("\n⚖️  Weight Adjustments:")
        for adj in results['weight_adjustments']:
            console.print(f"   • {adj['weight_name']}: {adj['current_value']:.3f} → {adj['proposed_value']:.3f}")
    
    if results.get('insights'):
        console.print("\n💡 Insights:")
        for insight in results['insights'][:3]:
            console.print(f"   • {insight.get('insight', '')}")


async def _run_learning(auto_adjust: bool):
    """Run learning cycle."""
    from src.orchestrator.engine import growth_engine
    return await growth_engine.run_learning_cycle(auto_adjust_weights=auto_adjust)


# ==================== RECORD OUTCOME ====================

@app.command()
def outcome(
    opportunity_id: str = typer.Argument(..., help="Opportunity ID"),
    result: str = typer.Argument(..., help="Outcome (accepted, rejected, interview, no_response)"),
    feedback: Optional[str] = typer.Option(None, "--feedback", "-f", help="Feedback received"),
    days: Optional[int] = typer.Option(None, "--days", "-d", help="Days until response"),
):
    """Record an application outcome for learning."""
    print_banner()
    
    console.print(f"\n📝 Recording outcome: {result} for {opportunity_id}\n", style="bold")
    
    asyncio.run(_record_outcome(opportunity_id, result, feedback, days))
    
    console.print("✅ Outcome recorded! The system will learn from this.", style="green")


async def _record_outcome(opp_id: str, result: str, feedback: Optional[str], days: Optional[int]):
    """Record application outcome."""
    from src.orchestrator.engine import growth_engine
    await growth_engine.record_application_outcome(
        opportunity_id=opp_id,
        outcome=result,
        feedback=feedback,
        response_time_days=days,
    )


# ==================== SERVE COMMAND ====================

@app.command()
def serve(
    port: int = typer.Option(8000, "--port", "-p", help="Port to run server on"),
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload"),
):
    """Start the Growth Engine API server."""
    print_banner()
    
    console.print(f"\n🌐 Starting API Server at http://{host}:{port}\n", style="bold")
    
    try:
        import uvicorn
        uvicorn.run(
            "src.api:app",
            host=host,
            port=port,
            reload=reload,
        )
    except ImportError:
        console.print("❌ uvicorn not installed. Run: pip install uvicorn", style="red")
        raise typer.Exit(1)


# ==================== MAIN ====================

def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
