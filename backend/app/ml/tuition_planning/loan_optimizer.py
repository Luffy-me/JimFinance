"""
Student Loan Optimizer - Optimize student loan strategy and repayment.

Provides:
- Loan comparison analysis
- Repayment plan optimization
- Refinancing recommendations
- Forgiveness program scenarios
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import numpy as np

logger = logging.getLogger(__name__)


class LoanType(str, Enum):
    """Student loan types."""
    FEDERAL_SUBSIDIZED = "federal_subsidized"
    FEDERAL_UNSUBSIDIZED = "federal_unsubsidized"
    FEDERAL_PLUS = "federal_plus"
    PRIVATE_LOAN = "private_loan"


class RepaymentPlan(str, Enum):
    """Federal loan repayment plans."""
    STANDARD = "standard"
    GRADUATED = "graduated"
    INCOME_DRIVEN = "income_driven"
    PAY_AS_YOU_EARN = "pay_as_you_earn"


@dataclass
class StudentLoanScenario:
    """Student loan repayment scenario."""
    loan_type: LoanType
    principal: float
    interest_rate: float
    repayment_plan: RepaymentPlan
    monthly_payment: float
    total_interest_paid: float
    years_to_repay: float
    total_cost: float
    forgiveness_eligible: bool
    forgiveness_timeline_years: Optional[int]
    confidence: float


@dataclass
class LoanOptimization:
    """Loan optimization recommendations."""
    recommended_repayment_plan: RepaymentPlan
    monthly_payment: float
    total_interest_cost: float
    payoff_timeline: float  # Years
    savings_vs_standard: float  # Amount saved
    key_recommendations: List[str]
    considerations: List[str]
    confidence: float
    assumptions: List[str]


class LoanOptimizer:
    """
    Optimizes student loan strategy.
    """
    
    # Federal loan rates (2024 academic year)
    FEDERAL_RATES = {
        LoanType.FEDERAL_SUBSIDIZED: 0.058,
        LoanType.FEDERAL_UNSUBSIDIZED: 0.058,
        LoanType.FEDERAL_PLUS: 0.075,
    }
    
    def __init__(self):
        """Initialize loan optimizer."""
        self.logger = logger
    
    def calculate_repayment_scenarios(
        self,
        principal: float,
        interest_rate: float,
        loan_type: LoanType,
        annual_income: Optional[float] = None,
        family_size: int = 1,
    ) -> Dict[str, StudentLoanScenario]:
        """
        Calculate repayment scenarios for different plans.
        
        Args:
            principal: Loan principal amount
            interest_rate: Annual interest rate
            loan_type: Type of student loan
            annual_income: Annual income (for income-driven plans)
            family_size: Family size (for income-driven plans)
            
        Returns:
            Dict of scenarios by repayment plan
        """
        scenarios = {}
        
        # Standard plan (10 years)
        scenarios["standard"] = self._calculate_standard_plan(
            principal, interest_rate, loan_type
        )
        
        # Graduated plan
        scenarios["graduated"] = self._calculate_graduated_plan(
            principal, interest_rate, loan_type
        )
        
        # Income-driven plans (if income provided)
        if annual_income is not None:
            scenarios["income_driven"] = self._calculate_income_driven_plan(
                principal, interest_rate, loan_type, annual_income, family_size
            )
            scenarios["pay_as_you_earn"] = self._calculate_paye_plan(
                principal, interest_rate, loan_type, annual_income, family_size
            )
        
        return scenarios
    
    def optimize_loan_strategy(
        self,
        principal: float,
        interest_rate: float,
        loan_type: LoanType,
        annual_income: Optional[float] = None,
        other_debts: float = 0,
        emergency_fund_months: int = 3,
    ) -> LoanOptimization:
        """
        Optimize loan repayment strategy.
        
        Args:
            principal: Loan principal
            interest_rate: Interest rate
            loan_type: Loan type
            annual_income: Annual income
            other_debts: Other debt obligations
            emergency_fund_months: Emergency fund available
            
        Returns:
            LoanOptimization with recommendations
        """
        scenarios = self.calculate_repayment_scenarios(
            principal, interest_rate, loan_type, annual_income
        )
        
        # Evaluate each scenario
        best_scenario = self._select_best_scenario(
            scenarios, annual_income, other_debts, emergency_fund_months
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            best_scenario, scenarios, loan_type, interest_rate
        )
        
        # Calculate savings vs standard
        standard_cost = scenarios["standard"].total_cost
        best_cost = best_scenario.total_cost
        savings = standard_cost - best_cost
        
        considerations = [
            "Assumes consistent income over repayment period",
            "Does not account for loan consolidation",
            "Tax implications of forgiveness not modeled",
            "Public Service Loan Forgiveness (PSLF) requires 120 payments",
            "Income-driven plans may extend interest costs",
        ]
        
        assumptions = [
            f"Interest rate: {interest_rate*100:.2f}%",
            f"Loan type: {loan_type.value}",
            "Assumes fixed rate (no rate changes)",
            "Based on current federal rules",
        ]
        
        return LoanOptimization(
            recommended_repayment_plan=best_scenario.repayment_plan,
            monthly_payment=best_scenario.monthly_payment,
            total_interest_cost=best_scenario.total_interest_paid,
            payoff_timeline=best_scenario.years_to_repay,
            savings_vs_standard=savings,
            key_recommendations=recommendations,
            considerations=considerations,
            confidence=0.80,
            assumptions=assumptions,
        )
    
    def evaluate_refinancing(
        self,
        current_principal: float,
        current_rate: float,
        current_term_years: float,
        current_age_years: float,
        refinance_rate: float,
        refinance_term_years: Optional[float] = None,
    ) -> Dict[str, float]:
        """
        Evaluate refinancing opportunity.
        
        Args:
            current_principal: Current loan balance
            current_rate: Current interest rate
            current_term_years: Years remaining on current loan
            current_age_years: Years already paid
            refinance_rate: Potential refinance rate
            refinance_term_years: Refinance term (defaults to full amortization)
            
        Returns:
            Refinancing analysis
        """
        if refinance_term_years is None:
            refinance_term_years = 10  # Standard
        
        # Current scenario
        current_monthly = self._calculate_monthly_payment(
            current_principal, current_rate, current_term_years * 12
        )
        current_remaining_payments = current_term_years * 12
        current_total_remaining = current_monthly * current_remaining_payments
        
        # Refinance scenario
        refinance_monthly = self._calculate_monthly_payment(
            current_principal, refinance_rate, refinance_term_years * 12
        )
        refinance_remaining_payments = refinance_term_years * 12
        refinance_total_cost = refinance_monthly * refinance_remaining_payments
        
        # Interest comparison
        current_interest_remaining = current_total_remaining - current_principal
        refinance_interest = refinance_total_cost - current_principal
        
        return {
            "current_monthly_payment": current_monthly,
            "refinance_monthly_payment": refinance_monthly,
            "monthly_savings": current_monthly - refinance_monthly,
            "current_term_remaining": current_term_years,
            "refinance_term": refinance_term_years,
            "current_total_interest_remaining": current_interest_remaining,
            "refinance_total_interest": refinance_interest,
            "interest_savings": current_interest_remaining - refinance_interest,
            "breakeven_months": self._calculate_breakeven(
                current_monthly, refinance_monthly
            ),
            "should_refinance": refinance_rate < current_rate,
        }
    
    def _calculate_standard_plan(
        self,
        principal: float,
        interest_rate: float,
        loan_type: LoanType,
    ) -> StudentLoanScenario:
        """Calculate standard 10-year repayment plan."""
        years = 10
        monthly_payment = self._calculate_monthly_payment(principal, interest_rate, years * 12)
        total_paid = monthly_payment * years * 12
        total_interest = total_paid - principal
        
        return StudentLoanScenario(
            loan_type=loan_type,
            principal=principal,
            interest_rate=interest_rate,
            repayment_plan=RepaymentPlan.STANDARD,
            monthly_payment=monthly_payment,
            total_interest_paid=total_interest,
            years_to_repay=years,
            total_cost=total_paid,
            forgiveness_eligible=False,
            forgiveness_timeline_years=None,
            confidence=0.95,
        )
    
    def _calculate_graduated_plan(
        self,
        principal: float,
        interest_rate: float,
        loan_type: LoanType,
    ) -> StudentLoanScenario:
        """Calculate graduated repayment plan (10 years, payments increase)."""
        years = 10
        months = years * 12
        
        # Start at standard payment rate, increase by 2% per year
        # Simplified: average of min and max payments
        min_payment = self._calculate_monthly_payment(principal, interest_rate, months)
        max_payment = min_payment * 1.2  # Max 20% higher
        average_payment = (min_payment + max_payment) / 2
        
        total_paid = average_payment * months
        total_interest = total_paid - principal
        
        return StudentLoanScenario(
            loan_type=loan_type,
            principal=principal,
            interest_rate=interest_rate,
            repayment_plan=RepaymentPlan.GRADUATED,
            monthly_payment=average_payment,
            total_interest_paid=total_interest,
            years_to_repay=years,
            total_cost=total_paid,
            forgiveness_eligible=False,
            forgiveness_timeline_years=None,
            confidence=0.90,
        )
    
    def _calculate_income_driven_plan(
        self,
        principal: float,
        interest_rate: float,
        loan_type: LoanType,
        annual_income: float,
        family_size: int,
    ) -> StudentLoanScenario:
        """Calculate income-driven repayment plan."""
        # Simplified: monthly payment = 10% of discretionary income / 12
        # Discretionary income = income - 150% of poverty line
        poverty_line = 14580 + (5060 * family_size)
        discretionary = max(0, annual_income - poverty_line * 1.5)
        monthly_payment = max(0, discretionary * 0.10 / 12)
        
        # 20 years to forgiveness
        years_to_forgiveness = 20
        total_payments = monthly_payment * years_to_forgiveness * 12
        
        # Amount forgiven
        forgiven = max(0, principal * (1 + interest_rate) ** years_to_forgiveness - total_payments)
        
        return StudentLoanScenario(
            loan_type=loan_type,
            principal=principal,
            interest_rate=interest_rate,
            repayment_plan=RepaymentPlan.INCOME_DRIVEN,
            monthly_payment=monthly_payment,
            total_interest_paid=0,  # Simplified
            years_to_repay=years_to_forgiveness,
            total_cost=total_payments,
            forgiveness_eligible=True,
            forgiveness_timeline_years=years_to_forgiveness,
            confidence=0.80,
        )
    
    def _calculate_paye_plan(
        self,
        principal: float,
        interest_rate: float,
        loan_type: LoanType,
        annual_income: float,
        family_size: int,
    ) -> StudentLoanScenario:
        """Calculate Pay As You Earn repayment plan."""
        # Similar to income-driven but lower payments
        poverty_line = 14580 + (5060 * family_size)
        discretionary = max(0, annual_income - poverty_line * 1.5)
        monthly_payment = max(0, discretionary * 0.10 / 12)  # 10% discretionary
        
        years_to_forgiveness = 20
        total_payments = monthly_payment * years_to_forgiveness * 12
        
        return StudentLoanScenario(
            loan_type=loan_type,
            principal=principal,
            interest_rate=interest_rate,
            repayment_plan=RepaymentPlan.PAY_AS_YOU_EARN,
            monthly_payment=monthly_payment,
            total_interest_paid=0,
            years_to_repay=years_to_forgiveness,
            total_cost=total_payments,
            forgiveness_eligible=True,
            forgiveness_timeline_years=years_to_forgiveness,
            confidence=0.80,
        )
    
    def _calculate_monthly_payment(
        self,
        principal: float,
        annual_rate: float,
        months: int,
    ) -> float:
        """Calculate monthly payment using amortization formula."""
        if months <= 0 or annual_rate < 0:
            return 0
        
        monthly_rate = annual_rate / 12
        
        if monthly_rate == 0:
            return principal / months
        
        # PMT = P * [r(1+r)^n] / [(1+r)^n - 1]
        numerator = principal * monthly_rate * ((1 + monthly_rate) ** months)
        denominator = ((1 + monthly_rate) ** months) - 1
        
        return numerator / denominator if denominator != 0 else 0
    
    def _select_best_scenario(
        self,
        scenarios: Dict[str, StudentLoanScenario],
        income: Optional[float],
        other_debts: float,
        emergency_fund_months: int,
    ) -> StudentLoanScenario:
        """Select best repayment scenario based on financial situation."""
        # If low emergency fund and other debts, prefer income-driven
        if emergency_fund_months < 3 and other_debts > 0 and "income_driven" in scenarios:
            return scenarios["income_driven"]
        
        # Otherwise prefer lowest total cost (standard plan usually wins)
        return scenarios.get("standard", list(scenarios.values())[0])
    
    def _generate_recommendations(
        self,
        best_scenario: StudentLoanScenario,
        all_scenarios: Dict[str, StudentLoanScenario],
        loan_type: LoanType,
        interest_rate: float,
    ) -> List[str]:
        """Generate recommendations."""
        recommendations = []
        
        if best_scenario.repayment_plan == RepaymentPlan.INCOME_DRIVEN:
            recommendations.append("Income-driven plan recommended to manage cash flow")
            recommendations.append("Consider PSLF if working in public service")
        else:
            recommendations.append("Standard repayment plan minimizes total interest cost")
        
        if interest_rate > 0.065:
            recommendations.append("Consider refinancing if credit improves")
        
        if loan_type == LoanType.FEDERAL_PLUS:
            recommendations.append("High interest rate: explore consolidation options")
        
        return recommendations
    
    def _calculate_breakeven(self, current_payment: float, refinance_payment: float) -> int:
        """Calculate breakeven months for refinancing."""
        if current_payment <= refinance_payment:
            return 0
        
        savings_per_month = current_payment - refinance_payment
        # Assuming typical closing costs of $500-1000
        breakeven = 1000 / savings_per_month if savings_per_month > 0 else 0
        
        return int(breakeven)
