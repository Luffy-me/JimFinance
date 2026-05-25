"""
Comprehensive tests for Financial Intelligence modules.

Tests cover all analytics engines with edge cases and confidence scoring validation.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
import statistics

from app.ml.financial_intelligence import (
    FinancialMetricsEngine,
    MerchantIntelligenceSystem,
    SubscriptionAnalyzer,
    FinancialRunwayEngine,
    CashflowAnalyzer,
    ForecastingEngine,
    BehavioralAnalyzer,
)


class TestFinancialMetricsEngine:
    """Test Financial Metrics Engine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = FinancialMetricsEngine()
        self.base_date = datetime(2024, 1, 1)
    
    def _create_transactions(self, count=30, daily_amount=50):
        """Create test transactions."""
        transactions = []
        for i in range(count):
            transactions.append({
                'amount': daily_amount,
                'merchant': 'Test Merchant',
                'category': 'food',
                'transaction_type': 'expense',
                'transaction_date': self.base_date + timedelta(days=i),
                'date': self.base_date + timedelta(days=i),
            })
        return transactions
    
    def test_empty_transactions(self):
        """Test metrics with empty transactions."""
        metrics = self.engine.calculate_all_metrics([], Decimal(1000))
        assert metrics.savings_rate.confidence == 0.0
        assert metrics.financial_health_score.value == 50.0
    
    def test_savings_rate_calculation(self):
        """Test savings rate calculation."""
        transactions = [
            {
                'amount': 3000, 'transaction_type': 'income', 'category': 'salary',
                'merchant': 'Employer', 'transaction_date': self.base_date, 'date': self.base_date,
            },
            {
                'amount': 1000, 'transaction_type': 'expense', 'category': 'food',
                'merchant': 'Store', 'transaction_date': self.base_date + timedelta(days=1), 'date': self.base_date + timedelta(days=1),
            },
            {
                'amount': 500, 'transaction_type': 'expense', 'category': 'transport',
                'merchant': 'Transit', 'transaction_date': self.base_date + timedelta(days=2), 'date': self.base_date + timedelta(days=2),
            },
        ]
        
        metrics = self.engine.calculate_all_metrics(transactions, Decimal(5000))
        
        # (3000 - 1500) / 3000 = 0.5 = 50%
        assert metrics.savings_rate.value == 50.0
        assert metrics.savings_rate.unit == '%'
    
    def test_burn_rate_calculation(self):
        """Test burn rate calculation."""
        transactions = self._create_transactions(count=90, daily_amount=50)
        metrics = self.engine.calculate_all_metrics(transactions, Decimal(10000))
        
        # Expected: ~1500/month (50 * 30)
        expected_burn = 50 * 30
        assert abs(metrics.burn_rate.value - expected_burn) < 100  # Allow some variance
    
    def test_confidence_scoring(self):
        """Test confidence scoring based on data."""
        # Few transactions = low confidence
        few_txns = self._create_transactions(count=3)
        metrics_few = self.engine.calculate_all_metrics(few_txns, Decimal(1000))
        
        # Many transactions = higher confidence
        many_txns = self._create_transactions(count=50)
        metrics_many = self.engine.calculate_all_metrics(many_txns, Decimal(1000))
        
        assert metrics_many.savings_rate.confidence > metrics_few.savings_rate.confidence
    
    def test_health_score_range(self):
        """Test health score is within 0-100."""
        transactions = self._create_transactions(count=60)
        metrics = self.engine.calculate_all_metrics(transactions, Decimal(5000))
        
        assert 0 <= metrics.financial_health_score.value <= 100
    
    def test_volatility_calculation(self):
        """Test volatility/smoothness calculation."""
        # Consistent transactions = low volatility
        consistent_txns = self._create_transactions(count=30, daily_amount=50)
        metrics_consistent = self.engine.calculate_all_metrics(consistent_txns, Decimal(5000))
        
        # Variable transactions = high volatility
        variable_txns = [
            {
                'amount': 50 if i % 2 == 0 else 200,
                'merchant': 'Merchant',
                'category': 'food',
                'transaction_type': 'expense',
                'transaction_date': self.base_date + timedelta(days=i),
                'date': self.base_date + timedelta(days=i),
            }
            for i in range(30)
        ]
        metrics_variable = self.engine.calculate_all_metrics(variable_txns, Decimal(5000))
        
        assert metrics_consistent.volatility_score.value > metrics_variable.volatility_score.value
    
    def test_essential_vs_discretionary(self):
        """Test essential vs discretionary categorization."""
        transactions = [
            {'amount': 50, 'category': 'food', 'transaction_type': 'expense', 'merchant': 'Store', 'transaction_date': self.base_date, 'date': self.base_date},
            {'amount': 20, 'category': 'transport', 'transaction_type': 'expense', 'merchant': 'Transit', 'transaction_date': self.base_date, 'date': self.base_date},
            {'amount': 30, 'category': 'entertainment', 'transaction_type': 'expense', 'merchant': 'Theater', 'transaction_date': self.base_date, 'date': self.base_date},
        ]
        
        metrics = self.engine.calculate_all_metrics(transactions, Decimal(1000))
        
        essential = metrics.essential_vs_discretionary['essential_monthly'].value
        discretionary = metrics.essential_vs_discretionary['discretionary_monthly'].value
        
        assert essential > 0
        assert discretionary > 0


