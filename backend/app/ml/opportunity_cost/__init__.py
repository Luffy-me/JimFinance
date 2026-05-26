"""Opportunity cost analysis for financial decisions.

Modules:
- decision_framework: Structure financial decisions
- tco_calculator: Total cost of ownership analysis
"""

from .decision_framework import (
    DecisionType,
    FinancialChoice,
    Decision,
    DecisionFramework,
)
from .tco_calculator import (
    CostType,
    CostComponent,
    TCOAnalysis,
    TCOCalculator,
)

__all__ = [
    "DecisionType",
    "FinancialChoice",
    "Decision",
    "DecisionFramework",
    "CostType",
    "CostComponent",
    "TCOAnalysis",
    "TCOCalculator",
]
