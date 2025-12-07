#!/usr/bin/env python
"""
Daily Run Script

Execute the daily discovery and scoring loop.
Run this as a cron job or manually to discover and score opportunities.

Usage:
    python scripts/daily_run.py
    python scripts/daily_run.py --discover-only
    python scripts/daily_run.py --user-id my_user
"""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


async def run_daily_loop(user_id: str = "default_user", discover_only: bool = False):
    """Run the daily discovery and scoring loop."""
    
    console.print(Panel.fit(
        "[bold blue]🚀 GIVONDO GROWTH ENGINE[/bold blue]\n"
        f"[dim]Daily Run - {datetime.now().strftime('%Y-%m-%d %H:%M')}[/dim]",
        border_style="blue"
    ))
    
    try:
        from src.orchestrator import growth_engine
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            if discover_only:
                task = progress.add_task("Discovering opportunities...", total=None)
                result = await growth_engine.discover_opportunities(
                    query="AI ML Engineer Remote",
                    opportunity_type="job",
                    user_id=user_id,
                )
                progress.update(task, completed=True)
            else:
                task = progress.add_task("Running full daily loop...", total=None)
                result = await growth_engine.run_daily_loop(user_id=user_id)
                progress.update(task, completed=True)
        
        console.print("\n[bold green]✅ Daily loop completed![/bold green]\n")
        
        if isinstance(result, dict):
            console.print(Panel(
                result.get("summary", str(result)),
                title="📊 Summary",
                border_style="green"
            ))
        else:
            console.print(Panel(str(result), title="📊 Result", border_style="green"))
        
        return result
        
    except ImportError as e:
        console.print(f"[bold red]❌ Import Error:[/bold red] {e}")
        console.print("\n[yellow]Make sure you have installed dependencies:[/yellow]")
        console.print("  pip install -r requirements.txt")
        console.print("  pip install google-adk litellm")
        return None
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
        raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run the Givondo Growth Engine daily loop"
    )
    parser.add_argument(
        "--user-id",
        default="default_user",
        help="User ID for session tracking"
    )
    parser.add_argument(
        "--discover-only",
        action="store_true",
        help="Only run discovery, skip scoring"
    )
    
    args = parser.parse_args()
    
    asyncio.run(run_daily_loop(
        user_id=args.user_id,
        discover_only=args.discover_only,
    ))


if __name__ == "__main__":
    main()
