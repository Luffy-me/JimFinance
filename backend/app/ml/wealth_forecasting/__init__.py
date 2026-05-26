"""Advanced wealth forecasting engine.

Modules:
- compound_simulator: Multi-factor wealth compounding
- scenario_modeler: Life event scenarios
"""

from .compound_simulator import (
    CompoundingAssumptions,
    WealthProjection,
    CompoundSimulator,
)
from .scenario_modeler import (
    LifeEventType,
    LifeEventScenario,
    WealthScenarioAnalysis,
    WealthScenarioModeler,
)

__all__ = [
    "CompoundingAssumptions",
    "WealthProjection",
    "CompoundSimulator",
    "LifeEventType",
    "LifeEventScenario",
    "WealthScenarioAnalysis",
    "WealthScenarioModeler",
]
