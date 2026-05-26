"""
Type definitions for multi-agent reasoning system.
Defines data structures for agent inputs, outputs, and insights.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InsightType(str, Enum):
    """Types of financial insights."""
    SPENDING_PATTERN = "spending_pattern"
    BUDGET_OPTIMIZATION = "budget_optimization"
    SAVINGS_OPPORTUNITY = "savings_opportunity"
    RISK_ALERT = "risk_alert"
    GOAL_SUGGESTION = "goal_suggestion"
    FINANCIAL_HEALTH = "financial_health"
    ANOMALY_DETECTED = "anomaly_detected"
    RECOMMENDATION = "recommendation"


@dataclass
class FinancialMetrics:
    """Current user financial metrics."""
    total_income: float
    total_expenses: float
    savings_rate: float
    average_monthly_expense: float
    expense_categories: Dict[str, float]
    account_balances: Dict[str, float]
    recurring_expenses: float
    average_transaction_size: float
    transaction_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class TransactionContext:
    """Context about recent transactions."""
    recent_transactions: List[Dict[str, Any]]
    spending_trends: Dict[str, float]
    category_breakdown: Dict[str, Dict[str, float]]
    recurring_patterns: List[Dict[str, Any]]
    anomalies_detected: List[Dict[str, Any]]
    time_period: str = "30_days"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class StrategistOutput:
    """Output from Strategist Agent."""
    recommendations: List[str]
    budget_suggestions: Dict[str, float]
    savings_opportunities: List[Dict[str, Any]]
    goals_suggestions: List[Dict[str, Any]]
    spending_analysis: Dict[str, Any]
    confidence_score: float
    thinking_process: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "recommendations": self.recommendations,
            "budget_suggestions": self.budget_suggestions,
            "savings_opportunities": self.savings_opportunities,
            "goals_suggestions": self.goals_suggestions,
            "spending_analysis": self.spending_analysis,
            "confidence_score": self.confidence_score,
            "thinking_process": self.thinking_process,
        }


@dataclass
class CriticOutput:
    """Output from Critic Agent."""
    risk_level: RiskLevel
    risk_score: float  # 0-100
    vulnerabilities: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]
    financial_health_score: float  # 0-100
    critical_issues: List[str]
    recommendations: List[str]
    confidence_score: float
    thinking_process: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "risk_level": self.risk_level.value,
            "risk_score": self.risk_score,
            "vulnerabilities": self.vulnerabilities,
            "alerts": self.alerts,
            "financial_health_score": self.financial_health_score,
            "critical_issues": self.critical_issues,
            "recommendations": self.recommendations,
            "confidence_score": self.confidence_score,
            "thinking_process": self.thinking_process,
        }


@dataclass
class SynthesisOutput:
    """Combined output from Synthesis Engine."""
    executive_summary: str
    key_insights: List[Dict[str, Any]]
    action_items: List[Dict[str, Any]]
    priority_level: str  # critical, high, medium, low
    strategist_perspective: Dict[str, Any]
    critic_perspective: Dict[str, Any]
    overall_confidence: float
    generated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "executive_summary": self.executive_summary,
            "key_insights": self.key_insights,
            "action_items": self.action_items,
            "priority_level": self.priority_level,
            "strategist_perspective": self.strategist_perspective,
            "critic_perspective": self.critic_perspective,
            "overall_confidence": self.overall_confidence,
            "generated_at": self.generated_at.isoformat(),
        }


@dataclass
class FinancialInsight:
    """Single financial insight."""
    type: InsightType
    title: str
    description: str
    impact: str  # positive, negative, neutral
    confidence: float
    action: Optional[str] = None
    metric_value: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "title": self.title,
            "description": self.description,
            "impact": self.impact,
            "confidence": self.confidence,
            "action": self.action,
            "metric_value": self.metric_value,
        }


class AgentError(Exception):
    """Base exception for agent errors."""
    pass


class StrategyGenerationError(AgentError):
    """Error generating strategy."""
    pass


class RiskAssessmentError(AgentError):
    """Error assessing risk."""
    pass


class SynthesisError(AgentError):
    """Error synthesizing outputs."""
    pass
