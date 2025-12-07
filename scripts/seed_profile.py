#!/usr/bin/env python
"""
Seed Profile Script

Initialize your profile in the Growth Engine database.
This script helps you set up your professional profile for
personalized opportunity matching and application generation.

Usage:
    python scripts/seed_profile.py
    python scripts/seed_profile.py --file config/profile_data.yaml
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
import yaml

console = Console()


def get_sample_profile() -> dict:
    """Return a sample profile structure."""
    return {
        "name": "Your Name",
        "email": "your.email@example.com",
        "phone": "+1-555-000-0000",
        "location": "San Francisco, CA",
        "headline": "AI/ML Engineer | Building Intelligent Systems",
        
        "summary": """Passionate AI/ML engineer with expertise in building 
        production systems. Focused on applying cutting-edge research to 
        solve real-world problems.""",
        
        "experience": [
            {
                "title": "Senior ML Engineer",
                "company": "TechCorp",
                "location": "San Francisco, CA",
                "start_date": "2022-01",
                "end_date": "present",
                "description": "Leading ML infrastructure and model deployment.",
                "highlights": [
                    "Built ML platform serving 10M+ predictions/day",
                    "Reduced model training time by 60%",
                    "Led team of 5 engineers"
                ]
            },
            {
                "title": "ML Engineer",
                "company": "StartupAI",
                "location": "New York, NY",
                "start_date": "2020-03",
                "end_date": "2021-12",
                "description": "Full-stack ML development for NLP products.",
                "highlights": [
                    "Developed production NLP pipelines",
                    "Implemented real-time recommendation system"
                ]
            }
        ],
        
        "education": [
            {
                "degree": "M.S. Computer Science",
                "institution": "Stanford University",
                "year": 2020,
                "focus": "Machine Learning & AI",
                "gpa": 3.9
            },
            {
                "degree": "B.S. Computer Science",
                "institution": "UC Berkeley",
                "year": 2018,
                "gpa": 3.8
            }
        ],
        
        "skills": {
            "programming": ["Python", "Go", "TypeScript", "Rust"],
            "ml_frameworks": ["PyTorch", "TensorFlow", "JAX", "Hugging Face"],
            "infrastructure": ["Kubernetes", "Docker", "GCP", "AWS"],
            "specializations": ["NLP", "Computer Vision", "Reinforcement Learning"]
        },
        
        "publications": [
            {
                "title": "Efficient Transformer Training",
                "venue": "NeurIPS 2023",
                "url": "https://arxiv.org/abs/xxxx.xxxxx"
            }
        ],
        
        "projects": [
            {
                "name": "Open Source ML Library",
                "description": "Popular ML utility library with 5k+ GitHub stars",
                "url": "https://github.com/username/project",
                "impact": "Used by 100+ companies"
            }
        ],
        
        "preferences": {
            "opportunity_types": ["job", "fellowship", "grant"],
            "remote_preference": "remote_preferred",
            "salary_minimum": 150000,
            "location_preferences": ["San Francisco", "New York", "Remote"],
            "company_size_preferences": ["startup", "growth", "enterprise"],
            "industry_preferences": ["AI/ML", "Climate Tech", "Healthcare"]
        },
        
        "social": {
            "linkedin": "https://linkedin.com/in/yourprofile",
            "github": "https://github.com/yourusername",
            "twitter": "https://twitter.com/yourhandle",
            "website": "https://yourwebsite.com"
        }
    }


def display_profile(profile: dict) -> None:
    """Display profile in a formatted table."""
    console.print("\n[bold cyan]📋 Profile Summary[/bold cyan]\n")
    
    # Basic info
    table = Table(show_header=False, box=None)
    table.add_column("Field", style="cyan", width=20)
    table.add_column("Value")
    
    table.add_row("Name", profile.get("name", ""))
    table.add_row("Email", profile.get("email", ""))
    table.add_row("Location", profile.get("location", ""))
    table.add_row("Headline", profile.get("headline", ""))
    
    console.print(table)
    
    # Skills
    skills = profile.get("skills", {})
    if skills:
        console.print("\n[bold]Skills:[/bold]")
        for category, skill_list in skills.items():
            if isinstance(skill_list, list):
                console.print(f"  • {category}: {', '.join(skill_list)}")
    
    # Experience
    experience = profile.get("experience", [])
    if experience:
        console.print(f"\n[bold]Experience:[/bold] {len(experience)} positions")
        for exp in experience[:2]:
            console.print(f"  • {exp.get('title', '')} at {exp.get('company', '')}")
    
    # Education
    education = profile.get("education", [])
    if education:
        console.print(f"\n[bold]Education:[/bold] {len(education)} degrees")
        for edu in education:
            console.print(f"  • {edu.get('degree', '')} - {edu.get('institution', '')}")


async def save_profile_to_db(profile: dict) -> bool:
    """Save profile to database."""
    try:
        from src.models import Profile
        from src.data.database import async_session
        from sqlalchemy import select
        
        async with async_session() as session:
            # Check if profile exists
            existing = await session.execute(
                select(Profile).where(Profile.email == profile["email"])
            )
            existing_profile = existing.scalar_one_or_none()
            
            if existing_profile:
                # Update existing
                for key, value in profile.items():
                    if hasattr(existing_profile, key):
                        setattr(existing_profile, key, value)
                console.print("[yellow]Updated existing profile[/yellow]")
            else:
                # Create new
                new_profile = Profile(**profile)
                session.add(new_profile)
                console.print("[green]Created new profile[/green]")
            
            await session.commit()
            return True
            
    except ImportError:
        console.print("[yellow]Database not configured, saving to YAML only[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]Database error: {e}[/red]")
        return False


def save_profile_to_yaml(profile: dict, filepath: Path) -> None:
    """Save profile to YAML file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        yaml.dump(profile, f, default_flow_style=False, sort_keys=False)
    console.print(f"[green]✓ Profile saved to {filepath}[/green]")


