"""
Financial Runway Engine - Advanced runway calculations with scenario analysis.

Calculates how long finances can sustain current spending patterns.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from decimal import Decimal
import statistics

logger = logging.getLogger(__name__)


@dataclass
class RunwayScenario:
    """Runway projection for a specific scenario."""
    scenario_name: str
    burn_rate_monthly: float
    starting_balance: float
    runway_days: float
    runway_months: float
    exhaustion_date: datetime
    confidence_score: float
    assumptions: Dict[str, any]


@dataclass
class RunwayAnalysis:
    """Complete runway analysis with multiple scenarios."""
    primary_scenario: RunwayScenario
    optimistic_scenario: Optional[RunwayScenario]
    pessimistic_scenario: Optional[RunwayScenario]
    emergency_fund_status: Dict[str, any]
    sustainability_score: float
    recommendations: List[str]


class FinancialRunwayEngine:
    """Advanced runway calculations and scenario analysis."""
    
    # Emergency fund recommendations
    EMERGENCY_FUND_MONTHS = 3  # Minimum recommended
    EMERGENCY_FUND_OPTIMAL = 6
    
    # Scenario burn rate multipliers
    OPTIMISTIC_BURN_MULTIPLIER = 0.8  # 20% cost reduction
    PESSIMISTIC_BURN_MULTIPLIER = 1.2  # 20% cost increase
    
    def __init__(self):
        """Initialize runway engine."""
        self.logger = logger
    
    def calculate_runway_analysis(
        self,
        account_balance: Decimal,
        monthly_burn_rate: float,
        monthly_income: Optional[float] = None,
        transactions: Optional[List[Dict]] = None,
        emergency_fund_target: Optional[float] = None,
    ) -> RunwayAnalysis:
        """
        Calculate comprehensive runway analysis with scenarios.
        
        Args:
            account_balance: Current account balance
            monthly_burn_rate: Average monthly expenses
            monthly_income: Average monthly income (optional)
            transactions: Historical transactions (optional)
            emergency_fund_target: Target emergency fund (optional)
        
        Returns:
            RunwayAnalysis object with primary and scenario projections
        """
        account_balance = float(account_balance)
        
        if monthly_burn_rate <= 0:
            return self._zero_burn_analysis(account_balance)
        
        # Calculate primary scenario (current spend rate)
        primary = self._calculate_scenario(
            scenario_name='Current Spending',
            account_balance=account_balance,
            monthly_burn_rate=monthly_burn_rate,
            monthly_income=monthly_income,
        )
        
        # Optimistic scenario (20% cost reduction)
        optimistic_burn = monthly_burn_rate * self.OPTIMISTIC_BURN_MULTIPLIER
        optimistic = self._calculate_scenario(
            scenario_name='Reduced Spending',
            account_balance=account_balance,
            monthly_burn_rate=optimistic_burn,
            monthly_income=monthly_income,
            assumptions={'description': '20% cost reduction', 'burn_rate_reduction': 0.2},
        )
        
        # Pessimistic scenario (20% cost increase)
        pessimistic_burn = monthly_burn_rate * self.PESSIMISTIC_BURN_MULTIPLIER
        pessimistic = self._calculate_scenario(
            scenario_name='Increased Spending',
            account_balance=account_balance,
            monthly_burn_rate=pessimistic_burn,
            monthly_income=monthly_income,
            assumptions={'description': '20% cost increase', 'burn_rate_increase': 0.2},
        )
        
        # Emergency fund analysis
        if emergency_fund_target is None:
            emergency_fund_target = monthly_burn_rate * self.EMERGENCY_FUND_OPTIMAL
        
        emergency_analysis = self._analyze_emergency_fund(
            account_balance=account_balance,
            monthly_burn_rate=monthly_burn_rate,
            emergency_fund_target=emergency_fund_target,
        )
        
        # Sustainability score
        sustainability = self._calculate_sustainability_score(
            primary_scenario=primary,
            monthly_income=monthly_income,
            emergency_analysis=emergency_analysis,
        )
        
        # Recommendations
        recommendations = self._generate_recommendations(
            primary=primary,
            optimistic=optimistic,
            pessimistic=pessimistic,
            monthly_income=monthly_income,
            emergency_analysis=emergency_analysis,
        )
        
        return RunwayAnalysis(
            primary_scenario=primary,
            optimistic_scenario=optimistic,
            pessimistic_scenario=pessimistic,
            emergency_fund_status=emergency_analysis,
            sustainability_score=round(sustainability, 1),
            recommendations=recommendations,
        )
    
    def _calculate_scenario(
        self,
        scenario_name: str,
        account_balance: float,
        monthly_burn_rate: float,
        monthly_income: Optional[float] = None,
        assumptions: Optional[Dict] = None,
    ) -> RunwayScenario:
        """Calculate runway for a specific scenario."""
        if assumptions is None:
            assumptions = {}
        
        # Calculate net burn (burn - income)
        if monthly_income and monthly_income > 0:
            net_burn = monthly_burn_rate - monthly_income
            # If income exceeds burn, account grows
            if net_burn <= 0:
                return RunwayScenario(
                    scenario_name=scenario_name,
                    burn_rate_monthly=monthly_burn_rate,
                    starting_balance=account_balance,
                    runway_days=999999,  # Indefinite
                    runway_months=9999,
                    exhaustion_date=datetime.now() + timedelta(days=36500),  # 100 years
                    confidence_score=0.9,
                    assumptions={**assumptions, 'monthly_income': monthly_income, 'net_positive': True},
                )
        else:
            net_burn = monthly_burn_rate
        
        # Calculate runway
        if net_burn <= 0:
            # Net positive scenario - no exhaustion
            return RunwayScenario(
                scenario_name=scenario_name,
                burn_rate_monthly=monthly_burn_rate,
                starting_balance=account_balance,
                runway_days=999999,
                runway_months=9999,
                exhaustion_date=datetime.now() + timedelta(days=36500),
                confidence_score=0.95,
                assumptions={**assumptions, 'monthly_income': monthly_income, 'net_positive': True},
            )
        
        # Calculate days and months of runway
        daily_burn = net_burn / 30  # Approximate
        
        if daily_burn > 0:
            runway_days = account_balance / daily_burn
            runway_months = runway_days / 30
        else:
            runway_days = 999999
            runway_months = 9999
        
        # Calculate exhaustion date
        exhaustion_date = datetime.now() + timedelta(days=runway_days)
        
        # Confidence score based on burn rate stability
        confidence = 0.75  # Base confidence
        
        return RunwayScenario(
            scenario_name=scenario_name,
            burn_rate_monthly=round(net_burn, 2),
            starting_balance=round(account_balance, 2),
            runway_days=round(runway_days, 1),
            runway_months=round(runway_months, 1),
            exhaustion_date=exhaustion_date,
            confidence_score=round(confidence, 2),
            assumptions={
                **assumptions,
                'monthly_income': monthly_income,
                'daily_burn': round(daily_burn, 2),
            },
        )
    
    def _analyze_emergency_fund(
        self,
        account_balance: float,
        monthly_burn_rate: float,
        emergency_fund_target: float,
    ) -> Dict:
        """Analyze emergency fund adequacy."""
        if monthly_burn_rate <= 0:
            return {
                'current_balance': round(account_balance, 2),
                'target_amount': round(emergency_fund_target, 2),
                'coverage_months': 9999,
                'status': 'sufficient',
                'recommendation': 'No burn rate detected - emergency fund not applicable',
            }
        
        coverage_months = account_balance / monthly_burn_rate
        
        if coverage_months >= self.EMERGENCY_FUND_OPTIMAL:
            status = 'excellent'
            recommendation = 'Emergency fund is well-funded. Consider allocating excess funds.'
        elif coverage_months >= self.EMERGENCY_FUND_MONTHS:
            status = 'adequate'
            recommendation = 'Emergency fund is sufficient. Aim to build to 6 months.'
        else:
            status = 'insufficient'
            shortfall = (monthly_burn_rate * self.EMERGENCY_FUND_MONTHS) - account_balance
            recommendation = f'Emergency fund is insufficient. Build up ${shortfall:,.0f} more.'
        
        return {
            'current_balance': round(account_balance, 2),
            'target_amount': round(emergency_fund_target, 2),
            'shortfall': round(max(0, emergency_fund_target - account_balance), 2),
            'coverage_months': round(coverage_months, 1),
            'status': status,
            'recommendation': recommendation,
        }
    
    def _calculate_sustainability_score(
        self,
        primary_scenario: RunwayScenario,
        monthly_income: Optional[float] = None,
        emergency_analysis: Optional[Dict] = None,
    ) -> float:
        """
        Calculate overall sustainability score (0-100).
        
        Factors:
        - Runway duration (40%)
        - Income vs expense ratio (30%)
        - Emergency fund status (30%)
        """
        score = 0.0
        
        # Runway component (40%)
        if primary_scenario.runway_months >= 36:
            score += 40
        elif primary_scenario.runway_months >= 12:
            score += 30
        elif primary_scenario.runway_months >= 6:
            score += 20
        elif primary_scenario.runway_months >= 3:
            score += 10
        else:
            score += max(0, (primary_scenario.runway_months / 3) * 10)
        
        # Income vs expense component (30%)
        if monthly_income and monthly_income > 0:
            income_ratio = monthly_income / primary_scenario.burn_rate_monthly
            if income_ratio >= 1.2:
                score += 30
            elif income_ratio >= 1.0:
                score += 20
            elif income_ratio >= 0.8:
                score += 10
        
        # Emergency fund component (30%)
        if emergency_analysis:
            if emergency_analysis['status'] == 'excellent':
                score += 30
            elif emergency_analysis['status'] == 'adequate':
                score += 20
            elif emergency_analysis['status'] == 'insufficient':
                score += 5
        
        return min(100.0, score)
    
    def _generate_recommendations(
        self,
        primary: RunwayScenario,
        optimistic: RunwayScenario,
        pessimistic: RunwayScenario,
        monthly_income: Optional[float] = None,
        emergency_analysis: Optional[Dict] = None,
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Runway recommendations
        if primary.runway_months < 3:
            recommendations.append('🚨 CRITICAL: Runway is less than 3 months. Immediate cost reduction needed.')
        elif primary.runway_months < 6:
            recommendations.append('⚠️ WARNING: Runway is less than 6 months. Start planning cost cuts.')
        
        # Income recommendations
        if monthly_income is None or monthly_income == 0:
            recommendations.append('💡 Establish stable income to improve sustainability.')
        elif monthly_income < primary.burn_rate_monthly * 0.9:
            shortfall = primary.burn_rate_monthly - monthly_income
            recommendations.append(f'💰 Income covers {monthly_income/primary.burn_rate_monthly*100:.0f}% of expenses. Gap: ${shortfall:,.0f}/month')
        
        # Emergency fund recommendations
        if emergency_analysis and emergency_analysis['status'] == 'insufficient':
            recommendations.append(f"🛡️ Build emergency fund: {emergency_analysis['recommendation']}")
        
        # Scenario-based recommendations
        if pessimistic.runway_months < 2:
            recommendations.append('⚠️ In pessimistic scenario (20% cost increase), runway drops significantly.')
        
        if optimistic.runway_months > primary.runway_months * 1.5:
            opportunities = optimistic.runway_months - primary.runway_months
            recommendations.append(f'💡 Even a 20% cost reduction extends runway by {opportunities:.0f} months.')
        
        return recommendations
    
    def _zero_burn_analysis(self, account_balance: float) -> RunwayAnalysis:
        """Return analysis for zero burn rate."""
        zero_scenario = RunwayScenario(
            scenario_name='Current Spending',
            burn_rate_monthly=0.0,
            starting_balance=account_balance,
            runway_days=999999,
            runway_months=9999,
            exhaustion_date=datetime.now() + timedelta(days=36500),
            confidence_score=1.0,
            assumptions={'zero_burn_rate': True},
        )
        
        return RunwayAnalysis(
            primary_scenario=zero_scenario,
            optimistic_scenario=zero_scenario,
            pessimistic_scenario=zero_scenario,
            emergency_fund_status={
                'current_balance': account_balance,
                'target_amount': 0,
                'status': 'infinite',
                'recommendation': 'No recurring expenses detected.',
            },
            sustainability_score=100.0,
            recommendations=['No burn rate detected. Financial position is sustainable indefinitely.'],
        )
    
    def calculate_runway_by_spending_level(
        self,
        account_balance: Decimal,
        monthly_burn_rate: float,
    ) -> Dict[str, any]:
        """
        Calculate runway at different spending reduction levels.
        
        Returns dict with runway at 10%, 25%, 50% cost reductions.
        """
        account_balance = float(account_balance)
        
        reductions = {
            '10% reduction': 0.9,
            '25% reduction': 0.75,
            '50% reduction': 0.5,
        }
        
        results = {}
        
        for label, multiplier in reductions.items():
            reduced_burn = monthly_burn_rate * multiplier
            if reduced_burn > 0:
                runway_days = account_balance / (reduced_burn / 30)
                runway_months = runway_days / 30
            else:
                runway_days = 999999
                runway_months = 9999
            
            results[label] = {
                'monthly_spend': round(reduced_burn, 2),
                'runway_months': round(runway_months, 1),
                'runway_days': round(runway_days, 1),
            }
        
        return results