class TestMerchantIntelligenceSystem:
    """Test Merchant Intelligence System."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.system = MerchantIntelligenceSystem()
        self.base_date = datetime(2024, 1, 1)
    
    def _create_merchant_transactions(self, merchant='Starbucks', count=5, amount=5):
        """Create transactions for a specific merchant."""
        return [
            {
                'amount': amount,
                'merchant': merchant,
                'category': 'food',
                'transaction_type': 'expense',
                'transaction_date': self.base_date + timedelta(days=i),
                'date': self.base_date + timedelta(days=i),
            }
            for i in range(count)
        ]
    
    def test_merchant_normalization(self):
        """Test merchant name normalization."""
        name1 = self.system._normalize_merchant_name("STARBUCKS COFFEE LLC")
        name2 = self.system._normalize_merchant_name("starbucks coffee llc")
        name3 = self.system._normalize_merchant_name("(STARBUCKS) Coffee LLC")
        
        # Should normalize to similar names
        assert name1 == name2
    
    def test_single_merchant_profiling(self):
        """Test profiling a single merchant."""
        transactions = self._create_merchant_transactions('Coffee Shop', count=5, amount=5)
        profiles = self.system.profile_merchants(transactions)
        
        assert 'coffee shop' in profiles
        profile = profiles['coffee shop']
        
        assert profile.transaction_count == 5
        assert profile.total_spent == 25.0
        assert profile.average_transaction == 5.0
    
    def test_subscription_detection(self):
        """Test subscription detection."""
        # Regular Netflix transactions
        transactions = [
            {
                'amount': 15.99,
                'merchant': 'Netflix',
                'category': 'subscriptions',
                'transaction_type': 'expense',
                'transaction_date': self.base_date + timedelta(days=i*30),
                'date': self.base_date + timedelta(days=i*30),
            }
            for i in range(4)
        ]
        
        profiles = self.system.profile_merchants(transactions)
        netflix_profile = profiles.get('netflix')
        
        assert netflix_profile is not None
        assert netflix_profile.is_likely_subscription
    
    def test_merchant_risk_scoring(self):
        """Test merchant risk scoring."""
        normal_merchant = self._create_merchant_transactions('Coffee Shop', count=5)
        suspicious_merchant = self._create_merchant_transactions('Casino', count=5)
        
        profiles_normal = self.system.profile_merchants(normal_merchant)
        profiles_suspicious = self.system.profile_merchants(suspicious_merchant)
        
        risk_normal = list(profiles_normal.values())[0].merchant_risk_score
        risk_suspicious = list(profiles_suspicious.values())[0].merchant_risk_score
        
        # Casino should have higher risk
        assert risk_suspicious > risk_normal
    
    def test_loyalty_program_detection(self):
        """Test loyalty program detection."""
        starbucks_txns = self._create_merchant_transactions('Starbucks')
        profiles = self.system.profile_merchants(starbucks_txns)
        starbucks = profiles.get('starbucks')
        
        assert starbucks is not None
        assert starbucks.is_loyalty_program


class TestSubscriptionAnalyzer:
    """Test Subscription Analyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = SubscriptionAnalyzer()
        self.base_date = datetime(2024, 1, 1)
    
    def _create_subscription_transactions(self, merchant='Netflix', amount=15.99, days_between=30, count=4):
        """Create subscription-like transactions."""
        return [
            {
                'amount': amount,
                'merchant': merchant,
                'category': 'subscriptions',
                'transaction_type': 'expense',
                'transaction_date': self.base_date + timedelta(days=i*days_between),
                'date': self.base_date + timedelta(days=i*days_between),
            }
            for i in range(count)
        ]
    
    def test_subscription_detection(self):
        """Test subscription detection."""
        transactions = self._create_subscription_transactions('Spotify', 9.99)
        subscriptions = self.analyzer.detect_subscriptions(transactions)
        
        assert len(subscriptions) > 0
        spotify = subscriptions[0]
        assert spotify.is_active
        assert spotify.billing_cycle == 'monthly'
    
    def test_subscription_cost_analysis(self):
        """Test subscription cost analysis."""
        transactions = self._create_subscription_transactions('Netflix', 15.99)
        subscriptions = self.analyzer.detect_subscriptions(transactions)
        analysis = self.analyzer.analyze_subscription_costs(subscriptions)
        
        assert analysis['subscription_count'] > 0
        yearly_cost = analysis['total_yearly']
        assert abs(yearly_cost - (15.99 * 12)) < 10  # Allow small variance
    
    def test_churn_risk_calculation(self):
        """Test churn risk detection."""
        # Active subscription
        active_txns = self._create_subscription_transactions(count=4)
        active_subs = self.analyzer.detect_subscriptions(active_txns)
        active_risk = active_subs[0].churn_risk if active_subs else 0
        
        # Inactive subscription (old transactions)
        inactive_txns = [
            {
                'amount': 15.99,
                'merchant': 'Netflix',
                'category': 'subscriptions',
                'transaction_type': 'expense',
                'transaction_date': self.base_date - timedelta(days=200),
                'date': self.base_date - timedelta(days=200),
            }
        ]
        inactive_subs = self.analyzer.detect_subscriptions(inactive_txns)
        inactive_risk = inactive_subs[0].churn_risk if inactive_subs else 0
        
        # Inactive should have higher churn risk
        if inactive_subs:
            assert inactive_risk >= active_risk


