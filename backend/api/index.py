"""Vercel Serverless Function entry point for the FastAPI backend.

This module adapts the ASGI FastAPI application to Vercel's Python runtime.
The handler function is the entry point referenced in vercel.json.

Usage in vercel.json:
    "functions": {
        "backend/api/index.py": {
            "runtime": "@vercel/python@3",
            "maxDuration": 30
        }
    }
"""
from __future__ import annotations

import sys
import os

# Ensure the backend directory is on the Python path so `app.*` imports resolve.
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from mangum import Mangum
from app.main import app

# Mangum adapts ASGI apps to AWS Lambda / Vercel serverless handler format.
# The `app` is the FastAPI instance from app.main.
handler = Mangum(app, lifespan="auto")
