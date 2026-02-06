# Contract Compliance Guard - Source Package
"""Contract Compliance Guard - Adversarial AI contract analysis."""

from .agent import run_analysis, has_api_key, load_demo_results
from .config import COMPANY_POLICY, CONTRACT_DISPLAY_NAMES

__all__ = [
    "run_analysis",
    "has_api_key",
    "load_demo_results",
    "COMPANY_POLICY",
    "CONTRACT_DISPLAY_NAMES",
]
