"""
Education Cost Projector - Project future education expenses.

Provides:
- College cost projections (tuition, room & board, books, etc.)
- K-12 private school cost projections
- Graduate program cost analysis
- Cost-per-year inflation modeling
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import numpy as np

logger = logging.getLogger(__name__)


class EducationLevel(str, Enum):
    """Education level types."""
    PRIVATE_K12 = "private_k12"
    PUBLIC_COLLEGE = "public_college"
    PRIVATE_COLLEGE = "private_college"
    GRADUATE_DEGREE = "graduate_degree"
    PROFESSIONAL_DEGREE = "professional_degree"


@dataclass
class EducationCost:
    """Single education cost component."""
    category: str  # "tuition", "room_board", "books", "misc"
    annual_cost: float
    per_unit_cost: float  # Per year or per semester
    frequency: str  # "annual", "semester", "monthly"


@dataclass
class CostProjection:
    """Education cost projection."""
    education_level: EducationLevel
    current_total_cost: float
    projected_total_cost: float  # Total across all years
    cost_breakdown: Dict[str, float]  # By component
    annual_costs: List[float]  # Year by year
    years_of_education: int
    inflation_rate_assumed: float
    inflation_adjusted_total: float
    confidence: float
    calculation_method: str
    assumptions: List[str]


class CostProjector:
    """
    Projects education costs with inflation adjustment.
    """
    
    # Average annual costs (2023-2024 academic year)
    AVERAGE_COSTS = {
        EducationLevel.PRIVATE_K12: {
            "average_annual": 15000,
            "years": 13,
            "breakdown": {
                "tuition": 12000,
                "books": 1000,
                "supplies": 1000,
                "transportation": 1000,
            }
        },
        EducationLevel.PUBLIC_COLLEGE: {
            "average_annual": 28000,  # In-state
            "years": 4,
            "breakdown": {
                "tuition": 9700,
                "room_board": 12000,
                "books": 1200,
                "supplies": 1200,
                "transportation": 2400,
                "personal": 1500,
            }
        },
        EducationLevel.PRIVATE_COLLEGE: {
            "average_annual": 60000,
            "years": 4,
            "breakdown": {
                "tuition": 40000,
                "room_board": 14000,
                "books": 1200,
                "supplies": 1200,
                "transportation": 1200,
                "personal": 2400,
            }
        },
        EducationLevel.GRADUATE_DEGREE: {
            "average_annual": 35000,
            "years": 2,
            "breakdown": {
                "tuition": 25000,
                "books": 2000,
                "supplies": 2000,
                "transportation": 3000,
                "living": 3000,
            }
        },
        EducationLevel.PROFESSIONAL_DEGREE: {
            "average_annual": 50000,
            "years": 3,
            "breakdown": {
                "tuition": 35000,
                "books": 2500,
                "exam_fees": 2500,
                "living": 10000,
            }
        },
    }
    
    # Education cost inflation (historically ~5.8% annually)
    EDUCATION_INFLATION_RATE = 0.058
    
    def __init__(self):
        """Initialize cost projector."""
        self.logger = logger
    
    def project_education_costs(
        self,
        education_level: EducationLevel,
        years_until_start: int,
        inflation_rate: Optional[float] = None,
    ) -> CostProjection:
        """
        Project education costs into future.
        
        Args:
            education_level: Level of education
            years_until_start: Years until education starts
            inflation_rate: Custom inflation rate (uses historical if None)
            
        Returns:
            CostProjection with cost analysis
        """
        if inflation_rate is None:
            inflation_rate = self.EDUCATION_INFLATION_RATE
        
        if education_level not in self.AVERAGE_COSTS:
            logger.warning(f"Unknown education level: {education_level}")
            return None
        
        cost_data = self.AVERAGE_COSTS[education_level]
        current_annual = cost_data["average_annual"]
        years = cost_data["years"]
        breakdown = cost_data["breakdown"]
        
        # Project annual costs
        annual_costs = []
        total_projected = 0
        
        for year_index in range(years):
            # Years from now to start of that year
            years_from_now = years_until_start + year_index
            
            # Apply inflation
            year_cost = current_annual * ((1 + inflation_rate) ** years_from_now)
            annual_costs.append(year_cost)
            total_projected += year_cost
        
        # Project cost breakdown
        projected_breakdown = {}
        for category, percent_or_amount in breakdown.items():
            if isinstance(percent_or_amount, dict):
                projected_breakdown[category] = percent_or_amount
            else:
                # Assuming it's a fixed amount, inflate it
                component_cost = percent_or_amount * ((1 + inflation_rate) ** years_until_start)
                projected_breakdown[category] = component_cost
        
        # Calculate inflation-adjusted (real) total
        # Real cost = projected nominal cost / (1 + inflation)^years_until_start
        inflation_adjusted = total_projected / ((1 + inflation_rate) ** years_until_start)
        
        assumptions = [
            f"Education level: {education_level.value}",
            f"Years until start: {years_until_start}",
            f"Duration: {years} years",
            f"Annual inflation rate: {inflation_rate*100:.1f}%",
            "Uses average costs for education type",
            "Does not account for scholarships or aid",
            "Does not include lost income opportunity cost",
        ]
        
        return CostProjection(
            education_level=education_level,
            current_total_cost=current_annual * years,
            projected_total_cost=total_projected,
            cost_breakdown=projected_breakdown,
            annual_costs=annual_costs,
            years_of_education=years,
            inflation_rate_assumed=inflation_rate,
            inflation_adjusted_total=inflation_adjusted,
            confidence=0.75,
            calculation_method="Historical average with inflation adjustment",
            assumptions=assumptions,
        )
    
    def compare_education_options(
        self,
        options: List[EducationLevel],
        years_until_start: int,
    ) -> Dict[str, dict]:
        """
        Compare costs across education options.
        
        Args:
            options: List of education options to compare
            years_until_start: Years until education starts
            
        Returns:
            Dict with comparison data
        """
        comparisons = {}
        
        for option in options:
            projection = self.project_education_costs(option, years_until_start)
            if projection:
                comparisons[option.value] = {
                    "total_cost": projection.projected_total_cost,
                    "annual_average": projection.projected_total_cost / projection.years_of_education,
                    "years": projection.years_of_education,
                    "breakdown": projection.cost_breakdown,
                }
        
        return comparisons
    
    def calculate_monthly_savings_needed(
        self,
        projected_cost: float,
        months_until_start: int,
        starting_balance: float = 0,
        expected_return: float = 0.05,
    ) -> Dict[str, float]:
        """
        Calculate monthly savings needed to fund education.
        
        Args:
            projected_cost: Total projected education cost
            months_until_start: Months to save
            starting_balance: Starting savings balance
            expected_return: Expected annual return on savings
            
        Returns:
            Dict with savings analysis
        """
        if months_until_start <= 0:
            return {"error": "Must have positive months to save"}
        
        monthly_return = (1 + expected_return) ** (1/12) - 1
        
        # Future value of starting balance
        fv_starting = starting_balance * ((1 + monthly_return) ** months_until_start)
        
        # Need to accumulate
        need_to_accumulate = max(0, projected_cost - fv_starting)
        
        # Monthly savings (future value of annuity)
        # FV = PMT * [((1 + r)^n - 1) / r]
        annuity_factor = (((1 + monthly_return) ** months_until_start - 1) / monthly_return) if monthly_return > 0 else months_until_start
        
        monthly_savings = need_to_accumulate / annuity_factor if annuity_factor > 0 else 0
        
        return {
            "monthly_savings_needed": monthly_savings,
            "total_to_accumulate": need_to_accumulate,
            "projected_balance_at_start": fv_starting,
            "months_to_save": months_until_start,
            "expected_investment_return": expected_return,
        }
    
    def analyze_scholarship_impact(
        self,
        projected_cost: float,
        scholarship_amount: float,
    ) -> Dict[str, float]:
        """
        Analyze impact of scholarship on costs.
        
        Args:
            projected_cost: Total projected cost
            scholarship_amount: Annual scholarship
            
        Returns:
            Cost reduction analysis
        """
        years_in_school = 4  # Default assumption
        total_scholarship = scholarship_amount * years_in_school
        net_cost = max(0, projected_cost - total_scholarship)
        
        return {
            "original_cost": projected_cost,
            "scholarship_amount": scholarship_amount,
            "total_scholarship_over_years": total_scholarship,
            "net_cost_after_scholarship": net_cost,
            "cost_reduction_percent": (total_scholarship / projected_cost * 100) if projected_cost > 0 else 0,
        }