class TestFinancialRunwayEngine:
    """Test Financial Runway Engine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = FinancialRunwayEngine()
    
    def test_runway_calculation(self):
        """Test basic runway calculation."""
        account_balance = 3000.0
        monthly_burn = 1000.0
        
        analysis = self.engine.calculate_runway_analysis(
            account_balance=Decimal(account_balance),
            monthly_burn_rate=monthly_burn,
        )
        
        # 3000 / 1000 = 3 months
        assert analysis.primary_scenario.runway_months == 3.0
    
    def test_runway_with_positive_income(self):
        """Test runway when income exceeds burn."""
        account_balance = 5000.0
        burn_rate = 1000.0
        income = 2000.0
        
        analysis = self.engine.calculate_runway_analysis(
            account_balance=Decimal(account_balance),
            monthly_burn_rate=burn_rate,
            monthly_income=income,
        )
        
        # Income exceeds burn, so runway should be very long
        assert analysis.primary_scenario.runway_months > 100
    
    def test_emergency_fund_analysis(self):
        """Test emergency fund sufficiency."""
        account_balance = 3000.0
        burn_rate = 1000.0
        
        analysis = self.engine.calculate_runway_analysis(
            account_balance=Decimal(account_balance),
            monthly_burn_rate=burn_rate,
        )
        
        # 3000 / 1000 = 3 months of coverage
        assert analysis.emergency_fund_status['coverage_months'] == 3.0
        assert analysis.emergency_fund_status['status'] == 'adequate'
    
    def test_sustainability_score(self):
        """Test sustainability score calculation."""
        analysis_poor = self.engine.calculate_runway_analysis(
            account_balance=Decimal(500),
            monthly_burn_rate=1000,
        )
        
        analysis_good = self.engine.calculate_runway_analysis(
            account_balance=Decimal(30000),
            monthly_burn_rate=1000,
        )
        
        assert analysis_good.sustainability_score > analysis_poor.sustainability_score


class TestCashflowAnalyzer:
    """Test Cashflow Analyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = CashflowAnalyzer()
        self.base_date = datetime(2024, 1, 1)
    
    def _create_monthly_cashflow(self, months=3, monthly_income=3000, monthly_expense=2000):
        """Create monthly cashflow transactions."""
        transactions = []
        for m in range(months):
            month_date = self.base_date + timedelta(days=m*30)
            # Income
            transactions.append({
                'amount': monthly_income,
                'merchant': 'Employer',
                'category': 'salary',
                'transaction_type': 'income',
                'transaction_date': month_date,
                'date': month_date,
            })
            # Expense
            transactions.append({
                'amount': monthly_expense,
                'merchant': 'Expenses',
                'category': 'food',
                'transaction_type': 'expense',
                'transaction_date': month_date + timedelta(days=5),
                'date': month_date + timedelta(days=5),
            })
        return transactions
    
    def test_cashflow_smoothness(self):
        """Test cashflow smoothness calculation."""
        # Consistent cash flow
        consistent = self._create_monthly_cashflow(months=3, monthly_expense=2000)
        metrics_consistent = self.analyzer.analyze_cashflow(consistent)
        
        # Variable cash flow
        variable = [
            {
                'amount': 1000, 'merchant': 'Exp', 'category': 'food',
                'transaction_type': 'expense', 'transaction_date': self.base_date, 'date': self.base_date,
            },
            {
                'amount': 3000, 'merchant': 'Exp', 'category': 'food',
                'transaction_type': 'expense', 'transaction_date': self.base_date + timedelta(days=30), 'date': self.base_date + timedelta(days=30),
            },
            {
                'amount': 500, 'merchant': 'Exp', 'category': 'food',
                'transaction_type': 'expense', 'transaction_date': self.base_date + timedelta(days=60), 'date': self.base_date + timedelta(days=60),
            },
        ]
        metrics_variable = self.analyzer.analyze_cashflow(variable)
        
        # Consistent should have higher smoothness
        assert metrics_consistent.cashflow_smoothness > metrics_variable.cashflow_smoothness


