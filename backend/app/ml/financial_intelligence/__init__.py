"""
Financial Intelligence Module - Advanced financial analytics engine.

Provides mathematically rigorous financial analysis with confidence scoring and explainability.

Components:
- metrics: Financial metrics engine with confidence scoring
- merchant_intelligence: Merchant profiling and analysis
- subscription_analyzer: Recurring payment pattern detection
- runway_engine: Financial runway calculations with scenarios
- cashflow_analyzer: Cashflow pattern and velocity analysis
- forecaster: Time series forecasting for spending and income
- behavioral_analyzer: Spending behavior clustering and insights
"""

from .metrics import FinancialMetricsEngine, FinancialMetrics, Metric
from .merchant_intelligence import MerchantIntelligenceSystem, MerchantProfile
from .subscription_analyzer import SubscriptionAnalyzer, SubscriptionProfile
from .runway_engine import FinancialRunwayEngine, RunwayAnalysis, RunwayScenario
from .cashflow_analyzer import CashflowAnalyzer, CashflowMetrics
from .forecaster import ForecastingEngine, Forecast, CategoryForecast
from .behavioral_analyzer import BehavioralAnalyzer, BehaviorInsight

__all__ = [
    # Metrics
    'FinancialMetricsEngine',
    'FinancialMetrics',
    'Metric',
    # Merchant Intelligence
    'MerchantIntelligenceSystem',
    'MerchantProfile',
    # Subscriptions
    'SubscriptionAnalyzer',
    'SubscriptionProfile',
    # Runway
    'FinancialRunwayEngine',
    'RunwayAnalysis',
    'RunwayScenario',
    # Cashflow
    'CashflowAnalyzer',
    'CashflowMetrics',
    # Forecasting
    'ForecastingEngine',
    'Forecast',
    'CategoryForecast',
    # Behavioral Analysis
    'BehavioralAnalyzer',
    'BehaviorInsight',
]
