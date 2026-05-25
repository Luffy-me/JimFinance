"""
Financial Decision Analyzer - Quantitative analysis for purchase decisions.
Analyzes affordability, opportunity cost, and impact on financial health.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from app.ml.financial_reasoning.quantitative_engine import (
    QuantitativeEngine,
    QuantitativeMetric,
)
from app.ml.financial_reasoning.scenario_analyzer import (
    ScenarioAnalyzer,
    ScenarioType,
)
from app.ml.financial_reasoning.probability_engine import ProbabilityEngine

logger = logging.getLogger(__name__)


class DecisionRecommendation(str, Enum):
    """Decision recommendation levels."""
    HIGHLY_RECOMMENDED = "highly_recommended"
    RECOMMENDED = "recommended"
    NEUTRAL = "neutral"
    NOT_RECOMMENDED = "not_recommended"
    STRONGLY_NOT_RECOMMENDED = "strongly_not_recommended"


@dataclass
class FinancialImpact:
    """Impact of a decision on financial health."""
    impact_type: str  # runway, savings_rate, debt_to_income, etc.
    current_value: float
    projected_value: float  # After purchase
    percentage_change: float
    severity: str  # minimal, moderate, significant, critical


class DecisionAnalyzer:
    """
    Analyzes financial decisions with quantitative rigor.
    Determines affordability, impact, and provides recommendation.
    """
    
    def __init__(self):
        """Initialize decision analyzer."""
        self.logger = logger
        self.quant_engine = QuantitativeEngine()
        self.scenario_analyzer = ScenarioAnalyzer()
        self.probability_engine = ProbabilityEngine()
    
    def analyze_decision(
        self,
        decision_name: str,
        decision_description: str,
        purchase_price: float,
        monthly_payment: Optional[float] = None,
        months_to_pay: int = 1,
        # User financial state
        monthly_income: float = 0.0,
        monthly_expenses: float = 0.0,
        current_balance: float = 0.0,
        recurring_expenses: float = 0.0,
        transactions: List[Dict] = None,
        # Risk parameters
        emergency_fund_months: int = 6,
        max_debt_to_income: float = 0.30,
    ) -> Dict[str, Any]:
        """
        Comprehensive financial decision analysis.
        
        Args:
            decision_name: Name of decision (e.g., "iPhone Purchase")
            decision_description: Description of purchase/decision
            purchase_price: Total price or amount being considered
            monthly_payment: For financed purchases
            months_to_pay: Financing period in months
            monthly_income: Monthly gross income
            monthly_expenses: Current monthly expenses
            current_balance: Current account balance
            recurring_expenses: Fixed recurring monthly expenses
            transactions: Transaction history for trend analysis
            emergency_fund_months: Emergency fund requirement (3-6 months)
            max_debt_to_income: Maximum acceptable debt-to-income ratio
            
        Returns:
            Comprehensive decision analysis
        """
        transactions = transactions or []
        
        # Step 1: Calculate quantitative metrics
        metrics = self._calculate_metrics(
            monthly_income,
            monthly_expenses,
            current_balance,
            transactions,
        )
        
        # Step 2: Generate scenarios
        scenarios = self.scenario_analyzer.generate_scenarios(
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            current_balance=current_balance,
            monthly_recurring=recurring_expenses,
        )
        
        # Step 3: Analyze affordability in each scenario
        affordability = self._analyze_affordability(
            purchase_price=purchase_price,
            monthly_payment=monthly_payment,
            months_to_pay=months_to_pay,
            scenarios=scenarios,
            current_balance=current_balance,
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            emergency_fund_months=emergency_fund_months,
            max_debt_to_income=max_debt_to_income,
        )
        
        # Step 4: Calculate financial impacts
        impacts = self._calculate_impacts(
            purchase_price=purchase_price,
            monthly_payment=monthly_payment,
            current_balance=current_balance,
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            metrics=metrics,
        )
        
        # Step 5: Generate recommendation
        recommendation, confidence = self._generate_recommendation(
            affordability=affordability,
            impacts=impacts,
            scenarios=scenarios,
        )
        
        # Step 6: Build comprehensive analysis
        analysis = {
            "decision": {
                "name": decision_name,
                "description": decision_description,
                "type": "financed" if monthly_payment else "lump_sum",
                "price": purchase_price,
                "monthly_payment": monthly_payment,
                "analysis_timestamp": datetime.utcnow().isoformat(),
            },
            "financial_snapshot": {
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "current_balance": current_balance,
                "savings_rate": metrics["savings_rate"].to_dict() if metrics.get("savings_rate") else None,
                "burn_rate": metrics["burn_rate"].to_dict() if metrics.get("burn_rate") else None,
            },
            "affordability": affordability,
            "financial_impacts": [
                {
                    "type": impact.impact_type,
                    "current": impact.current_value,
                    "projected": impact.projected_value,
                    "change_percent": impact.percentage_change,
                    "severity": impact.severity,
                }
                for impact in impacts
            ],
            "scenario_analysis": [
                {
                    "type": scenario.type.value,
                    "probability": scenario.probability,
                    "recommendation": scenario.recommendation,
                    "runway_months": scenario.projected_runway_months,
                    "stress_level": scenario.stress_level,
                }
                for scenario in scenarios
            ],
            "recommendation": {
                "level": recommendation.value,
                "confidence": confidence,
                "reasoning": self._build_reasoning(affordability, impacts),
                "key_concerns": self._identify_concerns(affordability, impacts),
                "action_items": self._generate_action_items(
                    recommendation, affordability, impacts
                ),
            },
            "assumptions": self._collect_assumptions(metrics),
        }
        
        return analysis
    
    def _calculate_metrics(
        self,
        monthly_income: float,
        monthly_expenses: float,
        current_balance: float,
        transactions: List[Dict],
    ) -> Dict[str, QuantitativeMetric]:
        """Calculate all quantitative metrics."""
        metrics = {}
        
        try:
            # Savings rate
            metrics["savings_rate"] = self.quant_engine.calculate_savings_rate(
                monthly_income=monthly_income,
                monthly_expenses=monthly_expenses,
            )
            
            # Burn rate
            if transactions:
                burn_rate, burn_trend = self.quant_engine.calculate_burn_rate(
                    transactions=transactions,
                )
                metrics["burn_rate"] = burn_rate
                metrics["burn_trend"] = burn_trend
            
            # Runway
            if transactions and monthly_expenses > 0:
                burn_metric = metrics.get("burn_rate")
                if burn_metric:
                    metrics["runway"] = self.quant_engine.calculate_runway(
                        current_balance=current_balance,
                        monthly_burn_rate=burn_metric.value,
                    )
        except Exception as e:
            self.logger.error(f"Metric calculation failed: {e}")
        
        return metrics
    
    def _analyze_affordability(
        self,
        purchase_price: float,
        monthly_payment: Optional[float],
        months_to_pay: int,
        scenarios: List,
        current_balance: float,
        monthly_income: float,
        monthly_expenses: float,
        emergency_fund_months: int,
        max_debt_to_income: float,
    ) -> Dict[str, Any]:
        """Analyze affordability across scenarios."""
        emergency_fund = monthly_expenses * emergency_fund_months
        
        affordability = {
            "purchase_price": purchase_price,
            "is_lump_sum": monthly_payment is None,
            "emergency_fund_target": emergency_fund,
            "max_debt_to_income": max_debt_to_income,
            "scenarios": {},
        }
        
        # Check lump sum affordability
        if monthly_payment is None:
            balance_after = current_balance - purchase_price
            can_afford_lump = balance_after >= emergency_fund
            
            affordability["lump_sum_analysis"] = {
                "can_afford": can_afford_lump,
                "balance_after_purchase": balance_after,
                "emergency_fund_impact": balance_after - emergency_fund,
                "depletes_emergency_fund": balance_after < emergency_fund,
            }
        
        # Analyze each scenario
        for scenario in scenarios:
            scenario_affordability = self.scenario_analyzer.affordability_analysis(
                purchase_price=purchase_price,
                monthly_payment=monthly_payment,
                months_to_pay=months_to_pay,
                current_balance=current_balance,
                monthly_income=monthly_income,
                monthly_expenses=monthly_expenses,
                emergency_fund_target=emergency_fund,
            )
            affordability["scenarios"][scenario.type.value] = scenario_affordability["scenarios"].get(
                scenario.type.value
            )
        
        # Overall affordability verdict
        affordable_scenarios = sum(
            1 for s in affordability["scenarios"].values()
            if s and s.get("can_afford", False)
        )
        total_scenarios = len(affordability["scenarios"])
        
        affordability["overall_verdict"] = {
            "scenarios_affordable": affordable_scenarios,
            "total_scenarios": total_scenarios,
            "consensus": affordable_scenarios >= 2,  # At least 2/3 scenarios
        }
        
        return affordability
    
    def _calculate_impacts(
        self,
        purchase_price: float,
        monthly_payment: Optional[float],
        current_balance: float,
        monthly_income: float,
        monthly_expenses: float,
        metrics: Dict[str, QuantitativeMetric],
    ) -> List[FinancialImpact]:
        """Calculate impacts of the decision."""
        impacts = []
        
        # Impact on runway
        if "runway" in metrics and monthly_payment:
            current_runway = metrics["runway"].value
            new_monthly_expenses = monthly_expenses + monthly_payment
            new_runway = current_balance / max(0.1, new_monthly_expenses - monthly_income)
            
            runway_change = ((new_runway - current_runway) / max(0.1, current_runway)) * 100
            
            severity = "critical" if runway_change < -50 else (
                "significant" if runway_change < -20 else (
                    "moderate" if runway_change < -5 else "minimal"
                )
            )
            
            impacts.append(
                FinancialImpact(
                    impact_type="runway_reduction",
                    current_value=current_runway,
                    projected_value=new_runway,
                    percentage_change=runway_change,
                    severity=severity,
                )
            )
        
        # Impact on balance (lump sum)
        if monthly_payment is None:
            balance_change = (purchase_price / current_balance) * 100 if current_balance > 0 else 0
            
            severity = "critical" if balance_change > 50 else (
                "significant" if balance_change > 25 else (
                    "moderate" if balance_change > 10 else "minimal"
                )
            )
            
            impacts.append(
                FinancialImpact(
                    impact_type="balance_reduction",
                    current_value=current_balance,
                    projected_value=current_balance - purchase_price,
                    percentage_change=-balance_change,
                    severity=severity,
                )
            )
        
        # Impact on debt-to-income ratio
        if monthly_payment:
            current_dti = monthly_payment / monthly_income if monthly_income > 0 else 0
            new_dti = (monthly_expenses + monthly_payment) / monthly_income if monthly_income > 0 else 0
            dti_change = (new_dti - current_dti) * 100
            
            severity = "critical" if new_dti > 0.40 else (
                "significant" if new_dti > 0.30 else (
                    "moderate" if new_dti > 0.20 else "minimal"
                )
            )
            
            impacts.append(
                FinancialImpact(
                    impact_type="debt_to_income_ratio",
                    current_value=current_dti,
                    projected_value=new_dti,
                    percentage_change=dti_change,
                    severity=severity,
                )
            )
        
        return impacts
    
    def _generate_recommendation(
        self,
        affordability: Dict,
        impacts: List[FinancialImpact],
        scenarios: List,
    ) -> Tuple[DecisionRecommendation, float]:
        """Generate recommendation based on analysis."""
        
        # Base recommendation scoring
        score = 50  # Neutral starting point
        
        # Affordability (±30 points)
        if affordability.get("overall_verdict", {}).get("consensus"):
            score += 20
        elif affordability.get("overall_verdict", {}).get("scenarios_affordable", 0) > 1:
            score += 10
        elif affordability.get("overall_verdict", {}).get("scenarios_affordable", 0) == 0:
            score -= 30
        
        # Critical impacts (−40 points)
        critical_impacts = [i for i in impacts if i.severity == "critical"]
        if critical_impacts:
            score -= 40
        
        # Significant impacts (−20 points)
        significant_impacts = [i for i in impacts if i.severity == "significant"]
        score -= len(significant_impacts) * 10
        
        # Stress levels in scenarios
        critical_scenarios = [s for s in scenarios if s.stress_level == "critical"]
        if critical_scenarios:
            score -= 25
        
        # Conservative scenario affordability
        conservative = next((s for s in scenarios if s.type == ScenarioType.CONSERVATIVE), None)
        if conservative and "can_afford" in str(conservative):
            score += 15
        
        # Convert score to recommendation
        if score >= 70:
            recommendation = DecisionRecommendation.HIGHLY_RECOMMENDED
            confidence = 0.90
        elif score >= 50:
            recommendation = DecisionRecommendation.RECOMMENDED
            confidence = 0.75
        elif score >= 30:
            recommendation = DecisionRecommendation.NEUTRAL
            confidence = 0.65
        elif score >= 10:
            recommendation = DecisionRecommendation.NOT_RECOMMENDED
            confidence = 0.75
        else:
            recommendation = DecisionRecommendation.STRONGLY_NOT_RECOMMENDED
            confidence = 0.90
        
        return recommendation, confidence
    
    def _build_reasoning(self, affordability: Dict, impacts: List[FinancialImpact]) -> str:
        """Build reasoning explanation."""
        reasons = []
        
        # Affordability reasoning
        verdict = affordability.get("overall_verdict", {})
        if verdict.get("consensus"):
            reasons.append("Affordable in all major scenarios")
        elif verdict.get("scenarios_affordable", 0) >= 1:
            reasons.append(f"Affordable in {verdict['scenarios_affordable']}/3 scenarios")
        else:
            reasons.append("Not affordable based on financial scenarios")
        
        # Impact reasoning
        critical = [i for i in impacts if i.severity == "critical"]
        if critical:
            reasons.append(f"{len(critical)} critical financial impacts identified")
        
        significant = [i for i in impacts if i.severity == "significant"]
        if significant:
            reasons.append(f"{len(significant)} significant impacts")
        
        return " | ".join(reasons)
    
    def _identify_concerns(self, affordability: Dict, impacts: List[FinancialImpact]) -> List[str]:
        """Identify key concerns."""
        concerns = []
        
        # Affordability concerns
        if not affordability.get("overall_verdict", {}).get("consensus"):
            concerns.append("Not affordable in all scenarios")
        
        # Depletes emergency fund
        lump_sum = affordability.get("lump_sum_analysis", {})
        if lump_sum.get("depletes_emergency_fund"):
            concerns.append("Would deplete emergency fund")
        
        # Critical impacts
        for impact in impacts:
            if impact.severity == "critical":
                concerns.append(f"Critical impact on {impact.impact_type}")
        
        return concerns
    
    def _generate_action_items(
        self,
        recommendation: DecisionRecommendation,
        affordability: Dict,
        impacts: List[FinancialImpact],
    ) -> List[str]:
        """Generate action items based on recommendation."""
        actions = []
        
        if recommendation == DecisionRecommendation.STRONGLY_NOT_RECOMMENDED:
            actions.append("Do not proceed with this purchase at this time")
            actions.append("Focus on building emergency fund")
            actions.append("Re-evaluate in 3-6 months after improving financial position")
        elif recommendation == DecisionRecommendation.NOT_RECOMMENDED:
            actions.append("Consider postponing this purchase")
            actions.append("Explore financing options to reduce immediate impact")
            actions.append("Work on reducing monthly expenses first")
        elif recommendation == DecisionRecommendation.NEUTRAL:
            actions.append("Proceed with caution")
            actions.append("Ensure emergency fund remains intact")
            actions.append("Monitor budget closely after purchase")
        elif recommendation == DecisionRecommendation.RECOMMENDED:
            actions.append("Can proceed with this purchase")
            actions.append("Consider financing to preserve cash flow")
            actions.append("Monitor spending for next 60 days")
        else:  # HIGHLY_RECOMMENDED
            actions.append("Excellent decision - proceed confidently")
            actions.append("No additional financial adjustments needed")
        
        return actions
    
    def _collect_assumptions(self, metrics: Dict[str, QuantitativeMetric]) -> List[str]:
        """Collect all assumptions from metrics."""
        assumptions = set()
        
        for metric in metrics.values():
            if hasattr(metric, 'assumptions'):
                assumptions.update(metric.assumptions)
        
        return list(assumptions)
