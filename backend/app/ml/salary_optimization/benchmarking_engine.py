"""
Compensation Benchmarking Engine - Benchmark and negotiate compensation.

Provides:
- Compensation benchmarking
- Negotiation guidance
- Offer evaluation framework
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CompensationBenchmark:
    """Compensation benchmark analysis."""
    job_title: str
    location: str
    base_salary_p25: float
    base_salary_p50: float  # Median
    base_salary_p75: float
    bonus_percent_p50: float
    equity_grant_value: float
    total_comp_p50: float
    percentile_rank: float  # 0-1 scale where person ranks
    cost_of_living_adjusted: float
    confidence: float


@dataclass
class NegotiationGuidance:
    """Negotiation guidance and strategy."""
    current_offer_total_comp: float
    market_median_comp: float
    recommended_ask: float
    negotiation_strategy: List[str]
    leverage_points: List[str]
    risk_assessment: str  # "low", "moderate", "high"
    walk_away_number: float
    success_likelihood: float
    confidence: float


class BenchmarkingEngine:
    """
    Benchmarks compensation and provides negotiation guidance.
    """
    
    def __init__(self):
        """Initialize benchmarking engine."""
        self.logger = logger
    
    def benchmark_compensation(
        self,
        job_title: str,
        location: str,
        years_of_experience: int,
        skills: List[str],
        current_salary: Optional[float] = None,
    ) -> CompensationBenchmark:
        """
        Benchmark compensation against market.
        
        Args:
            job_title: Job title
            location: Geographic location
            years_of_experience: Years in role
            skills: Key skills possessed
            current_salary: Current salary (optional)
            
        Returns:
            CompensationBenchmark with market analysis
        """
        # Base market data (simplified)
        market_data = self._get_market_benchmarks(job_title, location)
        
        if not market_data:
            logger.warning(f"No benchmark data for {job_title} in {location}")
            return None
        
        # Adjust for experience
        experience_factor = self._experience_adjustment(years_of_experience)
        
        # Adjust for skills
        skill_premium = self._skill_premium_adjustment(skills)
        
        # Calculate percentiles
        p25 = market_data["p50"] * 0.80 * experience_factor * (1 + skill_premium)
        p50 = market_data["p50"] * experience_factor * (1 + skill_premium)
        p75 = market_data["p50"] * 1.25 * experience_factor * (1 + skill_premium)
        
        # Equity and bonus
        bonus = market_data.get("bonus_percent", 0.15) * p50
        equity = market_data.get("equity_value", 0)
        total_comp = p50 + bonus + equity
        
        # Determine percentile rank
        if current_salary:
            percentile = (current_salary - p25) / (p75 - p25) if p75 > p25 else 0.5
            percentile = max(0, min(1, percentile))
        else:
            percentile = 0.5
        
        # Cost of living adjustment
        col_index = market_data.get("cost_of_living", 1.0)
        adjusted_comp = total_comp / col_index
        
        return CompensationBenchmark(
            job_title=job_title,
            location=location,
            base_salary_p25=p25,
            base_salary_p50=p50,
            base_salary_p75=p75,
            bonus_percent_p50=market_data.get("bonus_percent", 0.15),
            equity_grant_value=equity,
            total_comp_p50=total_comp,
            percentile_rank=percentile,
            cost_of_living_adjusted=adjusted_comp,
            confidence=0.80,
        )
    
    def create_negotiation_strategy(
        self,
        current_offer_base: float,
        current_offer_bonus: float,
        current_offer_equity: float,
        market_benchmark: CompensationBenchmark,
        years_of_experience: int,
        leverage: str,  # "strong", "moderate", "weak"
    ) -> NegotiationGuidance:
        """
        Create negotiation strategy and guidance.
        
        Args:
            current_offer_base: Offered base salary
            current_offer_bonus: Offered bonus
            current_offer_equity: Offered equity value
            market_benchmark: Market benchmark data
            years_of_experience: Years of experience
            leverage: Negotiation leverage position
            
        Returns:
            NegotiationGuidance with strategy
        """
        current_total = current_offer_base + current_offer_bonus + current_offer_equity
        market_total = market_benchmark.total_comp_p50
        
        # Calculate recommended ask
        if leverage == "strong":
            # Target 75th percentile
            recommended_ask = market_benchmark.base_salary_p75 * 1.15
        elif leverage == "moderate":
            # Target 60th percentile
            recommended_ask = market_benchmark.base_salary_p50 * 1.10
        else:
            # Target 50th percentile
            recommended_ask = market_benchmark.base_salary_p50
        
        # Walk-away number (minimum acceptable)
        walk_away = market_benchmark.base_salary_p25 * 1.05
        
        # Generate strategy
        strategy = self._generate_negotiation_strategy(
            current_total, market_total, years_of_experience, leverage
        )
        
        # Identify leverage points
        leverage_points = self._identify_leverage_points(
            years_of_experience, current_total, market_total
        )
        
        # Risk assessment
        if leverage == "strong":
            risk = "low"
            success = 0.75
        elif leverage == "moderate":
            risk = "moderate"
            success = 0.50
        else:
            risk = "high"
            success = 0.30
        
        return NegotiationGuidance(
            current_offer_total_comp=current_total,
            market_median_comp=market_total,
            recommended_ask=recommended_ask,
            negotiation_strategy=strategy,
            leverage_points=leverage_points,
            risk_assessment=risk,
            walk_away_number=walk_away,
            success_likelihood=success,
            confidence=0.70,
        )
    
    def evaluate_offer(
        self,
        offer_base: float,
        offer_bonus: float,
        offer_equity: float,
        offer_equity_years: float,
        market_benchmark: CompensationBenchmark,
        cost_of_living_current: float,
        cost_of_living_new: float,
    ) -> Dict[str, float]:
        """
        Evaluate job offer against current situation.
        
        Args:
            offer_base: Offered base salary
            offer_bonus: Offered bonus
            offer_equity: Offered equity value
            offer_equity_years: Vesting period for equity
            market_benchmark: Market benchmark
            cost_of_living_current: Current cost of living index
            cost_of_living_new: New location cost of living index
            
        Returns:
            Offer evaluation metrics
        """
        # Total comp
        offer_total = offer_base + offer_bonus + offer_equity / offer_equity_years
        
        # Cost of living adjusted comparison
        col_adjusted_offer = offer_base / cost_of_living_new
        market_adjusted = market_benchmark.base_salary_p50 / cost_of_living_new
        
        # Percentile vs market
        percentile = (offer_base - market_benchmark.base_salary_p25) / (
            market_benchmark.base_salary_p75 - market_benchmark.base_salary_p25
        ) if market_benchmark.base_salary_p75 > market_benchmark.base_salary_p25 else 0.5
        
        # Risk factors
        upside = market_benchmark.base_salary_p75 - offer_base
        downside = max(0, market_benchmark.base_salary_p25 - offer_base)
        
        return {
            "offer_total_comp": offer_total,
            "market_median": market_benchmark.total_comp_p50,
            "percent_vs_market": (offer_total / market_benchmark.total_comp_p50 - 1) * 100,
            "percentile_vs_market": percentile,
            "cost_of_living_adjusted_base": col_adjusted_offer,
            "upside_potential": upside,
            "downside_risk": downside,
            "recommendation": "accept" if percentile >= 0.5 else "negotiate",
        }
    
    def _get_market_benchmarks(
        self,
        job_title: str,
        location: str,
    ) -> Optional[Dict]:
        """Get market benchmarks for job and location."""
        # Simplified market data
        benchmarks = {
            "Software Engineer": {
                "San Francisco": {
                    "p50": 180000,
                    "bonus_percent": 0.15,
                    "equity_value": 40000,
                    "cost_of_living": 1.85,
                },
                "New York": {
                    "p50": 165000,
                    "bonus_percent": 0.15,
                    "equity_value": 35000,
                    "cost_of_living": 1.70,
                },
                "Remote": {
                    "p50": 155000,
                    "bonus_percent": 0.10,
                    "equity_value": 30000,
                    "cost_of_living": 1.00,
                },
            },
            "Product Manager": {
                "San Francisco": {
                    "p50": 200000,
                    "bonus_percent": 0.20,
                    "equity_value": 50000,
                    "cost_of_living": 1.85,
                },
                "New York": {
                    "p50": 185000,
                    "bonus_percent": 0.20,
                    "equity_value": 45000,
                    "cost_of_living": 1.70,
                },
            },
        }
        
        return benchmarks.get(job_title, {}).get(location)
    
    def _experience_adjustment(self, years_experience: int) -> float:
        """Calculate experience adjustment factor."""
        if years_experience <= 2:
            return 0.80
        elif years_experience <= 5:
            return 1.00
        elif years_experience <= 10:
            return 1.20
        elif years_experience <= 15:
            return 1.40
        else:
            return 1.55
    
    def _skill_premium_adjustment(self, skills: List[str]) -> float:
        """Calculate skill premium adjustment."""
        premium = 0
        valuable_skills = ["AI/ML", "Leadership", "Strategic Planning"]
        
        for skill in skills:
            if skill in valuable_skills:
                premium += 0.10
        
        return min(0.30, premium)  # Cap at 30%
    
    def _generate_negotiation_strategy(
        self,
        current_total: float,
        market_total: float,
        years_exp: int,
        leverage: str,
    ) -> List[str]:
        """Generate negotiation strategy."""
        strategy = []
        
        if current_total < market_total * 0.90:
            strategy.append("Significant gap vs market: strong negotiation position")
        
        if leverage == "strong":
            strategy.append("Emphasize your unique value and accomplishments")
            strategy.append("Request detailed breakdown of equity/bonus")
            strategy.append("Negotiate base salary first, then equity refresh")
        elif leverage == "moderate":
            strategy.append("Focus negotiation on specific gaps vs market data")
            strategy.append("Propose phased equity vesting or refresh")
            strategy.append("Consider non-monetary benefits as trade-offs")
        else:
            strategy.append("Accept offer as competitive and market-aligned")
            strategy.append("Request review discussion after 6 months")
        
        return strategy
    
    def _identify_leverage_points(
        self,
        years_exp: int,
        current_comp: float,
        market_comp: float,
    ) -> List[str]:
        """Identify negotiation leverage points."""
        leverage = []
        
        if years_exp >= 10:
            leverage.append("Senior experience level")
        if current_comp < market_comp * 0.85:
            leverage.append("Significant market underpayment")
        if market_comp > 200000:
            leverage.append("High market salary room for negotiation")
        
        return leverage if leverage else ["Competitive market positioning"]
