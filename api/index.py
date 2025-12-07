"""
Vercel Serverless Function Entry Point
Wraps the FastAPI app for Vercel deployment
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api import app

# Vercel expects the app to be named 'app' or 'handler'
# FastAPI works directly with Vercel's Python runtime
