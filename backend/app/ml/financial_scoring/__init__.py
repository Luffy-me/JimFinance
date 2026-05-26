"""Financial Health Scoring Engine

Comprehensive financial health assessment combining multiple indicators:
- Cash flow stability
- Savings rate
- Expense trends
- Runway health
- Subscription efficiency
- Debt management
- Emergency fund adequacy
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class HealthScoreComponent:
    """Individual health score component"""
    name: str
    score: float  # 0-100
    weight: float  # 0-1, sum should be 1.0
    trend: str  # "improving", "stable", "declining"
    insight: str
    recommendation: str


@dataclass
class FinancialHealthScore:
    """Overall financial health assessment"""
    overall_score: float  # 0-100
    score_grade: str  # A+, A, B+, B, C, D, F
    components: List[HealthScoreComponent]
    risk_level: str  # low, medium, high, critical
    confidence: float  # 0-1, how confident we are
    insights: List[str]
    recommendations: List[str]
    generated_at: datetime


class FinancialHealthScoringEngine:
    """Calculates comprehensive financial health score"""
    
    COMPONENT_WEIGHTS = {
        "savings_rate": 0.20,
        "cash_flow_stability": 0.20,
        "expense_trends": 0.15,
        "runway_health": 0.25,
        "subscription_efficiency": 0.10,
        "emergency_fund": 0.10,
    }
    
    def __init__(self):
        """Initialize scoring engine."""
        pass
    
    def calculate_health_score(
        self,
        transactions: List[Dict],
        account_balance: Decimal,
        monthly_income: Optional[float] = None,
        monthly_expenses: Optional[float] = None,
        subscriptions: Optional[List[Dict]] = None,
        debt: Optional[float] = None,
        emergency_fund_target: Optional[float] = None,
    ) -> FinancialHealthScore:
        """
        Calculate comprehensive financial health score.
        
        Args:
            transactions: Historical transactions
            account_balance: Current account balance
            monthly_income: Average monthly income
            monthly_expenses: Average monthly expenses
            subscriptions: List of subscriptions
            debt: Total outstanding debt
            emergency_fund_target: Target emergency fund
        
        Returns:
            FinancialHealthScore with breakdown
        """
        try:
            # Calculate component scores
            components = []
            weighted_total = 0.0
            
            # 1. Savings Rate Score
            savings_component = self._calculate_savings_rate_score(
                transactions, monthly_income, monthly_expenses
            )
            components.append(savings_component)
            weighted_total += savings_component.score * savings_component.weight
            
            # 2. Cash Flow Stability Score
            stability_component = self._calculate_cash_flow_stability_score(
                transactions, monthly_income
            )
            components.append(stability_component)
            weighted_total += stability_component.score * stability_component.weight
            
            # 3. Expense Trends Score
            trends_component = self._calculate_expense_trends_score(
                transactions
            )
            components.append(trends_component)
            weighted_total += trends_component.score * trends_component.weight
            
            # 4. Runway Health Score
            runway_component = self._calculate_runway_health_score(
                account_balance, monthly_expenses
            )
            components.append(runway_component)
            weighted_total += runway_component.score * runway_component.weight
            
            # 5. Subscription Efficiency Score
            subscription_component = self._calculate_subscription_efficiency_score(
                subscriptions, monthly_expenses
            )
            components.append(subscription_component)
            weighted_total += subscription_component.score * subscription_component.weight
            
            # 6. Emergency Fund Score
            emergency_component = self._calculate_emergency_fund_score(
                account_balance, monthly_expenses, emergency_fund_target
            )
            components.append(emergency_component)
            weighted_total += emergency_component.score * emergency_component.weight
            
            # Calculate overall score and risk level
            overall_score = max(0, min(100, weighted_total))
            risk_level = self._assess_risk_level(overall_score)
            grade = self._score_to_grade(overall_score)
            
            # Calculate confidence
            confidence = self._calculate_confidence(transactions, monthly_income)
            
            # Generate insights and recommendations
            insights = self._generate_insights(components, overall_score)
            recommendations = self._generate_recommendations(components, overall_score)
            
            return FinancialHealthScore(
                overall_score=overall_score,
                score_grade=grade,
                components=components,
                risk_level=risk_level,
                confidence=confidence,
                insights=insights,
                recommendations=recommendations,
                generated_at=datetime.now(),
            )
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            # Return minimal score on error
            return FinancialHealthScore(
                overall_score=50,
                score_grade="C",
                components=[],
                risk_level="medium",
                confidence=0.0,
                insights=["Could not calculate health score"],
                recommendations=["Try adding more transaction data"],
                generated_at=datetime.now(),
            )
    
    def _calculate_savings_rate_score(
        self,
        transactions: List[Dict],
        monthly_income: Optional[float],
        monthly_expenses: Optional[float],
    ) -> HealthScoreComponent:
        """Calculate savings rate component score."""
        try:
            if not monthly_income or monthly_income <= 0:
                return HealthScoreComponent(
                    name="Savings Rate",
                    score=50,
                    weight=self.COMPONENT_WEIGHTS["savings_rate"],
                    trend="unknown",
                    insight="No income data",
                    recommendation="Add income to your profile for better insights",
                )
            
            if not monthly_expenses:
                monthly_expenses = self._calculate_monthly_expenses(transactions)
            
            savings_rate = (monthly_income - monthly_expenses) / monthly_income
            
            # Score: 0-100 based on savings rate
            # 50%+ = 100, 30-50% = 80, 10-30% = 60, 0-10% = 40, negative = 20
            if savings_rate >= 0.5:
                score = 100
                trend = "excellent"
            elif savings_rate >= 0.3:
                score = 80
                trend = "good"
            elif savings_rate >= 0.1:
                score = 60
                trend = "fair"
            elif savings_rate >= 0:
                score = 40
                trend = "poor"
            else:
                score = 20
                trend = "concerning"
            
            # Detect trend
            trend_direction = self._detect_trend(transactions, "savings_rate")
            
            insight = f"Your savings rate is {savings_rate:.1%}"
            recommendation = (
                "Increase income or reduce expenses to improve savings rate"
                if savings_rate < 0.3
                else "Maintain your current savings rate"
            )
            
            return HealthScoreComponent(
                name="Savings Rate",
                score=score,
                weight=self.COMPONENT_WEIGHTS["savings_rate"],
                trend=trend_direction,
                insight=insight,
                recommendation=recommendation,
            )
        except Exception as e:
            logger.error(f"Error calculating savings rate: {e}")
            return HealthScoreComponent(
                name="Savings Rate",
                score=50,
                weight=self.COMPONENT_WEIGHTS["savings_rate"],
                trend="error",
                insight="Error calculating savings rate",
                recommendation="Add more transaction data",
            )
    
    def _calculate_cash_flow_stability_score(
        self,
        transactions: List[Dict],
        monthly_income: Optional[float],
    ) -> HealthScoreComponent:
        """Calculate cash flow stability component score."""
        try:
            if not transactions:
                return HealthScoreComponent(
                    name="Cash Flow Stability",
                    score=50,
                    weight=self.COMPONENT_WEIGHTS["cash_flow_stability"],
                    trend="unknown",
                    insight="Insufficient data",
                    recommendation="Add more transactions for better analysis",
                )
            
            # Calculate monthly expenses variance
            monthly_expenses = self._get_monthly_expenses_list(transactions)
            
            if len(monthly_expenses) < 2:
                score = 60
                trend = "unknown"
                insight = "Insufficient months of data"
            else:
                import statistics
                avg_expense = statistics.mean(monthly_expenses)
                std_dev = statistics.stdev(monthly_expenses)
                cv = std_dev / avg_expense if avg_expense > 0 else 0
                
                # Score based on coefficient of variation
                # CV < 0.2 = excellent (100), 0.2-0.4 = good (75), 0.4-0.6 = fair (50), 0.6+ = poor (25)
                if cv < 0.2:
                    score = 100
                    trend = "stable"
                elif cv < 0.4:
                    score = 75
                    trend = "relatively_stable"
                elif cv < 0.6:
                    score = 50
                    trend = "variable"
                else:
                    score = 25
                    trend = "highly_variable"
                
                insight = f"Expense volatility: {cv:.1%}"
            
            recommendation = (
                "Try to stabilize your monthly spending"
                if trend in ["variable", "highly_variable"]
                else "Your spending is well-structured"
            )
            
            return HealthScoreComponent(
                name="Cash Flow Stability",
                score=score,
                weight=self.COMPONENT_WEIGHTS["cash_flow_stability"],
                trend=trend,
                insight=insight,
                recommendation=recommendation,
            )
        except Exception as e:
            logger.error(f"Error calculating cash flow stability: {e}")
            return HealthScoreComponent(
                name="Cash Flow Stability",
                score=50,
                weight=self.COMPONENT_WEIGHTS["cash_flow_stability"],
                trend="error",
                insight="Error calculating stability",
                recommendation="Add more transaction data",
            )
    
    def _calculate_expense_trends_score(
        self,
        transactions: List[Dict],
    ) -> HealthScoreComponent:
        """Calculate expense trends component score."""
        try:
            if not transactions:
                return HealthScoreComponent(
                    name="Expense Trends",
                    score=50,
                    weight=self.COMPONENT_WEIGHTS["expense_trends"],
                    trend="unknown",
                    insight="Insufficient data",
                    recommendation="Add more transactions",
                )
            
            # Get monthly expenses
            monthly_expenses = self._get_monthly_expenses_list(transactions)
            
            if len(monthly_expenses) < 2:
                score = 60
                trend = "unknown"
                insight = "Insufficient data for trend analysis"
            else:
                # Calculate trend: recent vs older
                recent_avg = sum(monthly_expenses[-3:]) / min(3, len(monthly_expenses[-3:]))
                older_avg = sum(monthly_expenses[:-3]) / max(1, len(monthly_expenses[:-3]))
                
                if older_avg == 0:
                    trend_pct = 0
                else:
                    trend_pct = (recent_avg - older_avg) / older_avg
                
                # Score based on trend
                if trend_pct < -0.1:  # 10%+ decrease
                    score = 90
                    trend = "improving"
                    insight = f"Expenses down {-trend_pct:.1%} recently"
                elif trend_pct < 0:  # Any decrease
                    score = 75
                    trend = "improving"
                    insight = f"Expenses down {-trend_pct:.1%} recently"
                elif trend_pct < 0.05:  # Stable
                    score = 70
                    trend = "stable"
                    insight = "Expenses relatively stable"
                elif trend_pct < 0.15:  # Up to 15% increase
                    score = 50
                    trend = "increasing"
                    insight = f"Expenses up {trend_pct:.1%} recently"
                else:  # 15%+ increase
                    score = 30
                    trend = "rapidly_increasing"
                    insight = f"Expenses up {trend_pct:.1%} recently - concerning trend"
            
            recommendation = (
                "Try to reduce or stabilize your monthly expenses"
                if trend in ["increasing", "rapidly_increasing"]
                else "Your expense trend looks good"
            )
            
            return HealthScoreComponent(
                name="Expense Trends",
                score=score,
                weight=self.COMPONENT_WEIGHTS["expense_trends"],
                trend=trend,
                insight=insight,
                recommendation=recommendation,
            )
        except Exception as e:
            logger.error(f"Error calculating expense trends: {e}")
            return HealthScoreComponent(
                name="Expense Trends",
                score=50,
                weight=self.COMPONENT_WEIGHTS["expense_trends"],
                trend="error",
                insight="Error calculating trends",
                recommendation="Add more transaction data",
            )
    
    def _calculate_runway_health_score(
        self,
        account_balance: Decimal,
        monthly_expenses: Optional[float],
    ) -> HealthScoreComponent:
        """Calculate runway health component score."""
        try:
            if not monthly_expenses or monthly_expenses <= 0:
                return HealthScoreComponent(
                    name="Runway Health",
                    score=50,
                    weight=self.COMPONENT_WEIGHTS["runway_health"],
                    trend="unknown",
                    insight="No expense data",
                    recommendation="Add expenses to calculate runway",
                )
            
            balance_float = float(account_balance)
            months_of_runway = balance_float / monthly_expenses if monthly_expenses > 0 else float('inf')
            
            # Score based on months of runway
            # 12+ months = 100, 6-12 = 80, 3-6 = 60, 1-3 = 40, <1 = 20
            if months_of_runway >= 12:
                score = 100
                trend = "excellent"
            elif months_of_runway >= 6:
                score = 80
                trend = "good"
            elif months_of_runway >= 3:
                score = 60
                trend = "fair"
            elif months_of_runway >= 1:
                score = 40
                trend = "concerning"
            else:
                score = 20
                trend = "critical"
            
            insight = f"Runway: {months_of_runway:.1f} months"
            recommendation = (
                "Build your emergency fund to 3-6 months of expenses"
                if months_of_runway < 3
                else "Maintain your current emergency fund"
            )
            
            return HealthScoreComponent(
                name="Runway Health",
                score=score,
                weight=self.COMPONENT_WEIGHTS["runway_health"],
                trend=trend,
                insight=insight,
                recommendation=recommendation,
            )
        except Exception as e:
            logger.error(f"Error calculating runway health: {e}")
            return HealthScoreComponent(
                name="Runway Health",
                score=50,
                weight=self.COMPONENT_WEIGHTS["runway_health"],
                trend="error",
                insight="Error calculating runway",
                recommendation="Check your account balance and expenses",
            )
    
    def _calculate_subscription_efficiency_score(
        self,
        subscriptions: Optional[List[Dict]],
        monthly_expenses: Optional[float],
    ) -> HealthScoreComponent:
        """Calculate subscription efficiency component score."""
        try:
            if not subscriptions:
                return HealthScoreComponent(
                    name="Subscription Efficiency",
                    score=75,
                    weight=self.COMPONENT_WEIGHTS["subscription_efficiency"],
                    trend="unknown",
                    insight="No subscriptions tracked",
                    recommendation="Add your subscriptions for better analysis",
                )
            
            total_subscription_cost = sum(
                float(sub.get("amount", 0)) for sub in subscriptions
                if sub.get("is_active", True)
            )
            
            if not monthly_expenses or monthly_expenses <= 0:
                score = 60
                insight = "Cannot calculate subscription percentage"
            else:
                subscription_percentage = total_subscription_cost / monthly_expenses
                
                # Score based on subscription percentage
                # <5% = 90, 5-10% = 70, 10-15% = 50, 15-20% = 30, 20%+ = 10
                if subscription_percentage < 0.05:
                    score = 90
                    trend = "efficient"
                elif subscription_percentage < 0.10:
                    score = 70
                    trend = "reasonable"
                elif subscription_percentage < 0.15:
                    score = 50
                    trend = "moderate"
                elif subscription_percentage < 0.20:
                    score = 30
                    trend = "high"
                else:
                    score = 10
                    trend = "excessive"
                
                insight = f"Subscriptions: {subscription_percentage:.1%} of expenses"
            
            recommendation = (
                "Review and cancel unused subscriptions" 
                if score < 50
                else "Your subscriptions are well-managed"
            )
            
            return HealthScoreComponent(
                name="Subscription Efficiency",
                score=score,
                weight=self.COMPONENT_WEIGHTS["subscription_efficiency"],
                trend=trend,
                insight=insight,
                recommendation=recommendation,
            )
        except Exception as e:
            logger.error(f"Error calculating subscription efficiency: {e}")
            return HealthScoreComponent(
                name="Subscription Efficiency",
                score=50,
                weight=self.COMPONENT_WEIGHTS["subscription_efficiency"],
                trend="error",
                insight="Error calculating subscription efficiency",
                recommendation="Check your subscriptions data",
            )
    
    def _calculate_emergency_fund_score(
        self,
        account_balance: Decimal,
        monthly_expenses: Optional[float],
        emergency_fund_target: Optional[float] = None,
    ) -> HealthScoreComponent:
        """Calculate emergency fund adequacy component score."""
        try:
            if not monthly_expenses or monthly_expenses <= 0:
                return HealthScoreComponent(
                    name="Emergency Fund",
                    score=50,
                    weight=self.COMPONENT_WEIGHTS["emergency_fund"],
                    trend="unknown",
                    insight="No expense data",
                    recommendation="Add expense data to calculate emergency fund adequacy",
                )
            
            balance_float = float(account_balance)
            target = emergency_fund_target or (monthly_expenses * 6)  # Default 6 months
            
            coverage_ratio = balance_float / target if target > 0 else 0
            
            # Score based on coverage ratio
            # 1.0+ = 100, 0.75-1.0 = 75, 0.5-0.75 = 50, 0.25-0.5 = 30, <0.25 = 10
            if coverage_ratio >= 1.0:
                score = 100
                trend = "excellent"
            elif coverage_ratio >= 0.75:
                score = 75
                trend = "good"
            elif coverage_ratio >= 0.5:
                score = 50
                trend = "fair"
            elif coverage_ratio >= 0.25:
                score = 30
                trend = "low"
            else:
                score = 10
                trend = "critical"
            
            insight = f"Emergency fund covers {coverage_ratio:.0%} of target ({target/monthly_expenses:.0f} months)"
            recommendation = (
                f"Build your emergency fund to {target:,.0f} ({target/monthly_expenses:.0f} months of expenses)"
                if coverage_ratio < 1.0
                else "Your emergency fund is well-funded"
            )
            
            return HealthScoreComponent(
                name="Emergency Fund",
                score=score,
                weight=self.COMPONENT_WEIGHTS["emergency_fund"],
                trend=trend,
                insight=insight,
                recommendation=recommendation,
            )
        except Exception as e:
            logger.error(f"Error calculating emergency fund: {e}")
            return HealthScoreComponent(
                name="Emergency Fund",
                score=50,
                weight=self.COMPONENT_WEIGHTS["emergency_fund"],
                trend="error",
                insight="Error calculating emergency fund",
                recommendation="Check your account balance",
            )
    
    def _calculate_monthly_expenses(self, transactions: List[Dict]) -> float:
        """Calculate average monthly expenses."""
        try:
            monthly_totals = {}
            for txn in transactions:
                if txn.get("type") == "expense":
                    date = txn.get("date")
                    if isinstance(date, str):
                        month = date[:7]  # YYYY-MM
                    else:
                        month = date.strftime("%Y-%m")
                    
                    monthly_totals[month] = monthly_totals.get(month, 0) + float(txn.get("amount", 0))
            
            if not monthly_totals:
                return 0
            
            return sum(monthly_totals.values()) / len(monthly_totals)
        except Exception as e:
            logger.error(f"Error calculating monthly expenses: {e}")
            return 0
    
    def _get_monthly_expenses_list(self, transactions: List[Dict]) -> List[float]:
        """Get list of monthly expense totals."""
        try:
            monthly_totals = {}
            for txn in transactions:
                if txn.get("type") == "expense":
                    date = txn.get("date")
                    if isinstance(date, str):
                        month = date[:7]  # YYYY-MM
                    else:
                        month = date.strftime("%Y-%m")
                    
                    monthly_totals[month] = monthly_totals.get(month, 0) + float(txn.get("amount", 0))
            
            return sorted(monthly_totals.values()) if monthly_totals else []
        except Exception as e:
            logger.error(f"Error getting monthly expenses list: {e}")
            return []
    
    def _detect_trend(self, transactions: List[Dict], metric: str) -> str:
        """Detect trend for a metric."""
        try:
            # Simplified trend detection
            # In a real scenario, would do more sophisticated time series analysis
            return "stable"
        except Exception as e:
            logger.error(f"Error detecting trend: {e}")
            return "unknown"
    
    def _assess_risk_level(self, score: float) -> str:
        """Assess risk level based on score."""
        if score >= 80:
            return "low"
        elif score >= 60:
            return "medium"
        elif score >= 40:
            return "high"
        else:
            return "critical"
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        elif score >= 55:
            return "C-"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def _calculate_confidence(self, transactions: List[Dict], monthly_income: Optional[float]) -> float:
        """Calculate confidence score based on data quality."""
        try:
            confidence = 0.5  # Base confidence
            
            # More transactions = higher confidence
            if len(transactions) >= 100:
                confidence += 0.3
            elif len(transactions) >= 50:
                confidence += 0.2
            elif len(transactions) >= 20:
                confidence += 0.1
            
            # Income data increases confidence
            if monthly_income:
                confidence += 0.2
            
            return min(1.0, confidence)
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _generate_insights(
        self,
        components: List[HealthScoreComponent],
        overall_score: float,
    ) -> List[str]:
        """Generate insights based on components."""
        insights = []
        
        try:
            # Add insights based on components
            for component in components:
                if component.score < 40:
                    insights.append(f"⚠️ {component.name} needs attention: {component.insight}")
                elif component.score >= 80:
                    insights.append(f"✅ {component.name} is strong: {component.insight}")
            
            # Overall health insight
            if overall_score >= 80:
                insights.append("Your financial health is excellent. Keep up the good work!")
            elif overall_score >= 60:
                insights.append("Your financial health is fair. Look for areas to improve.")
            elif overall_score >= 40:
                insights.append("Your financial health needs attention. Review recommendations.")
            else:
                insights.append("Your financial health is at risk. Take action immediately.")
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
        
        return insights[:5]  # Return top 5 insights
    
    def _generate_recommendations(
        self,
        components: List[HealthScoreComponent],
        overall_score: float,
    ) -> List[str]:
        """Generate recommendations based on components."""
        recommendations = []
        
        try:
            # Collect all recommendations from components
            for component in components:
                if component.score < 60:
                    recommendations.append(component.recommendation)
            
            # Sort by priority
            recommendations = sorted(set(recommendations))[:5]
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
        
        return recommendations
