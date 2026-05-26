"""
Wealth Scenario Modeler - Life event scenarios and wealth impact analysis.

Provides:
- Life event scenarios (marriage, kids, career change, health crisis)
- Wealth impact simulation
- Recovery planning
- Scenario comparison
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import numpy as np

logger = logging.getLogger(__name__)


class LifeEventType(str, Enum):
    """Types of life events."""
    MARRIAGE = "marriage"
    DIVORCE = "divorce"
    BABY = "baby"
    HOME_PURCHASE = "home_purchase"
    JOB_LOSS = "job_loss"
    CAREER_CHANGE = "career_change"
    HEALTH_CRISIS = "health_crisis"
    INHERITANCE = "inheritance"
    MAJOR_PURCHASE = "major_purchase"
    BUSINESS_LAUNCH = "business_launch"


@dataclass
class LifeEventScenario:
    """Impact of a life event on wealth."""
    event_type: LifeEventType
    event_year: int
    immediate_cost: float  # Initial impact
    ongoing_cost_annual: float  # Recurring annual impact
    duration_years: int
    wealth_recovery_timeline: int  # Years to recover
    opportunity_cost: float
    best_case_scenario: float
    worst_case_scenario: float
    mitigation_strategies: List[str]


@dataclass
class WealthScenarioAnalysis:
    """Wealth projection under scenario."""
    base_case_wealth: float
    scenario_wealth: float
    wealth_difference: float
    percent_impact: float
    key_events: List[str]
    recovery_path: Dict[str, float]  # Year -> wealth
    recommendations: List[str]
    confidence: float


class WealthScenarioModeler:
    """
    Models wealth under different life event scenarios.
    """
    
    # Life event impact templates
    EVENT_IMPACTS = {
        LifeEventType.MARRIAGE: {
            "immediate_cost": 30000,
            "ongoing_annual": 0,
            "duration": 0,
            "opportunity_cost": 0,
            "positive_factor": 1.5,  # Dual income potential
        },
        LifeEventType.BABY: {
            "immediate_cost": 15000,
            "ongoing_annual": 12000,
            "duration": 18,
            "opportunity_cost": 50000,  # Lost career income
            "positive_factor": 0.7,
        },
        LifeEventType.HOME_PURCHASE: {
            "immediate_cost": 50000,  # Down payment
            "ongoing_annual": 0,
            "duration": 0,
            "opportunity_cost": 200000,  # Mortgage interest
            "positive_factor": 2.0,  # Long-term appreciation
        },
        LifeEventType.JOB_LOSS: {
            "immediate_cost": 0,
            "ongoing_annual": 40000,  # Lost income
            "duration": 6,
            "opportunity_cost": 0,
            "positive_factor": 0.3,
        },
        LifeEventType.CAREER_CHANGE: {
            "immediate_cost": 20000,
            "ongoing_annual": 30000,  # Income reduction 2 years
            "duration": 2,
            "opportunity_cost": 60000,
            "positive_factor": 1.8,  # Long-term growth
        },
        LifeEventType.HEALTH_CRISIS: {
            "immediate_cost": 50000,
            "ongoing_annual": 15000,
            "duration": 3,
            "opportunity_cost": 0,
            "positive_factor": 0.0,
        },
        LifeEventType.INHERITANCE: {
            "immediate_cost": -100000,  # Gain
            "ongoing_annual": 0,
            "duration": 0,
            "opportunity_cost": 0,
            "positive_factor": 2.0,
        },
        LifeEventType.MAJOR_PURCHASE: {
            "immediate_cost": 40000,
            "ongoing_annual": 0,
            "duration": 0,
            "opportunity_cost": 5000,
            "positive_factor": 0.5,
        },
        LifeEventType.BUSINESS_LAUNCH: {
            "immediate_cost": 50000,
            "ongoing_annual": 30000,
            "duration": 3,
            "opportunity_cost": 100000,
            "positive_factor": 5.0,  # High upside potential
        },
    }
    
    def __init__(self):
        """Initialize wealth scenario modeler."""
        self.logger = logger
    
    def model_life_event(
        self,
        event_type: LifeEventType,
        event_year: int,
        current_wealth: float,
        annual_savings_rate: float,
        investment_return: float,
        current_age: int,
        retirement_age: int,
    ) -> WealthScenarioAnalysis:
        """
        Model wealth impact of a life event.
        
        Args:
            event_type: Type of life event
            event_year: Year event occurs
            current_wealth: Current wealth
            annual_savings_rate: Annual savings rate
            investment_return: Investment return %
            current_age: Current age
            retirement_age: Retirement age
            
        Returns:
            WealthScenarioAnalysis with impact assessment
        """
        impact_data = self.EVENT_IMPACTS.get(event_type)
        if not impact_data:
            logger.warning(f"Unknown event type: {event_type}")
            return None
        
        # Project base case (no event)
        years_to_retirement = retirement_age - current_age
        base_projection = self._project_wealth(
            current_wealth, annual_savings_rate, investment_return,
            years_to_retirement, annual_cost=0, cost_years=0
        )
        base_wealth = base_projection[-1]
        
        # Project with event
        event_impact = impact_data["immediate_cost"]
        ongoing_cost = impact_data["ongoing_annual"]
        cost_years = impact_data["duration"]
        
        scenario_projection = self._project_wealth(
            current_wealth, annual_savings_rate, investment_return,
            years_to_retirement, annual_cost=ongoing_cost, cost_years=cost_years,
            immediate_impact=event_impact, impact_year=event_year
        )
        scenario_wealth = scenario_projection[-1]
        
        # Calculate recovery path
        recovery_path = self._calculate_recovery_path(
            scenario_projection, base_projection
        )
        
        # Generate recommendations
        recommendations = self._generate_event_recommendations(event_type, current_wealth)
        
        return WealthScenarioAnalysis(
            base_case_wealth=base_wealth,
            scenario_wealth=scenario_wealth,
            wealth_difference=base_wealth - scenario_wealth,
            percent_impact=(base_wealth - scenario_wealth) / base_wealth * 100 if base_wealth > 0 else 0,
            key_events=[f"{event_type.value} in year {event_year}"],
            recovery_path=recovery_path,
            recommendations=recommendations,
            confidence=0.70,
        )
    
    def model_combined_events(
        self,
        events: List[tuple],  # [(event_type, year), ...]
        current_wealth: float,
        annual_savings_rate: float,
        investment_return: float,
        current_age: int,
        retirement_age: int,
    ) -> WealthScenarioAnalysis:
        """
        Model wealth impact of multiple combined events.
        
        Args:
            events: List of (event_type, year) tuples
            current_wealth: Current wealth
            annual_savings_rate: Annual savings rate
            investment_return: Investment return %
            current_age: Current age
            retirement_age: Retirement age
            
        Returns:
            WealthScenarioAnalysis with combined impact
        """
        years_to_retirement = retirement_age - current_age
        
        # Project base case
        base_projection = self._project_wealth(
            current_wealth, annual_savings_rate, investment_return,
            years_to_retirement, annual_cost=0, cost_years=0
        )
        base_wealth = base_projection[-1]
        
        # Project with events
        wealth = current_wealth
        event_descriptions = []
        
        for event_type, year in sorted(events, key=lambda x: x[1]):
            impact_data = self.EVENT_IMPACTS.get(event_type)
            if impact_data:
                wealth -= impact_data["immediate_cost"]
                event_descriptions.append(f"{event_type.value} in year {year}")
        
        # Continue projecting
        remaining_years = years_to_retirement - (min([y for _, y in events]) if events else 0)
        final_projection = self._project_wealth(
            wealth, annual_savings_rate, investment_return, remaining_years
        )
        scenario_wealth = final_projection[-1] if final_projection else wealth
        
        return WealthScenarioAnalysis(
            base_case_wealth=base_wealth,
            scenario_wealth=scenario_wealth,
            wealth_difference=base_wealth - scenario_wealth,
            percent_impact=(base_wealth - scenario_wealth) / base_wealth * 100 if base_wealth > 0 else 0,
            key_events=event_descriptions,
            recovery_path={},
            recommendations=["Diversify income sources", "Build larger emergency fund", "Consider insurance"],
            confidence=0.60,
        )
    
    def _project_wealth(
        self,
        starting_wealth: float,
        savings_rate: float,
        investment_return: float,
        years: int,
        annual_cost: float = 0,
        cost_years: int = 0,
        immediate_impact: float = 0,
        impact_year: int = 0,
    ) -> List[float]:
        """Project wealth over time with optional costs."""
        wealth = starting_wealth - immediate_impact  # Apply immediate impact
        projection = [wealth]
        
        for year in range(1, years + 1):
            # Savings and investment growth
            annual_savings = wealth * savings_rate
            investment_growth = wealth * investment_return
            
            # Reduce for ongoing costs
            ongoing_cost = annual_cost if year <= cost_years + impact_year else 0
            
            wealth = wealth + annual_savings + investment_growth - ongoing_cost
            projection.append(max(0, wealth))
        
        return projection
    
    def _calculate_recovery_path(
        self,
        scenario: List[float],
        base_case: List[float],
    ) -> Dict[str, float]:
        """Calculate years to recovery from event."""
        recovery = {}
        
        for i in range(len(scenario)):
            gap = base_case[i] - scenario[i]
            recovery[f"year_{i}"] = gap
        
        # Find breakeven year
        for i in range(len(scenario)):
            if scenario[i] >= base_case[i] * 0.95:  # Within 5%
                recovery["recovery_year"] = i
                break
        
        return recovery
    
    def _generate_event_recommendations(
        self,
        event_type: LifeEventType,
        current_wealth: float,
    ) -> List[str]:
        """Generate recommendations for specific event."""
        recommendations = []
        
        if event_type == LifeEventType.JOB_LOSS:
            # Check emergency fund adequacy
            if current_wealth < 60000:
                recommendations.append("Build larger emergency fund (6 months expenses)")
            recommendations.append("Expand professional network proactively")
            recommendations.append("Consider transition to more stable industry")
        
        elif event_type == LifeEventType.HEALTH_CRISIS:
            recommendations.append("Secure comprehensive health insurance")
            recommendations.append("Build health-specific emergency fund")
            recommendations.append("Review disability insurance coverage")
        
        elif event_type == LifeEventType.HOME_PURCHASE:
            recommendations.append("Ensure adequate mortgage insurance")
            recommendations.append("Plan for higher property taxes and maintenance")
            recommendations.append("Maintain separate emergency fund for home repairs")
        
        elif event_type == LifeEventType.BABY:
            recommendations.append("Increase life insurance coverage")
            recommendations.append("Open 529 college savings plan early")
            recommendations.append("Consider flexible work arrangements")
        
        elif event_type == LifeEventType.BUSINESS_LAUNCH:
            recommendations.append("Separate personal and business finances")
            recommendations.append("Maintain personal emergency fund independently")
            recommendations.append("Plan for variable income cycles")
        
        else:
            recommendations.append("Review financial plan post-event")
            recommendations.append("Adjust budget and savings targets")
        
        return recommendations
    
    def compare_scenarios(
        self,
        base_wealth: float,
        savings_rate: float,
        investment_return: float,
        years: int,
        scenarios: Dict[str, Dict],  # {scenario_name: {events: [], etc.}}
    ) -> Dict[str, dict]:
        """
        Compare multiple scenarios.
        
        Args:
            base_wealth: Starting wealth
            savings_rate: Savings rate
            investment_return: Investment return
            years: Years to project
            scenarios: Dict of scenarios to compare
            
        Returns:
            Comparison results
        """
        results = {}
        
        for scenario_name, scenario_data in scenarios.items():
            annual_cost = scenario_data.get("annual_cost", 0)
            cost_years = scenario_data.get("cost_years", 0)
            immediate = scenario_data.get("immediate", 0)
            
            projection = self._project_wealth(
                base_wealth, savings_rate, investment_return, years,
                annual_cost=annual_cost, cost_years=cost_years,
                immediate_impact=immediate
            )
            
            results[scenario_name] = {
                "final_wealth": projection[-1],
                "wealth_path": projection,
            }
        
        return results
