"""
Decision Framework - Structure financial decisions with multi-factor analysis.

Provides:
- Decision evaluation framework
- Multi-criteria decision making
- Trade-off analysis
- Recommendation engine
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

import numpy as np

logger = logging.getLogger(__name__)


class DecisionType(str, Enum):
    """Types of financial decisions."""
    PURCHASE = "purchase"
    CAREER = "career"
    INVESTMENT = "investment"
    HOUSING = "housing"
    DEBT = "debt"
    INSURANCE = "insurance"
    EDUCATION = "education"


@dataclass
class FinancialChoice:
    """A financial choice/option to evaluate."""
    name: str
    description: str
    upfront_cost: float
    annual_cost: float
    annual_benefit: float
    duration_years: int
    risk_level: str  # "low", "medium", "high"
    flexibility: str  # "high", "medium", "low"
    alignment_score: float  # 0-1 with goals


@dataclass
class Decision:
    """Financial decision with analysis."""
    decision_type: DecisionType
    decision_question: str
    options: List[FinancialChoice]
    recommended_option: str
    recommendation_confidence: float
    financial_analysis: Dict
    non_financial_factors: Dict
    risk_assessment: Dict
    trade_offs: List[str]
    assumptions: List[str]


class DecisionFramework:
    """
    Framework for evaluating financial decisions with multiple factors.
    """
    
    def __init__(self):
        """Initialize decision framework."""
        self.logger = logger
    
    def evaluate_decision(
        self,
        decision_type: DecisionType,
        question: str,
        options: List[FinancialChoice],
        personal_factors: Dict = None,
        financial_goals: List[str] = None,
    ) -> Decision:
        """
        Evaluate financial decision with multi-factor analysis.
        
        Args:
            decision_type: Type of decision
            question: The decision question
            options: List of FinancialChoice options
            personal_factors: Personal circumstances (income, goals, etc.)
            financial_goals: Financial goals to consider
            
        Returns:
            Decision with recommendation
        """
        if not options or len(options) < 2:
            logger.warning("Need at least 2 options to evaluate")
            return None
        
        # Calculate financial metrics for each option
        financial_metrics = {}
        for option in options:
            metrics = self._calculate_financial_metrics(option)
            financial_metrics[option.name] = metrics
        
        # Calculate non-financial scores
        non_financial_scores = {}
        for option in options:
            score = self._score_non_financial(option, decision_type)
            non_financial_scores[option.name] = score
        
        # Determine recommended option
        recommended = self._select_best_option(
            options, financial_metrics, non_financial_scores, personal_factors
        )
        
        # Generate trade-offs
        trade_offs = self._identify_trade_offs(
            options, financial_metrics, recommended
        )
        
        # Risk assessment
        risk_assessment = self._assess_decision_risk(options, recommended)
        
        # Build assumptions list
        assumptions = [
            "Uses deterministic financial modeling",
            "Assumes stable economic conditions",
            "Based on historical averages",
            "Does not account for unknown future events",
        ]
        
        return Decision(
            decision_type=decision_type,
            decision_question=question,
            options=options,
            recommended_option=recommended,
            recommendation_confidence=0.75,
            financial_analysis=financial_metrics,
            non_financial_factors=non_financial_scores,
            risk_assessment=risk_assessment,
            trade_offs=trade_offs,
            assumptions=assumptions,
        )
    
    def compare_options(
        self,
        options: List[FinancialChoice],
        years_to_evaluate: int = 10,
    ) -> Dict:
        """
        Compare financial impact of different options.
        
        Args:
            options: Options to compare
            years_to_evaluate: Years to project forward
            
        Returns:
            Comparison matrix
        """
        comparison = {}
        
        for option in options:
            # Calculate total cost of ownership
            tco = (
                option.upfront_cost +
                (option.annual_cost * years_to_evaluate)
            )
            
            # Calculate total benefit
            total_benefit = option.annual_benefit * years_to_evaluate
            
            # Net benefit
            net_benefit = total_benefit - tco
            
            # Payback period
            annual_net = option.annual_benefit - option.annual_cost
            payback = option.upfront_cost / annual_net if annual_net > 0 else float('inf')
            
            # ROI
            roi = (net_benefit / max(tco, 1)) * 100 if tco > 0 else 0
            
            comparison[option.name] = {
                "total_cost": tco,
                "total_benefit": total_benefit,
                "net_benefit": net_benefit,
                "payback_period_years": payback,
                "roi_percent": roi,
                "annual_net_flow": annual_net,
            }
        
        return comparison
    
    def sensitivity_analysis(
        self,
        option: FinancialChoice,
        variables_to_test: Dict[str, tuple],  # {var_name: (low, high, steps)}
    ) -> Dict:
        """
        Run sensitivity analysis on key variables.
        
        Args:
            option: FinancialChoice to test
            variables_to_test: Variables to vary
            
        Returns:
            Sensitivity analysis results
        """
        results = {}
        
        # Test upfront cost sensitivity
        if "upfront_cost" in variables_to_test:
            low, high, steps = variables_to_test["upfront_cost"]
            upfront_scenarios = np.linspace(low, high, steps)
            upfront_results = []
            
            for cost in upfront_scenarios:
                net = (option.annual_benefit - option.annual_cost) * option.duration_years - cost
                upfront_results.append({
                    "upfront_cost": cost,
                    "net_benefit": net,
                })
            results["upfront_cost"] = upfront_results
        
        # Test annual benefit sensitivity
        if "annual_benefit" in variables_to_test:
            low, high, steps = variables_to_test["annual_benefit"]
            benefit_scenarios = np.linspace(low, high, steps)
            benefit_results = []
            
            for benefit in benefit_scenarios:
                total_benefit = benefit * option.duration_years
                net = total_benefit - option.upfront_cost - (option.annual_cost * option.duration_years)
                benefit_results.append({
                    "annual_benefit": benefit,
                    "net_benefit": net,
                })
            results["annual_benefit"] = benefit_results
        
        return results
    
    def breakeven_analysis(
        self,
        option1: FinancialChoice,
        option2: FinancialChoice,
    ) -> Dict:
        """
        Find breakeven point between two options.
        
        Args:
            option1: First option
            option2: Second option
            
        Returns:
            Breakeven analysis
        """
        # Annual net cost difference
        opt1_annual_net = option1.annual_benefit - option1.annual_cost
        opt2_annual_net = option2.annual_benefit - option2.annual_cost
        annual_difference = opt1_annual_net - opt2_annual_net
        
        # Upfront cost difference
        upfront_difference = option1.upfront_cost - option2.upfront_cost
        
        # Breakeven in years
        if annual_difference != 0:
            breakeven_years = upfront_difference / annual_difference
        else:
            breakeven_years = float('inf')
        
        return {
            "breakeven_years": max(0, breakeven_years),
            "option1_better_after_years": breakeven_years,
            "upfront_cost_difference": upfront_difference,
            "annual_net_difference": annual_difference,
            "preferred_option_initially": (
                option2.name if upfront_difference > 0 else option1.name
            ),
            "preferred_option_long_term": (
                option1.name if annual_difference > 0 else option2.name
            ),
        }
    
    def _calculate_financial_metrics(
        self,
        option: FinancialChoice,
    ) -> Dict:
        """Calculate financial metrics for option."""
        total_cost = option.upfront_cost + (option.annual_cost * option.duration_years)
        total_benefit = option.annual_benefit * option.duration_years
        net_benefit = total_benefit - total_cost
        
        # Annual net flow
        annual_net = option.annual_benefit - option.annual_cost
        
        # Payback period
        payback = (
            option.upfront_cost / annual_net
            if annual_net > 0 else float('inf')
        )
        
        # ROI
        roi = (net_benefit / max(total_cost, 1)) * 100 if total_cost > 0 else 0
        
        return {
            "total_cost": total_cost,
            "total_benefit": total_benefit,
            "net_benefit": net_benefit,
            "payback_period": payback,
            "roi_percent": roi,
            "cost_per_year": total_cost / option.duration_years,
        }
    
    def _score_non_financial(
        self,
        option: FinancialChoice,
        decision_type: DecisionType,
    ) -> Dict:
        """Score non-financial factors."""
        scores = {}
        
        # Risk score (lower is better)
        risk_map = {"low": 3, "medium": 2, "high": 1}
        scores["risk_score"] = risk_map.get(option.risk_level, 2)
        
        # Flexibility score (higher is better)
        flex_map = {"high": 3, "medium": 2, "low": 1}
        scores["flexibility_score"] = flex_map.get(option.flexibility, 2)
        
        # Goal alignment
        scores["goal_alignment"] = option.alignment_score
        
        # Decision-type specific factors
        if decision_type == DecisionType.CAREER:
            scores["growth_potential"] = 2.5  # Placeholder
        elif decision_type == DecisionType.HOUSING:
            scores["stability"] = 2.5
        
        return scores
    
    def _select_best_option(
        self,
        options: List[FinancialChoice],
        financial_metrics: Dict,
        non_financial_scores: Dict,
        personal_factors: Dict = None,
    ) -> str:
        """Select best option using weighted scoring."""
        best_score = -float('inf')
        best_option = None
        
        for option in options:
            # Financial score (higher net benefit is better)
            financial_score = financial_metrics[option.name]["net_benefit"] / 10000  # Normalize
            
            # Non-financial score
            non_financial = non_financial_scores[option.name]
            non_financial_score = (
                non_financial.get("risk_score", 2) * 0.3 +
                non_financial.get("flexibility_score", 2) * 0.3 +
                non_financial.get("goal_alignment", 0.5) * 0.4
            )
            
            # Combined score (weighted)
            combined_score = financial_score * 0.6 + non_financial_score * 0.4
            
            if combined_score > best_score:
                best_score = combined_score
                best_option = option.name
        
        return best_option
    
    def _identify_trade_offs(
        self,
        options: List[FinancialChoice],
        financial_metrics: Dict,
        recommended: str,
    ) -> List[str]:
        """Identify trade-offs vs recommended option."""
        trade_offs = []
        recommended_metrics = financial_metrics[recommended]
        
        for option in options:
            if option.name == recommended:
                continue
            
            metrics = financial_metrics[option.name]
            
            if metrics["net_benefit"] > recommended_metrics["net_benefit"]:
                trade_offs.append(
                    f"Choosing {recommended} over {option.name} "
                    f"costs ${metrics['net_benefit'] - recommended_metrics['net_benefit']:.0f} in net benefit"
                )
        
        return trade_offs
    
    def _assess_decision_risk(
        self,
        options: List[FinancialChoice],
        recommended: str,
    ) -> Dict:
        """Assess risk of recommended decision."""
        recommended_option = next(
            (o for o in options if o.name == recommended),
            None
        )
        
        if not recommended_option:
            return {}
        
        return {
            "risk_level": recommended_option.risk_level,
            "reversibility": "low" if "housing" in recommended_option.name.lower() else "high",
            "recovery_time": "long" if recommended_option.duration_years > 5 else "short",
            "mitigation_available": "high",
        }
