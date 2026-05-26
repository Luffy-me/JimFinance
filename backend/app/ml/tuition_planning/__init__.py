"""Tuition and education planning module.

Modules:
- cost_projector: Education cost projections
- loan_optimizer: Student loan scenarios
"""

from .cost_projector import (
    EducationLevel,
    EducationCost,
    CostProjection,
    CostProjector,
)
from .loan_optimizer import (
    LoanType,
    RepaymentPlan,
    StudentLoanScenario,
    LoanOptimization,
    LoanOptimizer,
)

__all__ = [
    "EducationLevel",
    "EducationCost",
    "CostProjection",
    "CostProjector",
    "LoanType",
    "RepaymentPlan",
    "StudentLoanScenario",
    "LoanOptimization",
    "LoanOptimizer",
]
