"""
Macro Scenario Modeler - Stress test scenarios and macro shock analysis.

Provides:
- Macro scenario definitions
- Stress test impact modeling
- Portfolio impact assessment
- Recovery timeline estimation
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import numpy as np

logger = logging.getLogger(__name__)


class MacroScenarioType(str, Enum):
    """Macro scenario types."""
    BASE_CASE = "base_case"
    SOFT_LANDING = "soft_landing"
    HARD_LANDING = "hard_landing"
    STAGFLATION = "stagflation"
    DEFLATION = "deflation"
    FINANCIAL_CRISIS = "financial_crisis"


@dataclass
class MacroScenario:
    """Macro scenario definition."""
    scenario_type: MacroScenarioType
    probability: float  # 0-1
    gdp_growth_impact: float  # Percent change
    unemployment_change: float  # Percent point change
    inflation_rate: float  # Resulting inflation rate
    interest_rate_change: float  # Percent point change
    stock_market_impact: float  # Percent change
    bond_market_impact: float  # Percent change
    currency_impact: float  # Percent change
    duration_months: int
    description: str


@dataclass
class StressTestResult:
    """Stress test impact assessment."""
    scenario: MacroScenario
    portfolio_impact: float  # Percent change in portfolio value
    asset_impacts: Dict[str, float]  # Asset class impacts
    cash_flow_impact: Dict[str, float]  # Monthly cash flow impacts
    recommended_adjustments: List[str]
    recovery_timeline_months: int
    confidence: float
    assumptions: List[str]


class ScenarioModeler:
    """
    Models macro scenarios and stress tests.
    """
    
    # Pre-defined scenarios with historical analogs
    SCENARIO_DEFINITIONS = {
        MacroScenarioType.SOFT_LANDING: MacroScenario(
            scenario_type=MacroScenarioType.SOFT_LANDING,
            probability=0.40,
            gdp_growth_impact=-0.01,
            unemployment_change=0.50,
            inflation_rate=0.025,
            interest_rate_change=-0.01,
            stock_market_impact=0.05,
            bond_market_impact=0.10,
            currency_impact=0.00,
            duration_months=6,
            description="Moderate slowdown with controlled inflation"
        ),
        MacroScenarioType.HARD_LANDING: MacroScenario(
            scenario_type=MacroScenarioType.HARD_LANDING,
            probability=0.25,
            gdp_growth_impact=-0.03,
            unemployment_change=1.50,
            inflation_rate=0.015,
            interest_rate_change=-0.025,
            stock_market_impact=-0.20,
            bond_market_impact=-0.10,
            currency_impact=-0.05,
            duration_months=18,
            description="Sharp recession with rising unemployment"
        ),
        MacroScenarioType.STAGFLATION: MacroScenario(
            scenario_type=MacroScenarioType.STAGFLATION,
            probability=0.15,
            gdp_growth_impact=-0.02,
            unemployment_change=1.00,
            inflation_rate=0.06,
            interest_rate_change=0.025,
            stock_market_impact=-0.25,
            bond_market_impact=-0.15,
            currency_impact=-0.10,
            duration_months=24,
            description="Recession with high inflation"
        ),
        MacroScenarioType.FINANCIAL_CRISIS: MacroScenario(
            scenario_type=MacroScenarioType.FINANCIAL_CRISIS,
            probability=0.10,
            gdp_growth_impact=-0.05,
            unemployment_change=2.50,
            inflation_rate=0.010,
            interest_rate_change=-0.03,
            stock_market_impact=-0.40,
            bond_market_impact=-0.25,
            currency_impact=-0.20,
            duration_months=36,
            description="Severe financial crisis with systemic impacts"
        ),
        MacroScenarioType.DEFLATION: MacroScenario(
            scenario_type=MacroScenarioType.DEFLATION,
            probability=0.05,
            gdp_growth_impact=-0.04,
            unemployment_change=2.00,
            inflation_rate=-0.02,
            interest_rate_change=-0.04,
            stock_market_impact=-0.30,
            bond_market_impact=0.15,
            currency_impact=0.10,
            duration_months=36,
            description="Deflationary environment with debt stress"
        ),
    }
    
    def __init__(self):
        """Initialize scenario modeler."""
        self.logger = logger
    
    def get_scenario(self, scenario_type: MacroScenarioType) -> Optional[MacroScenario]:
        """Get pre-defined scenario."""
        return self.SCENARIO_DEFINITIONS.get(scenario_type)
    
    def stress_test_portfolio(
        self,
        scenario: MacroScenario,
        portfolio_allocation: Dict[str, float],  # {asset_class: allocation}
    ) -> StressTestResult:
        """
        Stress test portfolio against macro scenario.
        
        Args:
            scenario: Macro scenario to test
            portfolio_allocation: Portfolio asset allocation
            
        Returns:
            StressTestResult with impact assessment
        """
        # Calculate asset impacts
        asset_impacts = self._calculate_asset_impacts(scenario, portfolio_allocation)
        
        # Calculate overall portfolio impact
        portfolio_impact = sum(
            allocation * asset_impacts.get(asset_class, 0)
            for asset_class, allocation in portfolio_allocation.items()
        )
        
        # Calculate monthly cash flow impacts
        monthly_impacts = self._calculate_monthly_impacts(scenario)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(scenario, asset_impacts)
        
        # Estimate recovery timeline
        recovery_months = self._estimate_recovery(scenario, portfolio_impact)
        
        assumptions = [
            f"Scenario: {scenario.description}",
            "Based on historical scenario analysis",
            "Assumes no policy intervention",
            "Does not include hedging strategies",
            "Correlation assumptions may not hold in crisis",
        ]
        
        return StressTestResult(
            scenario=scenario,
            portfolio_impact=portfolio_impact,
            asset_impacts=asset_impacts,
            cash_flow_impact=monthly_impacts,
            recommended_adjustments=recommendations,
            recovery_timeline_months=recovery_months,
            confidence=0.70,
            assumptions=assumptions,
        )
    
    def _calculate_asset_impacts(
        self,
        scenario: MacroScenario,
        portfolio_allocation: Dict[str, float],
    ) -> Dict[str, float]:
        """Calculate impact on each asset class."""
        impacts = {}
        
        # Stock impacts
        impacts["stocks_us"] = scenario.stock_market_impact * 1.0
        impacts["stocks_intl"] = scenario.stock_market_impact * 1.1
        
        # Bond impacts
        impacts["bonds"] = scenario.bond_market_impact
        impacts["high_yield"] = scenario.bond_market_impact * 1.5
        
        # Commodity impacts
        if scenario.scenario_type == MacroScenarioType.STAGFLATION:
            impacts["commodities"] = 0.10  # Hedge benefit
        else:
            impacts["commodities"] = scenario.gdp_growth_impact * 2.0
        
        # Real estate impacts
        impacts["real_estate"] = scenario.gdp_growth_impact * 1.2
        
        # Currency impacts
        impacts["currency"] = scenario.currency_impact
        
        # Cash remains stable
        impacts["cash"] = 0.00
        
        return impacts
    
    def _calculate_monthly_impacts(self, scenario: MacroScenario) -> Dict[str, float]:
        """Calculate monthly cash flow impacts."""
        monthly_impacts = {}
        monthly_decline = scenario.gdp_growth_impact / scenario.duration_months
        
        for month in range(scenario.duration_months):
            monthly_impacts[f"month_{month+1}"] = monthly_decline * (month + 1)
        
        return monthly_impacts
    
    def _generate_recommendations(
        self,
        scenario: MacroScenario,
        asset_impacts: Dict[str, float],
    ) -> List[str]:
        """Generate portfolio recommendations for scenario."""
        recommendations = []
        
        if scenario.scenario_type in [MacroScenarioType.HARD_LANDING, MacroScenarioType.FINANCIAL_CRISIS]:
            recommendations.append("Increase defensive positioning (bonds, cash)")
            recommendations.append("Consider quality equity bias")
            recommendations.append("Reduce leverage and margin exposure")
        
        if scenario.scenario_type == MacroScenarioType.STAGFLATION:
            recommendations.append("Increase inflation hedges (commodities, TIPS)")
            recommendations.append("Consider real assets (real estate, infrastructure)")
            recommendations.append("Avoid long-duration bonds")
        
        if scenario.scenario_type == MacroScenarioType.DEFLATION:
            recommendations.append("Increase bond duration")
            recommendations.append("Reduce commodity exposure")
            recommendations.append("Monitor debt service capacity")
        
        if scenario.stock_market_impact < -0.20:
            recommendations.append("Consider rebalancing to target allocation")
            recommendations.append("Dollar-cost average into equities if timeframe allows")
        
        return recommendations
    
    def _estimate_recovery(self, scenario: MacroScenario, portfolio_impact: float) -> int:
        """Estimate recovery timeline in months."""
        # Rough heuristic based on scenario severity
        base_recovery = scenario.duration_months
        
        # Deeper declines take longer to recover
        if portfolio_impact < -0.30:
            base_recovery *= 1.5
        elif portfolio_impact < -0.15:
            base_recovery *= 1.2
        
        return int(base_recovery)
    
    def run_scenario_analysis(
        self,
        portfolio_allocation: Dict[str, float],
    ) -> Dict[str, StressTestResult]:
        """
        Run full scenario analysis across all scenarios.
        
        Args:
            portfolio_allocation: Portfolio asset allocation
            
        Returns:
            Dict mapping scenario types to results
        """
        results = {}
        
        for scenario_type, scenario in self.SCENARIO_DEFINITIONS.items():
            result = self.stress_test_portfolio(scenario, portfolio_allocation)
            results[scenario_type] = result
        
        return results
