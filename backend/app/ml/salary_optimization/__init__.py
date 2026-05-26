"""Salary optimization and compensation benchmarking.

Modules:
- market_analyzer: Job market data and trends
- benchmarking_engine: Compensation benchmarking
"""

from .market_analyzer import (
    JobMarketData,
    SalaryTrend,
    MarketAnalyzer,
)
from .benchmarking_engine import (
    CompensationBenchmark,
    NegotiationGuidance,
    BenchmarkingEngine,
)

__all__ = [
    "JobMarketData",
    "SalaryTrend",
    "MarketAnalyzer",
    "CompensationBenchmark",
    "NegotiationGuidance",
    "BenchmarkingEngine",
]