class TestForecastingEngine:
    """Test Forecasting Engine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = ForecastingEngine()
        self.base_date = datetime(2023, 1, 1)
    
    def _create_yearly_transactions(self, monthly_amount=1000):
        """Create a year of transactions."""
        transactions = []
        for month in range(12):
            date = self.base_date + timedelta(days=month*30)
            transactions.append({
                'amount': monthly_amount,
                'merchant': 'Store',
                'category': 'food',
                'transaction_type': 'expense',
                'transaction_date': date,
                'date': date,
            })
        return transactions
    
    def test_forecast_generation(self):
        """Test forecast generation."""
        transactions = self._create_yearly_transactions()
        forecast = self.engine.forecast_spending(transactions, forecast_months=6)
        
        assert 'forecasts' in forecast
        assert len(forecast['forecasts']) == 6
        
        # Check forecast structure
        for f in forecast['forecasts']:
            assert 'period' in f
            assert 'forecasted_value' in f
            assert 'confidence_level' in f
    
    def test_confidence_intervals(self):
        """Test confidence interval generation."""
        transactions = self._create_yearly_transactions()
        forecast = self.engine.forecast_spending(transactions, forecast_months=6)
        
        for f in forecast['forecasts']:
            assert f['lower_confidence_bound'] <= f['forecasted_value']
            assert f['forecasted_value'] <= f['upper_confidence_bound']


class TestBehavioralAnalyzer:
    """Test Behavioral Analyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = BehavioralAnalyzer()
        self.base_date = datetime(2024, 1, 1)
    
    def test_lifestyle_inflation_detection(self):
        """Test lifestyle inflation detection."""
        # Early period: $1000/month
        # Late period: $1500/month (50% increase = lifestyle inflation)
        transactions = []
        
        for m in range(6):
            month_date = self.base_date + timedelta(days=m*30)
            amount = 1000 if m < 3 else 1500
            
            transactions.append({
                'amount': amount,
                'merchant': 'Store',
                'category': 'shopping',
                'transaction_type': 'expense',
                'transaction_date': month_date,
                'date': month_date,
            })
        
        insights = self.analyzer.analyze_behavior(transactions)
        
        # Should detect lifestyle inflation
        inflation_insights = [i for i in insights if i.insight_type == 'lifestyle_inflation']
        assert len(inflation_insights) > 0
    
    def test_spending_spike_detection(self):
        """Test spending spike detection."""
        transactions = [
            {
                'amount': 50, 'merchant': 'Store', 'category': 'shopping',
                'transaction_type': 'expense', 'transaction_date': self.base_date + timedelta(days=i), 'date': self.base_date + timedelta(days=i),
            }
            for i in range(10)
        ]
        
        # Add spike
        transactions.append({
            'amount': 500, 'merchant': 'Electronics', 'category': 'shopping',
            'transaction_type': 'expense', 'transaction_date': self.base_date + timedelta(days=11), 'date': self.base_date + timedelta(days=11),
        })
        
        insights = self.analyzer.analyze_behavior(transactions)
        spike_insights = [i for i in insights if i.insight_type == 'spending_spike']
        
        # Should detect spike
        assert len(spike_insights) > 0
    
    def test_discretionary_ratio_detection(self):
        """Test discretionary spending ratio detection."""
        # 80% discretionary, 20% essential
        transactions = [
            {
                'amount': 40, 'merchant': 'Store', 'category': 'entertainment',
                'transaction_type': 'expense', 'transaction_date': self.base_date, 'date': self.base_date,
            } for _ in range(40)
        ] + [
            {
                'amount': 10, 'merchant': 'Store', 'category': 'food',
                'transaction_type': 'expense', 'transaction_date': self.base_date, 'date': self.base_date,
            } for _ in range(10)
        ]
        
        insights = self.analyzer.analyze_behavior(transactions)
        
        # Should detect high discretionary ratio
        high_disc = [i for i in insights if i.insight_type == 'high_discretionary_ratio']
        assert len(high_disc) > 0


