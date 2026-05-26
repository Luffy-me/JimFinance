"""
Advanced Scenario Modeling - Employment shocks, tax impacts, and life events.

Extends scenario analysis with:
- Employment shock scenarios (job loss, salary cut, new employment)
- Tax impact modeling (country-specific, progressive tax rates)
- Loan/debt scenarios (student loans, mortgages, credit cards)
- Life event scenarios (medical emergency, family changes)
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

import numpy as np

logger = logging.getLogger(__name__)


class EmploymentShockType(str, Enum):
    """Employment shock scenarios."""
    JOB_LOSS = "job_loss"
    SALARY_CUT = "salary_cut"
    FURLOUGH = "furlough"
    SIDE_GIG = "side_gig"
    BONUS = "bonus"


class TaxRegime(str, Enum):
    """Tax calculation regime by country."""
    US = "us"
    RUSSIA = "russia"
    EU = "eu"
    SIMPLE = "simple"


@dataclass
class AdvancedScenario:
    """Advanced scenario with life event modeling."""
    scenario_name: str
    scenario_type: str  # employment, tax, loan, life_event, combination
    baseline_income: float
    baseline_expenses: float
    scenario_income: float
    scenario_expenses: float
    runway_months: float
    stress_level: str  # low, medium, high, critical
    probability: float  # 0-1
    recovery_timeline_months: Optional[int]
    recommendations: List[str]
    assumptions: List[str]


class EmploymentShockAnalyzer:
    """Analyzes financial impact of employment changes."""
    
    def __init__(self):
        """Initialize employment shock analyzer."""
        self.logger = logger
    
    def model_job_loss(
        self,
        current_monthly_income: float,
        monthly_expenses: float,
        current_balance: float,
        emergency_fund_months: int = 6,
        unemployment_benefit_months: int = 3,
        unemployment_benefit_percent: float = 0.60,  # 60% of income
    ) -> AdvancedScenario:
        """
        Model financial impact of job loss.
        
        Args:
            current_monthly_income: Current monthly income
            monthly_expenses: Monthly expenses
            current_balance: Current savings
            emergency_fund_months: Target emergency fund (months)
            unemployment_benefit_months: How many months unemployment lasts
            unemployment_benefit_percent: Unemployment benefit as % of income
            
        Returns:
            AdvancedScenario with job loss impact
        """
        emergency_fund_target = monthly_expenses * emergency_fund_months
        
        # Phase 1: Unemployment benefits (partial income)
        unemployment_income = current_monthly_income * unemployment_benefit_percent
        monthly_deficit_phase1 = monthly_expenses - unemployment_income
        
        # Phase 2: No income (after benefits end)
        monthly_deficit_phase2 = monthly_expenses
        
        # Calculate runway
        balance_after_phase1 = current_balance - (monthly_deficit_phase1 * unemployment_benefit_months)
        
        if balance_after_phase1 <= 0:
            runway_months = (current_balance / monthly_deficit_phase1) if monthly_deficit_phase1 > 0 else float('inf')
        else:
            phase2_runway = balance_after_phase1 / monthly_deficit_phase2 if monthly_deficit_phase2 > 0 else float('inf')
            runway_months = unemployment_benefit_months + phase2_runway
        
        # Determine stress level
        if runway_months < 1:
            stress_level = "critical"
        elif runway_months < 3:
            stress_level = "high"
        elif runway_months < 6:
            stress_level = "medium"
        else:
            stress_level = "low"
        
        recommendations = []
        if current_balance < emergency_fund_target:
            recommendations.append(
                f"Build emergency fund to {emergency_fund_months} months expenses "
                f"(need {emergency_fund_target - current_balance:,.0f} more)"
            )
        recommendations.extend([
            "Immediately reduce discretionary spending by 20-30%",
            "Prioritize job search and skill development",
            "Consider part-time or contract work within weeks",
            "Review subscription and recurring expenses",
        ])
        
        return AdvancedScenario(
            scenario_name="Job Loss",
            scenario_type="employment",
            baseline_income=current_monthly_income,
            baseline_expenses=monthly_expenses,
            scenario_income=0,
            scenario_expenses=monthly_expenses,
            runway_months=runway_months,
            stress_level=stress_level,
            probability=0.02,  # ~2% annual probability
            recovery_timeline_months=3,
            recommendations=recommendations,
            assumptions=[
                f"Unemployment benefits: {unemployment_benefit_percent*100:.0f}% of income for {unemployment_benefit_months} months",
                "No secondary income sources",
                "Fixed expenses (cannot reduce)",
                "Assumes job search takes 3-6 months",
            ],
        )
    
    def model_salary_cut(
        self,
        current_monthly_income: float,
        monthly_expenses: float,
        current_balance: float,
        salary_reduction_percent: float = 0.20,  # 20% cut
        duration_months: int = 6,
    ) -> AdvancedScenario:
        """
        Model financial impact of salary reduction.
        
        Args:
            current_monthly_income: Current monthly income
            monthly_expenses: Monthly expenses
            current_balance: Current savings
            salary_reduction_percent: Percentage salary reduction
            duration_months: How many months the cut lasts
            
        Returns:
            AdvancedScenario with salary cut impact
        """
        reduced_income = current_monthly_income * (1 - salary_reduction_percent)
        monthly_deficit = monthly_expenses - reduced_income
        
        if monthly_deficit > 0:
            # Drawing down savings
            total_deficit = monthly_deficit * duration_months
            balance_after = current_balance - total_deficit
            
            if balance_after < 0:
                runway_months = (current_balance / monthly_deficit) if monthly_deficit > 0 else float('inf')
            else:
                runway_months = duration_months  # Can sustain for the full period
            
            stress_level = "medium" if balance_after > 0 else "high"
        else:
            # No deficit
            runway_months = float('inf')
            balance_after = current_balance
            stress_level = "low"
        
        recommendations = [
            f"Reduce discretionary spending by at least {salary_reduction_percent*100:.0f}%",
            "Prioritize cost-cutting: subscriptions, dining, entertainment",
            "Consider adjusting housing if possible",
            "Increase emergency fund contributions once salary restored",
        ]
        
        return AdvancedScenario(
            scenario_name=f"{salary_reduction_percent*100:.0f}% Salary Cut for {duration_months} Months",
            scenario_type="employment",
            baseline_income=current_monthly_income,
            baseline_expenses=monthly_expenses,
            scenario_income=reduced_income,
            scenario_expenses=monthly_expenses,
            runway_months=runway_months if monthly_deficit > 0 else float('inf'),
            stress_level=stress_level,
            probability=0.05,
            recovery_timeline_months=0,
            recommendations=recommendations,
            assumptions=[
                f"Salary reduction: {salary_reduction_percent*100:.0f}%",
                f"Duration: {duration_months} months",
                "Fixed expenses remain constant",
            ],
        )


class TaxImpactAnalyzer:
    """Analyzes tax impact on financial scenarios."""
    
    # US 2024 tax brackets (single filer)
    US_TAX_BRACKETS = [
        (11600, 0.10),
        (47150, 0.12),
        (100525, 0.22),
        (191950, 0.24),
        (243725, 0.32),
        (609350, 0.35),
        (float('inf'), 0.37),
    ]
    
    # Russian tax rate (simplified, personal income tax)
    RUSSIA_TAX_RATE = 0.13
    
    # EU average (varies by country, using rough average)
    EU_TAX_BRACKETS = [
        (20000, 0.18),
        (40000, 0.28),
        (60000, 0.35),
        (float('inf'), 0.42),
    ]
    
    def __init__(self, regime: TaxRegime = TaxRegime.US):
        """
        Initialize tax analyzer.
        
        Args:
            regime: Tax calculation regime
        """
        self.logger = logger
        self.regime = regime
    
    def calculate_net_income(
        self,
        gross_income: float,
        deductions: float = 0,
    ) -> Dict[str, float]:
        """
        Calculate net income after taxes.
        
        Args:
            gross_income: Gross annual income
            deductions: Tax-deductible deductions
            
        Returns:
            Dictionary with gross, taxes, net
        """
        taxable_income = max(0, gross_income - deductions)
        
        if self.regime == TaxRegime.US:
            taxes = self._calculate_us_taxes(taxable_income)
            effective_rate = taxes / gross_income if gross_income > 0 else 0
        elif self.regime == TaxRegime.RUSSIA:
            taxes = taxable_income * self.RUSSIA_TAX_RATE
            effective_rate = taxes / gross_income if gross_income > 0 else 0
        elif self.regime == TaxRegime.EU:
            taxes = self._calculate_eu_taxes(taxable_income)
            effective_rate = taxes / gross_income if gross_income > 0 else 0
        else:  # SIMPLE
            taxes = gross_income * 0.20  # 20% flat
            effective_rate = 0.20
        
        return {
            "gross_income": gross_income,
            "deductions": deductions,
            "taxable_income": taxable_income,
            "taxes": taxes,
            "net_income": gross_income - taxes,
            "effective_tax_rate": effective_rate,
        }
    
    def income_tax_scenario(
        self,
        current_gross_income: float,
        monthly_expenses: float,
        current_balance: float,
        projected_income_change: float = 0.0,  # +0.2 for 20% raise
        investment_income: float = 0,
    ) -> AdvancedScenario:
        """
        Model scenario with income tax implications.
        
        Args:
            current_gross_income: Current gross annual income
            monthly_expenses: Monthly expenses
            current_balance: Current balance
            projected_income_change: Percentage change in income
            investment_income: Additional investment income (bonds, stocks)
            
        Returns:
            AdvancedScenario with tax impact
        """
        new_gross_income = current_gross_income * (1 + projected_income_change)
        total_income = new_gross_income + investment_income
        
        # Calculate net income after taxes
        current_net = self.calculate_net_income(current_gross_income)["net_income"]
        new_net = self.calculate_net_income(total_income)["net_income"]
        
        current_monthly_net = current_net / 12
        new_monthly_net = new_net / 12
        
        monthly_surplus = new_monthly_net - monthly_expenses
        
        return AdvancedScenario(
            scenario_name=f"Tax Impact: {projected_income_change*100:+.0f}% Income Change",
            scenario_type="tax",
            baseline_income=current_monthly_net,
            baseline_expenses=monthly_expenses,
            scenario_income=new_monthly_net,
            scenario_expenses=monthly_expenses,
            runway_months=float('inf') if monthly_surplus > 0 else (current_balance / abs(monthly_surplus)),
            stress_level="low" if monthly_surplus > 0 else "high",
            probability=1.0,
            recovery_timeline_months=None,
            recommendations=[
                f"Net income change: {new_monthly_net - current_monthly_net:+,.0f}/month",
                "Review tax withholding and quarterly payments",
                "Consider tax-advantaged savings (401k, IRA, HSA)",
            ],
            assumptions=[
                f"Tax regime: {self.regime.value}",
                f"Projected income change: {projected_income_change*100:+.0f}%",
                "Tax rates remain constant",
            ],
        )
    
    @staticmethod
    def _calculate_us_taxes(taxable_income: float) -> float:
        """Calculate US income tax."""
        taxes = 0.0
        previous_limit = 0
        
        for bracket_limit, bracket_rate in TaxImpactAnalyzer.US_TAX_BRACKETS:
            if taxable_income > previous_limit:
                taxable_in_bracket = min(taxable_income, bracket_limit) - previous_limit
                taxes += taxable_in_bracket * bracket_rate
                previous_limit = bracket_limit
            else:
                break
        
        return taxes
    
    @staticmethod
    def _calculate_eu_taxes(taxable_income: float) -> float:
        """Calculate EU income tax."""
        taxes = 0.0
        previous_limit = 0
        
        for bracket_limit, bracket_rate in TaxImpactAnalyzer.EU_TAX_BRACKETS:
            if taxable_income > previous_limit:
                taxable_in_bracket = min(taxable_income, bracket_limit) - previous_limit
                taxes += taxable_in_bracket * bracket_rate
                previous_limit = bracket_limit
            else:
                break
        
        return taxes


class DebtScenarioAnalyzer:
    """Analyzes financial impact of debt and loans."""
    
    def model_student_loan(
        self,
        loan_amount: float,
        monthly_expenses: float,
        monthly_income: float,
        current_balance: float,
        interest_rate: float = 0.045,  # 4.5% annual
        repayment_years: int = 10,
    ) -> AdvancedScenario:
        """
        Model student loan impact on finances.
        
        Args:
            loan_amount: Total loan amount
            monthly_expenses: Current monthly expenses
            monthly_income: Monthly income
            current_balance: Current balance
            interest_rate: Annual interest rate
            repayment_years: Repayment period
            
        Returns:
            AdvancedScenario with loan impact
        """
        # Calculate monthly payment (standard formula)
        monthly_rate = interest_rate / 12
        num_payments = repayment_years * 12
        monthly_payment = (
            loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) /
            ((1 + monthly_rate) ** num_payments - 1)
        )
        
        total_interest = (monthly_payment * num_payments) - loan_amount
        
        new_monthly_expenses = monthly_expenses + monthly_payment
        monthly_surplus = monthly_income - new_monthly_expenses
        
        return AdvancedScenario(
            scenario_name=f"Student Loan: ${loan_amount:,.0f}",
            scenario_type="loan",
            baseline_income=monthly_income,
            baseline_expenses=monthly_expenses,
            scenario_income=monthly_income,
            scenario_expenses=new_monthly_expenses,
            runway_months=float('inf') if monthly_surplus > 0 else 0,
            stress_level="low" if monthly_surplus > 0 else "high",
            probability=1.0,
            recovery_timeline_months=repayment_years * 12,
            recommendations=[
                f"Monthly payment: ${monthly_payment:,.0f}",
                f"Total interest paid: ${total_interest:,.0f}",
                "Consider income-driven repayment plans if struggling",
                "Refinance if credit score improves",
            ],
            assumptions=[
                f"Interest rate: {interest_rate*100:.1f}% annual",
                f"Repayment period: {repayment_years} years",
                "Standard repayment plan (no deferment)",
            ],
        )
    
    def model_credit_card_debt(
        self,
        balance: float,
        monthly_expenses: float,
        monthly_income: float,
        current_balance: float,
        interest_rate: float = 0.20,  # 20% annual (typical)
        monthly_payment: Optional[float] = None,
    ) -> AdvancedScenario:
        """
        Model credit card debt impact.
        
        Args:
            balance: Credit card balance
            monthly_expenses: Monthly expenses
            monthly_income: Monthly income
            current_balance: Savings balance
            interest_rate: Annual interest rate
            monthly_payment: Monthly payment (if None, uses minimum)
            
        Returns:
            AdvancedScenario
        """
        if monthly_payment is None:
            # Minimum payment typically 2% of balance
            monthly_payment = balance * 0.02
        
        # Calculate payoff time
        monthly_rate = interest_rate / 12
        months_to_payoff = 0
        remaining_balance = balance
        total_interest = 0
        
        while remaining_balance > 0 and months_to_payoff < 360:  # Max 30 years
            interest_charged = remaining_balance * monthly_rate
            total_interest += interest_charged
            remaining_balance -= (monthly_payment - interest_charged)
            months_to_payoff += 1
        
        new_monthly_expenses = monthly_expenses + monthly_payment
        monthly_surplus = monthly_income - new_monthly_expenses
        
        return AdvancedScenario(
            scenario_name=f"Credit Card Debt: ${balance:,.0f}",
            scenario_type="loan",
            baseline_income=monthly_income,
            baseline_expenses=monthly_expenses,
            scenario_income=monthly_income,
            scenario_expenses=new_monthly_expenses,
            runway_months=float('inf') if monthly_surplus > 0 else 0,
            stress_level="high",
            probability=1.0,
            recovery_timeline_months=months_to_payoff,
            recommendations=[
                f"Payoff time: {months_to_payoff} months (~{months_to_payoff/12:.1f} years)",
                f"Total interest: ${total_interest:,.0f}",
                "Pay more than minimum to reduce interest",
                "Consider balance transfer or consolidation loan",
                "Avoid new charges while paying off",
            ],
            assumptions=[
                f"Interest rate: {interest_rate*100:.1f}% annual",
                f"Monthly payment: ${monthly_payment:,.0f}",
                "No new charges added",
            ],
        )


class LifeEventAnalyzer:
    """Analyzes financial impact of life events."""
    
    def model_medical_emergency(
        self,
        emergency_cost: float,
        monthly_expenses: float,
        monthly_income: float,
        current_balance: float,
        recovery_months: int = 3,
    ) -> AdvancedScenario:
        """
        Model financial impact of medical emergency.
        
        Args:
            emergency_cost: Cost of medical emergency
            monthly_expenses: Monthly expenses
            monthly_income: Monthly income
            current_balance: Current savings
            recovery_months: Months to recover (higher expenses during this time)
            
        Returns:
            AdvancedScenario
        """
        balance_after_emergency = current_balance - emergency_cost
        additional_recovery_costs = monthly_expenses * 0.3 * recovery_months  # 30% higher
        
        stress_level = "critical" if balance_after_emergency < 0 else (
            "high" if balance_after_emergency < monthly_expenses * 3 else "medium"
        )
        
        return AdvancedScenario(
            scenario_name=f"Medical Emergency: ${emergency_cost:,.0f}",
            scenario_type="life_event",
            baseline_income=monthly_income,
            baseline_expenses=monthly_expenses,
            scenario_income=monthly_income,
            scenario_expenses=monthly_expenses * 1.3,  # +30% during recovery
            runway_months=balance_after_emergency / monthly_income if monthly_income > 0 else 0,
            stress_level=stress_level,
            probability=0.15,  # ~15% annual probability
            recovery_timeline_months=recovery_months,
            recommendations=[
                "Review health insurance coverage",
                "Negotiate medical bills with providers",
                "Consider payment plans for remaining balance",
                "Rebuild emergency fund after recovery",
            ],
            assumptions=[
                f"Emergency cost: ${emergency_cost:,.0f}",
                f"Recovery period: {recovery_months} months",
                "Additional expenses during recovery: +30%",
            ],
        )
