"""
Shared pytest configuration for the AI Pilot Agent test suite.

Keeping the project root on sys.path here replaces the repeated per-test
PROJECT_ROOT/sys.path boilerplate that was previously copied into many files.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