# Integration tests
class TestFinancialIntelligenceIntegration:
    """Integration tests for the financial intelligence system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.base_date = datetime(2024, 1, 1)
    
    def _create_realistic_transactions(self):
        """Create realistic monthly transactions."""
        transactions = []
        
        for day in range(90):  # 3 months
            date = self.base_date + timedelta(days=day)
            
            # Monthly income
            if day % 30 == 0:
                transactions.append({
                    'amount': 5000,
                    'merchant': 'Employer',
                    'category': 'salary',
                    'transaction_type': 'income',
                    'transaction_date': date,
                    'date': date,
                })
            
            # Daily expenses
            transactions.append({
                'amount': 50,
                'merchant': 'Coffee Shop',
                'category': 'food',
                'transaction_type': 'expense',
                'transaction_date': date,
                'date': date,
            })
            
            # Weekly subscription
            if day % 7 == 0:
                transactions.append({
                    'amount': 15.99,
                    'merchant': 'Netflix',
                    'category': 'subscriptions',
                    'transaction_type': 'expense',
                    'transaction_date': date,
                    'date': date,
                })
        
        return transactions
    
    def test_all_engines_together(self):
        """Test all engines work together."""
        transactions = self._create_realistic_transactions()
        account_balance = Decimal(10000)
        
        # Financial Metrics
        metrics_engine = FinancialMetricsEngine()
        metrics = metrics_engine.calculate_all_metrics(transactions, account_balance)
        assert metrics is not None
        
        # Merchant Intelligence
        merchant_system = MerchantIntelligenceSystem()
        merchants = merchant_system.profile_merchants(transactions)
        assert len(merchants) > 0
        
        # Subscriptions
        sub_analyzer = SubscriptionAnalyzer()
        subscriptions = sub_analyzer.detect_subscriptions(transactions)
        assert len(subscriptions) > 0
        
        # Cashflow
        cf_analyzer = CashflowAnalyzer()
        cashflow = cf_analyzer.analyze_cashflow(transactions, account_balance)
        assert cashflow is not None
        
        # Runway
        runway_engine = FinancialRunwayEngine()
        runway = runway_engine.calculate_runway_analysis(
            account_balance, 
            burn_rate=metrics.burn_rate.value
        )
        assert runway is not None
        
        # Forecast
        forecast_engine = ForecastingEngine()
        forecast = forecast_engine.forecast_spending(transactions)
        assert forecast is not None
        
        # Behavior
        behavior_analyzer = BehavioralAnalyzer()
        insights = behavior_analyzer.analyze_behavior(transactions)
        assert isinstance(insights, list)
