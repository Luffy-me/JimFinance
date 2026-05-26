"""Report Generation Service

Generates comprehensive financial reports with:
- Executive summary
- Key metrics and trends
- Charts and visualizations
- AI analysis and insights
- Recommendations with confidence scores
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


@dataclass
class ReportChartData:
    """Chart data for visualization"""
    chart_type: str  # "line", "bar", "pie"
    title: str
    data: Dict[str, Any]
    description: str


@dataclass
class FinancialReport:
    """Comprehensive financial report"""
    report_id: str
    user_id: str
    report_period: str  # "weekly", "monthly"
    period_start: datetime
    period_end: datetime
    
    # Summary
    summary: Dict[str, Any]
    
    # Metrics
    key_metrics: Dict[str, Any]
    
    # Analysis
    spending_analysis: Dict[str, Any]
    income_analysis: Optional[Dict[str, Any]]
    trend_analysis: Dict[str, Any]
    health_analysis: Dict[str, Any]
    
    # Recommendations
    recommendations: List[Dict[str, Any]]
    
    # Alerts
    alerts: List[Dict[str, Any]]
    
    # Charts for PDF/UI
    charts: List[ReportChartData]
    
    # Metadata
    confidence: float  # Overall confidence in the report
    generated_at: datetime


class ReportGenerator:
    """Generates comprehensive financial reports"""
    
    def __init__(self):
        """Initialize report generator."""
        from app.ml.financial_scoring import FinancialHealthScoringEngine
        from app.ml.alerts import AlertDetectionEngine
        
        self.health_scoring = FinancialHealthScoringEngine()
        self.alert_detection = AlertDetectionEngine()
    
    def generate_weekly_report(
        self,
        user_id: str,
        transactions: List[Dict],
        account_balance: Decimal,
        monthly_income: Optional[float] = None,
        subscriptions: Optional[List[Dict]] = None,
        behavioral_profile: Optional[Dict] = None,
    ) -> FinancialReport:
        """
        Generate a comprehensive weekly financial report.
        
        Args:
            user_id: User identifier
            transactions: Historical transactions
            account_balance: Current account balance
            monthly_income: Average monthly income
            subscriptions: List of subscriptions
            behavioral_profile: User behavioral profile
        
        Returns:
            Comprehensive FinancialReport
        """
        try:
            import uuid
            
            # Period definition
            today = datetime.now()
            period_end = today
            period_start = today - timedelta(days=7)
            
            # Get weekly transactions
            weekly_txns = [
                t for t in transactions
                if self._is_in_period(t, period_start, period_end)
            ]
            
            # Calculate metrics
            monthly_expenses = self._calculate_monthly_expenses(transactions)
            
            # 1. Generate health score
            health_score = self.health_scoring.calculate_health_score(
                transactions=transactions,
                account_balance=account_balance,
                monthly_income=monthly_income,
                monthly_expenses=monthly_expenses,
                subscriptions=subscriptions,
            )
            
            # 2. Detect alerts
            alerts = self.alert_detection.detect_all_alerts(
                user_id=user_id,
                transactions=transactions,
                account_balance=account_balance,
                monthly_income=monthly_income,
                monthly_expenses=monthly_expenses,
                subscriptions=subscriptions,
                behavioral_profile=behavioral_profile,
            )
            
            # 3. Analyze spending
            spending_analysis = self._analyze_spending(weekly_txns, transactions)
            
            # 4. Analyze income (if available)
            income_analysis = None
            if monthly_income:
                income_analysis = self._analyze_income(transactions, monthly_income)
            
            # 5. Analyze trends
            trend_analysis = self._analyze_trends(transactions)
            
            # 6. Health analysis
            health_analysis = {
                "score": health_score.overall_score,
                "grade": health_score.score_grade,
                "risk_level": health_score.risk_level,
                "insights": health_score.insights,
                "recommendations": health_score.recommendations,
            }
            
            # 7. Generate AI recommendations
            recommendations = self._generate_recommendations(
                health_score,
                alerts,
                spending_analysis,
                trend_analysis,
            )
            
            # 8. Create charts
            charts = self._create_charts(
                weekly_txns,
                transactions,
                spending_analysis,
                trend_analysis,
            )
            
            # 9. Create summary
            summary = {
                "period": f"{period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}",
                "generated_at": datetime.now().isoformat(),
                "user_message": self._create_summary_message(
                    health_score, spending_analysis, alerts
                ),
            }
            
            # 10. Calculate confidence
            confidence = self._calculate_report_confidence(
                len(transactions), len(weekly_txns)
            )
            
            return FinancialReport(
                report_id=str(uuid.uuid4()),
                user_id=user_id,
                report_period="weekly",
                period_start=period_start,
                period_end=period_end,
                summary=summary,
                key_metrics=self._extract_key_metrics(
                    health_score, spending_analysis, trend_analysis
                ),
                spending_analysis=spending_analysis,
                income_analysis=income_analysis,
                trend_analysis=trend_analysis,
                health_analysis=health_analysis,
                recommendations=recommendations,
                alerts=[asdict(a) if hasattr(a, '__dataclass_fields__') else a for a in alerts[:5]],
                charts=charts,
                confidence=confidence,
                generated_at=datetime.now(),
            )
        except Exception as e:
            logger.error(f"Error generating weekly report for user {user_id}: {e}")
            raise
    
    def _is_in_period(self, transaction: Dict, start: datetime, end: datetime) -> bool:
        """Check if transaction is within period."""
        try:
            txn_date = transaction.get("date")
            if isinstance(txn_date, str):
                txn_date = datetime.fromisoformat(txn_date)
            return start <= txn_date <= end
        except Exception:
            return False
    
    def _calculate_monthly_expenses(self, transactions: List[Dict]) -> float:
        """Calculate average monthly expenses."""
        try:
            monthly_totals = {}
            for txn in transactions:
                if txn.get("type") == "expense":
                    date = txn.get("date")
                    if isinstance(date, str):
                        month = date[:7]
                    else:
                        month = date.strftime("%Y-%m")
                    monthly_totals[month] = monthly_totals.get(month, 0) + float(txn.get("amount", 0))
            
            return sum(monthly_totals.values()) / len(monthly_totals) if monthly_totals else 0
        except Exception as e:
            logger.error(f"Error calculating monthly expenses: {e}")
            return 0
    
    def _analyze_spending(
        self,
        weekly_txns: List[Dict],
        all_txns: List[Dict],
    ) -> Dict[str, Any]:
        """Analyze spending patterns."""
        try:
            # Weekly totals
            weekly_total = sum(
                float(t.get("amount", 0)) for t in weekly_txns if t.get("type") == "expense"
            )
            
            # By category
            by_category = {}
            for txn in weekly_txns:
                if txn.get("type") == "expense":
                    category = txn.get("category", "other")
                    by_category[category] = by_category.get(category, 0) + float(txn.get("amount", 0))
            
            # Top merchants
            by_merchant = {}
            for txn in weekly_txns:
                if txn.get("type") == "expense":
                    merchant = txn.get("merchant", "unknown")
                    by_merchant[merchant] = by_merchant.get(merchant, 0) + float(txn.get("amount", 0))
            
            top_merchants = sorted(by_merchant.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Compare to previous week
            today = datetime.now()
            week_start = today - timedelta(days=7)
            prev_week_start = week_start - timedelta(days=7)
            
            prev_week_txns = [
                t for t in all_txns
                if self._is_in_period(t, prev_week_start, week_start)
            ]
            
            prev_week_total = sum(
                float(t.get("amount", 0)) for t in prev_week_txns if t.get("type") == "expense"
            )
            
            week_over_week_change = (
                (weekly_total - prev_week_total) / prev_week_total * 100
                if prev_week_total > 0
                else 0
            )
            
            return {
                "total_spending": weekly_total,
                "transaction_count": len(weekly_txns),
                "average_transaction": weekly_total / len(weekly_txns) if weekly_txns else 0,
                "by_category": by_category,
                "top_merchants": [{"name": m, "amount": a} for m, a in top_merchants],
                "week_over_week_change": week_over_week_change,
                "prev_week_total": prev_week_total,
            }
        except Exception as e:
            logger.error(f"Error analyzing spending: {e}")
            return {}
    
    def _analyze_income(
        self,
        transactions: List[Dict],
        monthly_income: float,
    ) -> Dict[str, Any]:
        """Analyze income patterns."""
        try:
            income_txns = [t for t in transactions if t.get("type") == "income"]
            
            total_income = sum(float(t.get("amount", 0)) for t in income_txns)
            
            return {
                "monthly_income": monthly_income,
                "total_tracked_income": total_income,
                "income_transactions": len(income_txns),
            }
        except Exception as e:
            logger.error(f"Error analyzing income: {e}")
            return None
    
    def _analyze_trends(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Analyze spending trends."""
        try:
            monthly_expenses = {}
            for txn in transactions:
                if txn.get("type") == "expense":
                    date = txn.get("date")
                    if isinstance(date, str):
                        month = date[:7]
                    else:
                        month = date.strftime("%Y-%m")
                    monthly_expenses[month] = monthly_expenses.get(month, 0) + float(txn.get("amount", 0))
            
            if len(monthly_expenses) < 2:
                return {"trend": "insufficient_data"}
            
            months = sorted(monthly_expenses.keys())
            values = [monthly_expenses[m] for m in months]
            
            # Calculate trend
            import statistics
            avg = statistics.mean(values)
            recent_avg = statistics.mean(values[-3:]) if len(values) >= 3 else values[-1]
            
            trend_pct = (recent_avg - avg) / avg * 100 if avg > 0 else 0
            
            if trend_pct < -10:
                trend = "improving"
            elif trend_pct < 0:
                trend = "stable"
            elif trend_pct < 10:
                trend = "slightly_increasing"
            else:
                trend = "increasing"
            
            return {
                "trend": trend,
                "trend_percentage": trend_pct,
                "monthly_data": dict(zip(months[-6:], values[-6:])),  # Last 6 months
            }
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return {}
    
    def _generate_recommendations(
        self,
        health_score,
        alerts,
        spending_analysis,
        trend_analysis,
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered recommendations."""
        try:
            recommendations = []
            
            # From health components
            for component in health_score.components:
                if component.score < 60:
                    recommendations.append({
                        "category": component.name,
                        "priority": "high" if component.score < 40 else "medium",
                        "recommendation": component.recommendation,
                        "confidence": 0.9,
                        "impact": "medium",
                    })
            
            # From trend analysis
            if trend_analysis.get("trend") == "increasing":
                recommendations.append({
                    "category": "Spending Trends",
                    "priority": "medium",
                    "recommendation": "Your spending is increasing. Consider implementing a budget to control expenses.",
                    "confidence": 0.85,
                    "impact": "high",
                })
            
            # Sort by priority
            priority_map = {"high": 0, "medium": 1, "low": 2}
            recommendations.sort(key=lambda r: priority_map.get(r["priority"], 3))
            
            return recommendations[:5]  # Top 5 recommendations
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _create_charts(
        self,
        weekly_txns,
        all_txns,
        spending_analysis,
        trend_analysis,
    ) -> List[ReportChartData]:
        """Create chart data for visualizations."""
        try:
            charts = []
            
            # 1. Spending by category (pie chart)
            if spending_analysis.get("by_category"):
                charts.append(ReportChartData(
                    chart_type="pie",
                    title="Weekly Spending by Category",
                    data=spending_analysis.get("by_category", {}),
                    description="Breakdown of spending across categories",
                ))
            
            # 2. Monthly trend (line chart)
            if trend_analysis.get("monthly_data"):
                charts.append(ReportChartData(
                    chart_type="line",
                    title="Monthly Spending Trend",
                    data=trend_analysis.get("monthly_data", {}),
                    description="Your spending trend over the last 6 months",
                ))
            
            # 3. Top merchants (bar chart)
            if spending_analysis.get("top_merchants"):
                merchant_data = {
                    m["name"]: m["amount"]
                    for m in spending_analysis.get("top_merchants", [])
                }
                charts.append(ReportChartData(
                    chart_type="bar",
                    title="Top 5 Merchants",
                    data=merchant_data,
                    description="Your top spending merchants this week",
                ))
            
            return charts
        except Exception as e:
            logger.error(f"Error creating charts: {e}")
            return []
    
    def _extract_key_metrics(
        self,
        health_score,
        spending_analysis,
        trend_analysis,
    ) -> Dict[str, Any]:
        """Extract key metrics for the report."""
        return {
            "health_score": health_score.overall_score,
            "health_grade": health_score.score_grade,
            "weekly_spending": spending_analysis.get("total_spending", 0),
            "spending_trend": trend_analysis.get("trend", "unknown"),
            "spending_change": trend_analysis.get("trend_percentage", 0),
        }
    
    def _create_summary_message(
        self,
        health_score,
        spending_analysis,
        alerts,
    ) -> str:
        """Create an AI-generated summary message."""
        try:
            parts = []
            
            # Health score intro
            if health_score.overall_score >= 80:
                parts.append("📊 Your financial health is excellent this week!")
            elif health_score.overall_score >= 60:
                parts.append("📊 Your financial health is good this week, with some areas to improve.")
            else:
                parts.append("⚠️ Your financial health needs attention this week.")
            
            # Spending summary
            spending = spending_analysis.get("total_spending", 0)
            parts.append(f"💰 Weekly spending: ${spending:.2f}")
            
            # Trend
            trend = spending_analysis.get("week_over_week_change", 0)
            if trend > 10:
                parts.append(f"📈 Spending up {trend:.0f}% compared to last week")
            elif trend < -10:
                parts.append(f"📉 Spending down {trend:.0f}% compared to last week")
            
            # Alerts
            if alerts:
                parts.append(f"🔔 {len(alerts)} alert{'s' if len(alerts) > 1 else ''} detected")
            
            # Recommendations
            parts.append("✨ Check recommendations for ways to improve")
            
            return " • ".join(parts)
        except Exception as e:
            logger.error(f"Error creating summary message: {e}")
            return "Weekly financial report ready for review"
    
    def _calculate_report_confidence(self, total_txns: int, weekly_txns: int) -> float:
        """Calculate confidence in the report."""
        try:
            confidence = 0.5
            
            # More historical data = higher confidence
            if total_txns >= 100:
                confidence += 0.3
            elif total_txns >= 50:
                confidence += 0.2
            elif total_txns >= 20:
                confidence += 0.1
            
            # More weekly transactions = higher confidence
            if weekly_txns >= 20:
                confidence += 0.15
            elif weekly_txns >= 10:
                confidence += 0.1
            
            return min(1.0, confidence)
        except Exception:
            return 0.5
