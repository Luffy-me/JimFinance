"""
Total Cost of Ownership (TCO) Calculator - Comprehensive cost analysis.

Provides:
- TCO calculation with all cost components
- Lifecycle costing
- Cost comparison across options
- Hidden cost identification
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import numpy as np

logger = logging.getLogger(__name__)


class CostType(str, Enum):
    """Types of costs in TCO."""
    ACQUISITION = "acquisition"
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    FINANCING = "financing"
    INSURANCE = "insurance"
    TAX = "tax"
    DISPOSAL = "disposal"
    OPPORTUNITY = "opportunity"
    HIDDEN = "hidden"


@dataclass
class CostComponent:
    """Individual cost component."""
    cost_type: CostType
    description: str
    amount: float
    frequency: str  # "one-time", "monthly", "annual"
    duration_years: int  # Years this cost applies
    growth_rate: float  # Annual growth %
    confidence: float  # 0-1 confidence in estimate
    assumptions: List[str]


@dataclass
class TCOAnalysis:
    """Total Cost of Ownership analysis."""
    item_name: str
    analysis_period_years: int
    total_cost_nominal: float
    total_cost_present_value: float
    cost_breakdown: Dict[str, float]  # By type
    annual_average_cost: float
    cost_per_unit: float  # Cost per year of use, etc.
    sensitivity_range: Dict[str, tuple]  # Variable -> (low, high)
    comparison_to_alternative: Optional[Dict]
    payback_period: Optional[float]
    assumptions: List[str]
    confidence: float


class TCOCalculator:
    """
    Calculates total cost of ownership with detailed breakdown.
    """
    
    def __init__(self, discount_rate: float = 0.05):
        """
        Initialize TCO calculator.
        
        Args:
            discount_rate: Discount rate for NPV calculation (default 5%)
        """
        self.logger = logger
        self.discount_rate = discount_rate
    
    def calculate_tco(
        self,
        item_name: str,
        cost_components: List[CostComponent],
        analysis_period: int = 10,
    ) -> TCOAnalysis:
        """
        Calculate total cost of ownership.
        
        Args:
            item_name: Name of item/purchase
            cost_components: List of cost components
            analysis_period: Years to analyze
            
        Returns:
            TCOAnalysis with comprehensive cost breakdown
        """
        # Calculate total nominal cost
        total_nominal = self._calculate_total_nominal(cost_components, analysis_period)
        
        # Calculate present value
        total_pv = self._calculate_present_value(cost_components, analysis_period)
        
        # Breakdown by cost type
        breakdown = self._cost_breakdown_by_type(cost_components, analysis_period)
        
        # Annual average
        annual_average = total_pv / analysis_period if analysis_period > 0 else 0
        
        # Sensitivity analysis
        sensitivity = self._sensitivity_analysis(cost_components)
        
        # Assumptions
        assumptions = [
            f"Discount rate: {self.discount_rate*100:.1f}%",
            f"Analysis period: {analysis_period} years",
            "Assumes consistent inflation rates",
            "Does not account for technological obsolescence",
            "Based on provided component estimates",
        ]
        
        return TCOAnalysis(
            item_name=item_name,
            analysis_period_years=analysis_period,
            total_cost_nominal=total_nominal,
            total_cost_present_value=total_pv,
            cost_breakdown=breakdown,
            annual_average_cost=annual_average,
            cost_per_unit=annual_average,
            sensitivity_range=sensitivity,
            comparison_to_alternative=None,
            payback_period=None,
            assumptions=assumptions,
            confidence=0.80,
        )
    
    def compare_tco(
        self,
        item1_name: str,
        item1_components: List[CostComponent],
        item2_name: str,
        item2_components: List[CostComponent],
        analysis_period: int = 10,
    ) -> Dict:
        """
        Compare TCO between two items.
        
        Args:
            item1_name: First item name
            item1_components: First item costs
            item2_name: Second item name
            item2_components: Second item costs
            analysis_period: Years to analyze
            
        Returns:
            Comparison results
        """
        tco1 = self.calculate_tco(item1_name, item1_components, analysis_period)
        tco2 = self.calculate_tco(item2_name, item2_components, analysis_period)
        
        cost_difference = tco2.total_cost_present_value - tco1.total_cost_present_value
        cost_difference_percent = (cost_difference / tco1.total_cost_present_value * 100) if tco1.total_cost_present_value > 0 else 0
        
        # Break-even analysis
        breakeven_years = self._calculate_breakeven_years(
            item1_components, item2_components, analysis_period
        )
        
        return {
            "item1": {
                "name": item1_name,
                "tco_nominal": tco1.total_cost_nominal,
                "tco_pv": tco1.total_cost_present_value,
                "annual_average": tco1.annual_average_cost,
            },
            "item2": {
                "name": item2_name,
                "tco_nominal": tco2.total_cost_nominal,
                "tco_pv": tco2.total_cost_present_value,
                "annual_average": tco2.annual_average_cost,
            },
            "comparison": {
                "cost_difference_pv": cost_difference,
                "cost_difference_percent": cost_difference_percent,
                "cheaper_option": item1_name if cost_difference < 0 else item2_name,
                "savings_amount": abs(cost_difference),
                "breakeven_years": breakeven_years,
            },
        }
    
    def lifecycle_cost_analysis(
        self,
        purchase_price: float,
        life_expectancy_years: int,
        annual_maintenance: float,
        maintenance_growth_rate: float = 0.03,
        residual_value: float = 0,
        annual_insurance: float = 0,
        annual_tax: float = 0,
        financing_cost: float = 0,
    ) -> Dict:
        """
        Analyze lifecycle costs.
        
        Args:
            purchase_price: Initial purchase price
            life_expectancy_years: Expected useful life
            annual_maintenance: Annual maintenance cost
            maintenance_growth_rate: Maintenance cost growth %
            residual_value: Residual value at end of life
            annual_insurance: Annual insurance cost
            annual_tax: Annual tax/registration cost
            financing_cost: Total financing cost (interest)
            
        Returns:
            Lifecycle cost analysis
        """
        # Build component list
        components = [
            CostComponent(
                cost_type=CostType.ACQUISITION,
                description="Purchase price",
                amount=purchase_price,
                frequency="one-time",
                duration_years=1,
                growth_rate=0.0,
                confidence=0.95,
                assumptions=["At time of purchase"],
            ),
            CostComponent(
                cost_type=CostType.MAINTENANCE,
                description="Annual maintenance",
                amount=annual_maintenance,
                frequency="annual",
                duration_years=life_expectancy_years,
                growth_rate=maintenance_growth_rate,
                confidence=0.70,
                assumptions=["Based on historical rates"],
            ),
            CostComponent(
                cost_type=CostType.INSURANCE,
                description="Annual insurance",
                amount=annual_insurance,
                frequency="annual",
                duration_years=life_expectancy_years,
                growth_rate=0.02,
                confidence=0.80,
                assumptions=["Estimated insurance premium"],
            ),
            CostComponent(
                cost_type=CostType.TAX,
                description="Annual tax/registration",
                amount=annual_tax,
                frequency="annual",
                duration_years=life_expectancy_years,
                growth_rate=0.02,
                confidence=0.85,
                assumptions=["Based on current rates"],
            ),
            CostComponent(
                cost_type=CostType.FINANCING,
                description="Financing costs",
                amount=financing_cost,
                frequency="one-time",
                duration_years=1,
                growth_rate=0.0,
                confidence=0.90,
                assumptions=["Loan interest"],
            ),
        ]
        
        # Calculate TCO
        tco = self.calculate_tco("Item", components, life_expectancy_years)
        
        # Adjust for residual value
        net_cost = tco.total_cost_present_value - residual_value / ((1 + self.discount_rate) ** life_expectancy_years)
        
        # Cost per mile/unit/year
        cost_per_unit = net_cost / life_expectancy_years
        
        return {
            "gross_lifecycle_cost": tco.total_cost_present_value,
            "residual_value_pv": residual_value / ((1 + self.discount_rate) ** life_expectancy_years),
            "net_lifecycle_cost": net_cost,
            "cost_per_year": cost_per_unit,
            "cost_breakdown": tco.cost_breakdown,
            "recommendation": "High-cost item, evaluate alternatives" if net_cost > 50000 else "Moderate cost",
        }
    
    def identify_hidden_costs(
        self,
        item_type: str,
        cost_components: List[CostComponent],
    ) -> List[str]:
        """
        Identify potential hidden costs.
        
        Args:
            item_type: Type of item (car, house, equipment)
            cost_components: Existing cost components
            
        Returns:
            List of potential hidden costs
        """
        hidden_costs = []
        
        # Check what's included
        component_types = {c.cost_type for c in cost_components}
        
        if item_type == "car":
            if CostType.MAINTENANCE not in component_types:
                hidden_costs.append("Maintenance (repairs, servicing)")
            if CostType.INSURANCE not in component_types:
                hidden_costs.append("Insurance premiums")
            if CostType.TAX not in component_types:
                hidden_costs.append("Registration and taxes")
            hidden_costs.append("Fuel/charging costs")
            hidden_costs.append("Depreciation")
            hidden_costs.append("Parking fees")
            hidden_costs.append("Roadside assistance")
        
        elif item_type == "house":
            if CostType.MAINTENANCE not in component_types:
                hidden_costs.append("Maintenance and repairs")
            hidden_costs.append("Property taxes")
            hidden_costs.append("HOA fees")
            hidden_costs.append("Home insurance")
            hidden_costs.append("Utilities")
            hidden_costs.append("Landscaping maintenance")
            hidden_costs.append("Appliance replacement")
        
        elif item_type == "business":
            hidden_costs.append("Ongoing training and development")
            hidden_costs.append("Compliance and licensing")
            hidden_costs.append("Technology upgrades")
            hidden_costs.append("Staff training")
        
        return hidden_costs
    
    def _calculate_total_nominal(
        self,
        components: List[CostComponent],
        analysis_period: int,
    ) -> float:
        """Calculate total nominal cost without discounting."""
        total = 0
        
        for component in components:
            if component.frequency == "one-time":
                total += component.amount
            elif component.frequency == "monthly":
                # Monthly costs over analysis period
                total += component.amount * 12 * min(component.duration_years, analysis_period)
            elif component.frequency == "annual":
                # Annual costs with growth
                for year in range(min(component.duration_years, analysis_period)):
                    cost = component.amount * ((1 + component.growth_rate) ** year)
                    total += cost
        
        return total
    
    def _calculate_present_value(
        self,
        components: List[CostComponent],
        analysis_period: int,
    ) -> float:
        """Calculate present value of all costs."""
        total_pv = 0
        
        for component in components:
            if component.frequency == "one-time":
                total_pv += component.amount
            elif component.frequency == "monthly":
                # Monthly costs discounted
                monthly_rate = self.discount_rate / 12
                for month in range(min(component.duration_years, analysis_period) * 12):
                    pv = component.amount / ((1 + monthly_rate) ** month)
                    total_pv += pv
            elif component.frequency == "annual":
                # Annual costs discounted with growth
                for year in range(min(component.duration_years, analysis_period)):
                    cost = component.amount * ((1 + component.growth_rate) ** year)
                    pv = cost / ((1 + self.discount_rate) ** year)
                    total_pv += pv
        
        return total_pv
    
    def _cost_breakdown_by_type(
        self,
        components: List[CostComponent],
        analysis_period: int,
    ) -> Dict[str, float]:
        """Break down costs by type."""
        breakdown = {}
        
        for component in components:
            cost_type = component.cost_type.value
            
            if cost_type not in breakdown:
                breakdown[cost_type] = 0
            
            # Calculate present value for this component
            if component.frequency == "one-time":
                breakdown[cost_type] += component.amount
            elif component.frequency == "annual":
                for year in range(min(component.duration_years, analysis_period)):
                    cost = component.amount * ((1 + component.growth_rate) ** year)
                    pv = cost / ((1 + self.discount_rate) ** year)
                    breakdown[cost_type] += pv
            elif component.frequency == "monthly":
                monthly_rate = self.discount_rate / 12
                for month in range(min(component.duration_years, analysis_period) * 12):
                    pv = component.amount / ((1 + monthly_rate) ** month)
                    breakdown[cost_type] += pv
        
        return breakdown
    
    def _sensitivity_analysis(
        self,
        components: List[CostComponent],
    ) -> Dict[str, tuple]:
        """Run sensitivity analysis on major cost components."""
        sensitivity = {}
        
        for component in components:
            if component.amount > 10000:  # Only major components
                low = component.amount * 0.8
                high = component.amount * 1.2
                sensitivity[component.description] = (low, high)
        
        return sensitivity
    
    def _calculate_breakeven_years(
        self,
        components1: List[CostComponent],
        components2: List[CostComponent],
        analysis_period: int,
    ) -> Optional[float]:
        """Calculate breakeven years between two options."""
        # Calculate cumulative costs year by year
        for year in range(1, analysis_period + 1):
            cost1 = self._calculate_total_nominal(components1, year)
            cost2 = self._calculate_total_nominal(components2, year)
            
            if (cost1 - cost2) * ((self._calculate_total_nominal(components1, year + 1) - self._calculate_total_nominal(components2, year + 1)) if year < analysis_period else 1) < 0:
                # Crossover point
                return float(year)
        
        return None
