"""
Multi-agent reasoning system for JimFinance.
Combines Gemini Pro (strategist) and Groq (critic) for comprehensive financial analysis.
"""

from app.ml.agents.base import BaseAgent
from app.ml.agents.types import (
    FinancialMetrics,
    TransactionContext,
    StrategistOutput,
    CriticOutput,
    SynthesisOutput,
    FinancialInsight,
    RiskLevel,
    InsightType,
    AgentError,
    StrategyGenerationError,
    RiskAssessmentError,
    SynthesisError,
)
from app.ml.agents.strategist import StrategistAgent
from app.ml.agents.critic import CriticAgent
from app.ml.agents.synthesizer import SynthesisEngine

__all__ = [
    "BaseAgent",
    "FinancialMetrics",
    "TransactionContext",
    "StrategistOutput",
    "CriticOutput",
    "SynthesisOutput",
    "FinancialInsight",
    "RiskLevel",
    "InsightType",
    "AgentError",
    "StrategyGenerationError",
    "RiskAssessmentError",
    "SynthesisError",
    "StrategistAgent",
    "CriticAgent",
    "SynthesisEngine",
]