def load_profile_from_yaml(filepath: Path) -> dict:
    """Load profile from YAML file."""
    if not filepath.exists():
        return {}
    with open(filepath, 'r') as f:
        return yaml.safe_load(f) or {}


async def interactive_profile_setup() -> dict:
    """Interactively set up a profile."""
    console.print(Panel.fit(
        "[bold blue]🚀 GIVONDO GROWTH ENGINE[/bold blue]\n"
        "[dim]Profile Setup Wizard[/dim]",
        border_style="blue"
    ))
    
    profile = get_sample_profile()
    
    console.print("\n[cyan]Let's set up your professional profile.[/cyan]")
    console.print("[dim]Press Enter to keep the default value shown in brackets.[/dim]\n")
    
    # Basic info
    profile["name"] = Prompt.ask("Your full name", default=profile["name"])
    profile["email"] = Prompt.ask("Email", default=profile["email"])
    profile["location"] = Prompt.ask("Location", default=profile["location"])
    profile["headline"] = Prompt.ask("Professional headline", default=profile["headline"])
    
    # Skills
    console.print("\n[cyan]Enter your top skills (comma-separated):[/cyan]")
    skills_input = Prompt.ask(
        "Programming languages",
        default=", ".join(profile["skills"]["programming"])
    )
    profile["skills"]["programming"] = [s.strip() for s in skills_input.split(",")]
    
    ml_input = Prompt.ask(
        "ML frameworks",
        default=", ".join(profile["skills"]["ml_frameworks"])
    )
    profile["skills"]["ml_frameworks"] = [s.strip() for s in ml_input.split(",")]
    
    # Preferences
    console.print("\n[cyan]Set your job preferences:[/cyan]")
    profile["preferences"]["remote_preference"] = Prompt.ask(
        "Remote preference",
        choices=["remote_only", "remote_preferred", "hybrid", "onsite"],
        default="remote_preferred"
    )
    
    salary = Prompt.ask("Minimum salary (USD)", default="150000")
    profile["preferences"]["salary_minimum"] = int(salary)
    
    return profile


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Seed your profile in the Growth Engine"
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=Path("config/profile_data.yaml"),
        help="Path to profile YAML file"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run interactive profile setup"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Generate a sample profile file"
    )
    
    args = parser.parse_args()
    
    if args.sample:
        # Generate sample profile
        profile = get_sample_profile()
        save_profile_to_yaml(profile, args.file)
        console.print("\n[green]✓ Sample profile generated![/green]")
        console.print(f"[dim]Edit {args.file} with your information, then run:[/dim]")
        console.print(f"  python scripts/seed_profile.py --file {args.file}")
        return
    
    if args.interactive:
        # Interactive setup
        profile = await interactive_profile_setup()
    elif args.file.exists():
        # Load from file
        console.print(f"[cyan]Loading profile from {args.file}...[/cyan]")
        profile = load_profile_from_yaml(args.file)
    else:
        console.print(f"[yellow]Profile file not found: {args.file}[/yellow]")
        console.print("\nOptions:")
        console.print("  1. Generate a sample profile: python scripts/seed_profile.py --sample")
        console.print("  2. Interactive setup: python scripts/seed_profile.py --interactive")
        return
    
    # Display profile
    display_profile(profile)
    
    # Confirm and save
    if Confirm.ask("\n💾 Save this profile?", default=True):
        # Save to YAML
        save_profile_to_yaml(profile, args.file)
        
        # Try to save to database
        await save_profile_to_db(profile)
        
        console.print("\n[bold green]✅ Profile setup complete![/bold green]")
        console.print("[dim]Your profile will be used for opportunity matching and application generation.[/dim]")


if __name__ == "__main__":
    asyncio.run(main())
