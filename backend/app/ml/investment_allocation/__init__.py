"""
Investment Allocation Engine - Portfolio optimization and risk profiling.

Modules:
- portfolio_optimizer: Modern Portfolio Theory calculations
- risk_profiler: Risk tolerance assessment from behavioral data
- asset_analyzer: Asset class performance tracking
"""

from .portfolio_optimizer import (
    PortfolioMetrics,
    AllocationRecommendation,
    PortfolioOptimizer,
)
from .risk_profiler import (
    RiskProfile,
    BehavioralRiskProfile,
    RiskProfiler,
)
from .asset_analyzer import (
    AssetPerformance,
    AssetAnalysis,
    AssetAnalyzer,
)

__all__ = [
    "PortfolioMetrics",
    "AllocationRecommendation",
    "PortfolioOptimizer",
    "RiskProfile",
    "BehavioralRiskProfile",
    "RiskProfiler",
    "AssetPerformance",
    "AssetAnalysis",
    "AssetAnalyzer",
]
