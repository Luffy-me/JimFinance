"""Alert Detection Engine

Detects and generates financial alerts:
- Spending anomalies and trends
- Burn rate warnings
- Subscription waste
- Savings opportunities
- Behavioral anomalies
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Alert types"""
    SPENDING_SPIKE = "spending_spike"
    SPENDING_TREND = "spending_trend"
    BURN_RATE_WARNING = "burn_rate_warning"
    SUBSCRIPTION_WASTE = "subscription_waste"
    SAVINGS_OPPORTUNITY = "savings_opportunity"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    LOW_RUNWAY = "low_runway"
    HIGH_VOLATILITY = "high_volatility"


@dataclass
class Alert:
    """Financial alert"""
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    data: Dict  # Additional context
    confidence: float  # 0-1
    recommendation: str
    created_at: datetime


class AlertDetectionEngine:
    """Detects and generates financial alerts"""
    
    def __init__(self):
        """Initialize alert detection engine."""
        pass
    
    def detect_all_alerts(
        self,
        user_id: str,
        transactions: List[Dict],
        account_balance: Decimal,
        monthly_income: Optional[float] = None,
        monthly_expenses: Optional[float] = None,
        subscriptions: Optional[List[Dict]] = None,
        behavioral_profile: Optional[Dict] = None,
    ) -> List[Alert]:
        """
        Detect all types of alerts for a user.
        
        Args:
            user_id: User identifier
            transactions: Historical transactions
            account_balance: Current account balance
            monthly_income: Average monthly income
            monthly_expenses: Average monthly expenses
            subscriptions: List of subscriptions
            behavioral_profile: User behavioral profile
        
        Returns:
            List of detected alerts
        """
        alerts = []
        
        try:
            # Detect spending anomalies
            alerts.extend(self.detect_spending_anomalies(transactions))
            
            # Detect burn rate issues
            alerts.extend(self.detect_burn_rate_issues(
                transactions, account_balance, monthly_income, monthly_expenses
            ))
            
            # Detect subscription waste
            alerts.extend(self.detect_subscription_waste(subscriptions, monthly_expenses))
            
            # Detect behavioral anomalies
            if behavioral_profile:
                alerts.extend(self.detect_behavioral_anomalies(
                    transactions, behavioral_profile
                ))
            
            # Detect savings opportunities
            alerts.extend(self.detect_savings_opportunities(
                transactions, subscriptions, monthly_expenses
            ))
            
            # Sort by severity
            alerts.sort(key=lambda a: self._severity_rank(a.severity), reverse=True)
            
            # Limit to 10 most important alerts
            return alerts[:10]
        except Exception as e:
            logger.error(f"Error detecting alerts for user {user_id}: {e}")
            return []
    
    def detect_spending_anomalies(self, transactions: List[Dict]) -> List[Alert]:
        """Detect spending anomalies and spikes."""
        alerts = []
        
        try:
            if len(transactions) < 10:
                return alerts
            
            # Calculate spending by category for last month vs previous month
            today = datetime.now()
            last_month_start = today.replace(day=1) - timedelta(days=1)
            last_month_start = last_month_start.replace(day=1)
            prev_month_start = last_month_start - timedelta(days=1)
            prev_month_start = prev_month_start.replace(day=1)
            
            categories_current = {}
            categories_previous = {}
            
            for txn in transactions:
                if txn.get("type") != "expense":
                    continue
                
                try:
                    txn_date = txn.get("date")
                    if isinstance(txn_date, str):
                        txn_date = datetime.fromisoformat(txn_date)
                    
                    category = txn.get("category", "other")
                    amount = float(txn.get("amount", 0))
                    
                    if txn_date >= last_month_start:
                        categories_current[category] = categories_current.get(category, 0) + amount
                    elif txn_date >= prev_month_start:
                        categories_previous[category] = categories_previous.get(category, 0) + amount
                except Exception:
                    continue
            
            # Detect spikes
            for category, current_amount in categories_current.items():
                prev_amount = categories_previous.get(category, current_amount)
                
                if prev_amount > 0:
                    increase_pct = (current_amount - prev_amount) / prev_amount
                    
                    if increase_pct >= 0.4:  # 40%+ increase
                        alerts.append(Alert(
                            alert_type=AlertType.SPENDING_SPIKE,
                            severity=AlertSeverity.WARNING,
                            title=f"{category.title()} Spending Spike",
                            message=f"Your {category} spending increased {increase_pct:.0%} this month (${current_amount:.2f} vs ${prev_amount:.2f} last month).",
                            data={
                                "category": category,
                                "current_amount": current_amount,
                                "previous_amount": prev_amount,
                                "increase_pct": increase_pct,
                            },
                            confidence=0.8,
                            recommendation=f"Review your {category} expenses. Look for one-time purchases or subscription increases.",
                            created_at=datetime.now(),
                        ))
        except Exception as e:
            logger.error(f"Error detecting spending anomalies: {e}")
        
        return alerts
    
    def detect_burn_rate_issues(
        self,
        transactions: List[Dict],
        account_balance: Decimal,
        monthly_income: Optional[float],
        monthly_expenses: Optional[float],
    ) -> List[Alert]:
        """Detect burn rate and runway issues."""
        alerts = []
        
        try:
            if not monthly_expenses or monthly_expenses <= 0:
                return alerts
            
            balance_float = float(account_balance)
            months_runway = balance_float / monthly_expenses
            
            # Low runway warning
            if months_runway < 3:
                alerts.append(Alert(
                    alert_type=AlertType.LOW_RUNWAY,
                    severity=AlertSeverity.CRITICAL if months_runway < 1 else AlertSeverity.WARNING,
                    title="Low Runway Warning",
                    message=f"Your current burn rate reduces your runway to {months_runway:.1f} months.",
                    data={
                        "runway_months": months_runway,
                        "monthly_expense": monthly_expenses,
                        "account_balance": float(account_balance),
                    },
                    confidence=0.9,
                    recommendation="Increase income or reduce expenses to extend your runway.",
                    created_at=datetime.now(),
                ))
            
            # Burn rate trend
            if monthly_income and monthly_income > 0:
                burn_ratio = monthly_expenses / monthly_income
                if burn_ratio > 0.9:  # Spending 90%+ of income
                    alerts.append(Alert(
                        alert_type=AlertType.BURN_RATE_WARNING,
                        severity=AlertSeverity.WARNING,
                        title="High Burn Rate",
                        message=f"You're spending {burn_ratio:.0%} of your monthly income. Only {1-burn_ratio:.0%} is left for savings.",
                        data={
                            "monthly_income": monthly_income,
                            "monthly_expenses": monthly_expenses,
                            "burn_ratio": burn_ratio,
                        },
                        confidence=0.95,
                        recommendation="Reduce monthly expenses or seek additional income sources.",
                        created_at=datetime.now(),
                    ))
        except Exception as e:
            logger.error(f"Error detecting burn rate issues: {e}")
        
        return alerts
    
    def detect_subscription_waste(
        self,
        subscriptions: Optional[List[Dict]],
        monthly_expenses: Optional[float],
    ) -> List[Alert]:
        """Detect subscription waste and unused subscriptions."""
        alerts = []
        
        try:
            if not subscriptions:
                return alerts
            
            unused_subscriptions = [
                sub for sub in subscriptions
                if not sub.get("is_active", True) and sub.get("last_used")
            ]
            
            # Check for subscriptions not used in 30+ days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            potentially_unused = []
            
            for sub in subscriptions:
                if sub.get("is_active", True):
                    last_used = sub.get("last_used")
                    if last_used:
                        if isinstance(last_used, str):
                            last_used = datetime.fromisoformat(last_used)
                        
                        if last_used < thirty_days_ago:
                            potentially_unused.append(sub)
            
            # Generate alert if 20%+ of subscriptions are unused
            total_sub_cost = sum(
                float(sub.get("amount", 0)) for sub in subscriptions
                if sub.get("is_active", True)
            )
            unused_cost = sum(
                float(sub.get("amount", 0)) for sub in potentially_unused
            )
            
            if monthly_expenses and total_sub_cost > 0:
                sub_percentage = total_sub_cost / monthly_expenses
                if sub_percentage > 0.15:  # Subscriptions are 15%+ of expenses
                    alerts.append(Alert(
                        alert_type=AlertType.SUBSCRIPTION_WASTE,
                        severity=AlertSeverity.WARNING,
                        title="High Subscription Cost",
                        message=f"You have {len(subscriptions)} subscriptions costing ${total_sub_cost:.2f}/month ({sub_percentage:.1%} of expenses). {len(potentially_unused)} may be unused.",
                        data={
                            "total_subscriptions": len(subscriptions),
                            "active_subscriptions": len([s for s in subscriptions if s.get("is_active", True)]),
                            "potentially_unused": len(potentially_unused),
                            "total_cost": total_sub_cost,
                            "unused_cost": unused_cost,
                        },
                        confidence=0.7,
                        recommendation="Review and cancel unused subscriptions. Check last used dates.",
                        created_at=datetime.now(),
                    ))
            
            # Alert for specific potentially unused subscriptions
            for sub in potentially_unused[:3]:  # Top 3 unused
                alerts.append(Alert(
                    alert_type=AlertType.SUBSCRIPTION_WASTE,
                    severity=AlertSeverity.INFO,
                    title=f"Unused Subscription: {sub.get('name', 'Unknown')}",
                    message=f"Your {sub.get('name')} subscription (${sub.get('amount', 0):.2f}/month) hasn't been used in {self._days_ago(sub.get('last_used')):.0f} days.",
                    data={
                        "subscription": sub.get("name"),
                        "cost": sub.get("amount"),
                        "last_used": sub.get("last_used"),
                    },
                    confidence=0.6,
                    recommendation="Consider canceling this subscription if you no longer need it.",
                    created_at=datetime.now(),
                ))
        except Exception as e:
            logger.error(f"Error detecting subscription waste: {e}")
        
        return alerts
    
    def detect_behavioral_anomalies(
        self,
        transactions: List[Dict],
        behavioral_profile: Dict,
    ) -> List[Alert]:
        """Detect behavioral anomalies in spending patterns."""
        alerts = []
        
        try:
            # Get current week spending
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())
            
            current_week_spending = 0
            current_week_by_category = {}
            
            for txn in transactions:
                if txn.get("type") != "expense":
                    continue
                
                try:
                    txn_date = txn.get("date")
                    if isinstance(txn_date, str):
                        txn_date = datetime.fromisoformat(txn_date)
                    
                    if txn_date >= week_start:
                        amount = float(txn.get("amount", 0))
                        current_week_spending += amount
                        category = txn.get("category", "other")
                        current_week_by_category[category] = current_week_by_category.get(category, 0) + amount
                except Exception:
                    continue
            
            # Compare to behavioral profile
            avg_weekly_spending = behavioral_profile.get("avg_weekly_spending", 0)
            spending_volatility = behavioral_profile.get("spending_volatility", 0)
            
            if avg_weekly_spending > 0 and current_week_spending > avg_weekly_spending * 1.5:
                z_score = (current_week_spending - avg_weekly_spending) / max(spending_volatility, 1)
                
                if z_score > 2:  # 2+ standard deviations
                    alerts.append(Alert(
                        alert_type=AlertType.BEHAVIORAL_ANOMALY,
                        severity=AlertSeverity.WARNING,
                        title="Unusual Spending Pattern",
                        message=f"Your spending this week (${current_week_spending:.2f}) is {(current_week_spending/avg_weekly_spending - 1):.0%} above your average (${avg_weekly_spending:.2f}).",
                        data={
                            "current_week": current_week_spending,
                            "average_weekly": avg_weekly_spending,
                            "z_score": z_score,
                            "by_category": current_week_by_category,
                        },
                        confidence=0.85,
                        recommendation="Review your recent transactions to understand the increased spending.",
                        created_at=datetime.now(),
                    ))
        except Exception as e:
            logger.error(f"Error detecting behavioral anomalies: {e}")
        
        return alerts
    
    def detect_savings_opportunities(
        self,
        transactions: List[Dict],
        subscriptions: Optional[List[Dict]],
        monthly_expenses: Optional[float],
    ) -> List[Alert]:
        """Detect savings opportunities."""
        alerts = []
        
        try:
            opportunities = []
            
            # 1. Check for duplicate merchant spending
            merchant_spending = {}
            for txn in transactions:
                if txn.get("type") == "expense":
                    merchant = txn.get("merchant", "Unknown")
                    amount = float(txn.get("amount", 0))
                    merchant_spending[merchant] = merchant_spending.get(merchant, 0) + amount
            
            # Find high-frequency merchants where consolidation could help
            for merchant, total in merchant_spending.items():
                if total > 100:  # Only significant merchants
                    count = len([t for t in transactions if t.get("merchant") == merchant])
                    if count >= 10:  # Multiple purchases
                        opportunities.append((f"Consolidate {merchant} purchases", f"Consider buying in bulk or negotiating rates"))
            
            # 2. Identify spending on non-essentials
            discretionary_categories = ["entertainment", "shopping", "dining"]
            discretionary_spending = 0
            
            for txn in transactions[-30:]:  # Last 30 transactions
                if txn.get("type") == "expense" and txn.get("category") in discretionary_categories:
                    discretionary_spending += float(txn.get("amount", 0))
            
            if discretionary_spending > 100:
                opportunities.append(
                    ("Reduce discretionary spending", f"You spent ${discretionary_spending:.2f} on non-essentials recently")
                )
            
            # 3. Check subscription renewal dates for negotiation
            if subscriptions:
                annual_subs = [s for s in subscriptions if s.get("billing_cycle") == "annual"]
                if annual_subs:
                    opportunities.append(
                        ("Negotiate annual subscriptions", f"You have {len(annual_subs)} annual subscriptions - contact providers for discounts")
                    )
            
            # Generate alerts for top opportunities
            for i, (opportunity, description) in enumerate(opportunities[:3]):
                alerts.append(Alert(
                    alert_type=AlertType.SAVINGS_OPPORTUNITY,
                    severity=AlertSeverity.INFO,
                    title=f"Savings Opportunity: {opportunity}",
                    message=description,
                    data={"opportunity": opportunity},
                    confidence=0.6,
                    recommendation=f"Take action on this opportunity to improve your financial health.",
                    created_at=datetime.now(),
                ))
        except Exception as e:
            logger.error(f"Error detecting savings opportunities: {e}")
        
        return alerts
    
    def _severity_rank(self, severity: AlertSeverity) -> int:
        """Get rank for alert severity."""
        ranks = {
            AlertSeverity.CRITICAL: 3,
            AlertSeverity.WARNING: 2,
            AlertSeverity.INFO: 1,
        }
        return ranks.get(severity, 0)
    
    def _days_ago(self, date) -> float:
        """Calculate days since a date."""
        try:
            if isinstance(date, str):
                date = datetime.fromisoformat(date)
            return (datetime.now() - date).days
        except Exception:
            return 0
