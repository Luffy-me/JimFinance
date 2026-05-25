"""
Scenario Analyzer - Multi-tier financial scenario generation.
Provides conservative, balanced, and aggressive recommendations with modeling.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

import numpy as np

logger = logging.getLogger(__name__)


class ScenarioType(str, Enum):
    """Scenario types."""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"


@dataclass
class Scenario:
    """Single financial scenario."""
    type: ScenarioType
    probability: float  # 0-1
    description: str
    assumptions: List[str]
    projected_runway_months: float
    recommendation: str
    confidence: float
    monthly_savings_target: float
    stress_level: str  # low, medium, high, critical
    action_items: List[str]


class ScenarioAnalyzer:
    """
    Generates three-tier scenarios for financial decisions.
    Conservative, Balanced, and Aggressive provide complete decision space.
    """
    
    def __init__(self):
        """Initialize scenario analyzer."""
        self.logger = logger
    
    def generate_scenarios(
        self,
        monthly_income: float,
        monthly_expenses: float,
        current_balance: float,
        burn_rate_trend: float = 0.0,  # -1 to 1 indicating trend
        monthly_recurring: float = 0.0,
        account_volatility: float = 0.5,  # 0-1
        is_employed: bool = True,
        months_employed: float = 12.0,
    ) -> List[Scenario]:
        """
        Generate three scenarios for financial decision.
        
        Args:
            monthly_income: Monthly gross income
            monthly_expenses: Current monthly expenses
            current_balance: Current account balance
            burn_rate_trend: -1 to 1, indicates if expenses are growing/shrinking
            monthly_recurring: Fixed recurring expenses per month
            account_volatility: 0-1, spending volatility
            is_employed: Whether person is employed
            months_employed: How long in current job
            
        Returns:
            List of three Scenario objects (conservative, balanced, aggressive)
        """
        scenarios = []
        
        # Conservative Scenario (worst case planning)
        conservative = self._generate_conservative_scenario(
            monthly_income,
            monthly_expenses,
            current_balance,
            burn_rate_trend,
            monthly_recurring,
            is_employed,
            months_employed,
        )
        scenarios.append(conservative)
        
        # Balanced Scenario (most likely case)
        balanced = self._generate_balanced_scenario(
            monthly_income,
            monthly_expenses,
            current_balance,
            burn_rate_trend,
            monthly_recurring,
            account_volatility,
        )
        scenarios.append(balanced)
        
        # Aggressive Scenario (best case upside)
        aggressive = self._generate_aggressive_scenario(
            monthly_income,
            monthly_expenses,
            current_balance,
            burn_rate_trend,
            monthly_recurring,
            is_employed,
        )
        scenarios.append(aggressive)
        
        return scenarios
    
    def _generate_conservative_scenario(
        self,
        monthly_income: float,
        monthly_expenses: float,
        current_balance: float,
        burn_rate_trend: float,
        monthly_recurring: float,
        is_employed: bool,
        months_employed: float,
    ) -> Scenario:
        """
        Conservative scenario: Assumes worst case, income loss, expense growth.
        Planning assumption: prepare for job loss or income reduction.
        """
        # Assume 15% income reduction (recession/cut/hours)
        conservative_income = monthly_income * 0.85
        
        # Assume expenses grow 10% from trend
        trend_multiplier = max(0.95, 1.0 + burn_rate_trend * 0.5)
        conservative_expenses = monthly_expenses * trend_multiplier * 1.10
        
        # Calculate runway
        burn_monthly = max(0, conservative_expenses - conservative_income)
        runway = current_balance / burn_monthly if burn_monthly > 0 else float('inf')
        
        # Assess employment stability
        job_risk_factor = 1.0
        if not is_employed:
            job_risk_factor = 1.5  # No income
        elif months_employed < 12:
            job_risk_factor = 1.2  # New job (higher risk)
        
        stressed_runway = runway / job_risk_factor
        
        # Determine stress level
        if stressed_runway < 1:
            stress = "critical"
            recommendation = "IMMEDIATE ACTION REQUIRED: Your runway is critically short. Reduce expenses immediately or increase income."
        elif stressed_runway < 3:
            stress = "high"
            recommendation = "Build emergency fund to 6 months of expenses. Implement expense reductions now."
        elif stressed_runway < 6:
            stress = "medium"
            recommendation = "Increase savings rate to reach 6-month emergency fund."
        else:
            stress = "low"
            recommendation = "Continue current savings. Monitor spending patterns for opportunities."
        
        # Action items
        actions = [
            "Build emergency fund to 6 months of expenses",
            "Review and reduce discretionary spending",
            "Create backup income plan (freelance/side gig)",
            "Review insurance coverage",
            "Cut or reduce subscriptions",
        ]
        
        if stressed_runway < 3:
            actions.insert(0, "URGENT: Reduce monthly expenses immediately")
        
        return Scenario(
            type=ScenarioType.CONSERVATIVE,
            probability=0.25,  # 25% chance of downturn
            description="Worst case: Income reduced 15%, expenses grow 10%, potential job loss",
            assumptions=[
                "Income reduced to 85% of current (recession, reduced hours)",
                f"Monthly expenses grow {10 + int(burn_rate_trend*5)}% (trend adjustment)",
                "Job stability risk factored in",
                "No one-time windfalls or bonuses",
                "Emergency fund requirement: 6 months",
            ],
            projected_runway_months=stressed_runway,
            recommendation=recommendation,
            confidence=0.85,
            monthly_savings_target=max(0, (conservative_income * 0.20) - conservative_expenses),
            stress_level=stress,
            action_items=actions,
        )
    
    def _generate_balanced_scenario(
        self,
        monthly_income: float,
        monthly_expenses: float,
        current_balance: float,
        burn_rate_trend: float,
        monthly_recurring: float,
        account_volatility: float,
    ) -> Scenario:
        """
        Balanced scenario: Current trajectory continues.
        Planning assumption: status quo continues.
        """
        # Assume slight expense adjustment based on trend
        trend_multiplier = 1.0 + (burn_rate_trend * 0.25)
        balanced_expenses = monthly_expenses * trend_multiplier
        
        burn_monthly = max(0, balanced_expenses - monthly_income)
        runway = current_balance / burn_monthly if burn_monthly > 0 else float('inf')
        
        # Volatility adjustment to confidence
        confidence_adjustment = 1.0 - (account_volatility * 0.2)
        
        # Determine stress level
        if runway < 3:
            stress = "high"
            recommendation = "Build emergency fund while maintaining current income. Target 3-6 month savings."
        elif runway < 6:
            stress = "medium"
            recommendation = "Good trajectory. Optimize budget categories and increase savings rate to 15-20%."
        else:
            stress = "low"
            recommendation = "Healthy position. Focus on long-term wealth building and goal achievement."
        
        # Action items
        actions = [
            "Continue current saving patterns",
            "Review category spending for optimization opportunities",
            "Consider increasing income through promotions or side projects",
            "Plan for financial goals (vacation, major purchase, investment)",
            "Review and rebalance budget quarterly",
        ]
        
        savings_potential = (monthly_income - balanced_expenses) * 0.5  # Conservative savings
        
        return Scenario(
            type=ScenarioType.BALANCED,
            probability=0.50,  # 50% chance (most likely)
            description="Most likely: Current income and spending patterns continue",
            assumptions=[
                "Income remains stable at current level",
                f"Expenses trend naturally ({burn_rate_trend*100:+.1f}% trend)",
                "Current employment continues",
                "Spending volatility: moderate",
                "No major one-time expenses",
            ],
            projected_runway_months=runway,
            recommendation=recommendation,
            confidence=max(0.65, 0.85 * confidence_adjustment),
            monthly_savings_target=max(0, monthly_income - balanced_expenses),
            stress_level=stress,
            action_items=actions,
        )
    
    def _generate_aggressive_scenario(
        self,
        monthly_income: float,
        monthly_expenses: float,
        current_balance: float,
        burn_rate_trend: float,
        monthly_recurring: float,
        is_employed: bool,
    ) -> Scenario:
        """
        Aggressive scenario: Income growth, expense control, opportunity upside.
        Planning assumption: optimize finances, pursue growth.
        """
        # Assume 20% income increase (promotion, raise, side income)
        aggressive_income = monthly_income * 1.20
        
        # Assume expenses reduce 15% through optimization
        aggressive_expenses = monthly_expenses * 0.85
        
        burn_monthly = max(0, aggressive_expenses - aggressive_income)
        runway = current_balance / burn_monthly if burn_monthly > 0 else float('inf')
        
        # Maximum runway potential
        if runway > 12:
            stress = "low"
            recommendation = "Excellent position! Pursue wealth-building: invest, build passive income, pursue goals."
        elif runway > 6:
            stress = "low"
            recommendation = "Strong position. Increase investment rate and pursue financial goals."
        else:
            stress = "medium"
            recommendation = "Good potential. Execute optimization plan to unlock full savings capacity."
        
        # Action items
        actions = [
            "Execute expense reduction plan (target: reduce 15%)",
            "Pursue income growth (raise, promotion, side business)",
            "Increase savings rate to 25-30%",
            "Start investing excess cash (index funds, retirement)",
            "Build wealth through multiple income streams",
            "Plan major goals: home, education, sabbatical",
        ]
        
        return Scenario(
            type=ScenarioType.AGGRESSIVE,
            probability=0.25,  # 25% chance of upside
            description="Best case: Income +20%, expenses optimized -15%, growth mode activated",
            assumptions=[
                "Income grows 20% (promotion, raise, side income)",
                "Expenses reduce 15% through optimization",
                "Discretionary spending cut by 20%",
                "Employment stability maintained",
                "Savings rate reaches 25-30%",
                "Aggressive goal pursuit begins",
            ],
            projected_runway_months=runway,
            recommendation=recommendation,
            confidence=0.70,
            monthly_savings_target=max(0, aggressive_income - aggressive_expenses),
            stress_level=stress,
            action_items=actions,
        )
    
    def affordability_analysis(
        self,
        purchase_price: float,
        monthly_payment: Optional[float] = None,
        months_to_pay: int = 1,
        current_balance: float = 0.0,
        monthly_income: float = 0.0,
        monthly_expenses: float = 0.0,
        emergency_fund_target: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Analyze if a purchase is affordable.
        Example: "Can I afford iPhone for ₽120,000?"
        
        Args:
            purchase_price: Total purchase price
            monthly_payment: If financing, monthly payment required
            months_to_pay: Financing period in months
            current_balance: Current account balance
            monthly_income: Monthly income
            monthly_expenses: Monthly expenses
            emergency_fund_target: Emergency fund goal (3-6 months expenses)
            
        Returns:
            Dictionary with affordability analysis across all scenarios
        """
        # Generate scenarios first
        scenarios = self.generate_scenarios(
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            current_balance=current_balance,
            monthly_recurring=monthly_expenses * 0.7,  # Estimate recurring
        )
        
        affordability_results = {
            "purchase_price": purchase_price,
            "purchase_type": "lump_sum" if monthly_payment is None else "financed",
            "analysis_date": datetime.utcnow().isoformat(),
            "scenarios": {},
        }
        
        for scenario in scenarios:
            result = self._analyze_affordability_scenario(
                scenario=scenario,
                purchase_price=purchase_price,
                monthly_payment=monthly_payment,
                months_to_pay=months_to_pay,
                current_balance=current_balance,
                monthly_income=monthly_income,
                monthly_expenses=monthly_expenses,
                emergency_fund_target=emergency_fund_target,
            )
            affordability_results["scenarios"][scenario.type.value] = result
        
        return affordability_results
    
    def _analyze_affordability_scenario(
        self,
        scenario: Scenario,
        purchase_price: float,
        monthly_payment: Optional[float],
        months_to_pay: int,
        current_balance: float,
        monthly_income: float,
        monthly_expenses: float,
        emergency_fund_target: float,
    ) -> Dict[str, Any]:
        """Analyze affordability for single scenario."""
        
        # Check if can afford lump sum
        if monthly_payment is None:
            # Lump sum purchase
            can_afford_lump = (current_balance - purchase_price) > emergency_fund_target
            
            return {
                "can_afford": can_afford_lump,
                "reason": (
                    "Sufficient balance after emergency fund"
                    if can_afford_lump
                    else "Would deplete emergency fund or savings"
                ),
                "balance_after": current_balance - purchase_price,
                "impact_on_runway": scenario.projected_runway_months,
                "recommendation": (
                    "Purchase is affordable"
                    if can_afford_lump
                    else "Recommend postponing or financing"
                ),
                "confidence": 0.95 if can_afford_lump else 0.90,
            }
        else:
            # Financed purchase
            total_paid = monthly_payment * months_to_pay
            
            # Check if monthly payments fit in budget
            monthly_surplus = monthly_income - monthly_expenses
            payment_to_income_ratio = monthly_payment / monthly_income if monthly_income > 0 else 1.0
            
            can_afford = (
                monthly_payment <= monthly_surplus * 0.75 and
                payment_to_income_ratio <= 0.20  # Payment <20% of income
            )
            
            return {
                "can_afford": can_afford,
                "monthly_payment": monthly_payment,
                "months_to_pay": months_to_pay,
                "total_cost": total_paid,
                "payment_to_income_ratio": payment_to_income_ratio,
                "reason": (
                    f"Monthly payment ({monthly_payment}) fits budget"
                    if can_afford
                    else f"Monthly payment exceeds safe threshold"
                ),
                "impact_on_runway": (
                    scenario.projected_runway_months - (monthly_payment / (monthly_income - monthly_expenses))
                    if (monthly_income - monthly_expenses) > 0
                    else scenario.projected_runway_months
                ),
                "recommendation": (
                    "Purchase is affordable with financing"
                    if can_afford
                    else "Not recommended - exceeds debt-to-income threshold"
                ),
                "confidence": 0.85 if can_afford else 0.90,
            }
