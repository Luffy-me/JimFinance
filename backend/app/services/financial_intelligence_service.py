"""
Financial Intelligence Service - Orchestrates all analytics modules.

Provides comprehensive financial analysis with caching and batch processing.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal
import hashlib
import json

from app.ml.financial_intelligence import (
    FinancialMetricsEngine,
    MerchantIntelligenceSystem,
    SubscriptionAnalyzer,
    FinancialRunwayEngine,
    CashflowAnalyzer,
    ForecastingEngine,
    BehavioralAnalyzer,
)

logger = logging.getLogger(__name__)


class FinancialIntelligenceService:
    """
    Orchestrates all financial intelligence modules.
    
    Provides:
    - Comprehensive financial metrics
    - Merchant and subscription analysis
    - Cashflow analysis
    - Financial runway projections
    - Spending forecasts
    - Behavioral insights
    - Health reports
    """
    
    def __init__(self):
        """Initialize all analytics engines."""
        self.metrics_engine = FinancialMetricsEngine()
        self.merchant_system = MerchantIntelligenceSystem()
        self.subscription_analyzer = SubscriptionAnalyzer()
        self.runway_engine = FinancialRunwayEngine()
        self.cashflow_analyzer = CashflowAnalyzer()
        self.forecasting_engine = ForecastingEngine()
        self.behavioral_analyzer = BehavioralAnalyzer()
        
        self.logger = logger
    
    def generate_comprehensive_report(
        self,
        transactions: List[Dict],
        account_balance: Decimal,
        account_currency: str = "USD",
        monthly_income: Optional[float] = None,
    ) -> Dict:
        """
        Generate comprehensive financial intelligence report.
        
        Args:
            transactions: Historical transactions
            account_balance: Current account balance
            account_currency: Currency code
            monthly_income: Average monthly income (optional)
        
        Returns:
            Comprehensive analysis report
        """
        self.logger.info(f"Generating comprehensive report for {len(transactions)} transactions")
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'transaction_count': len(transactions),
            'account_balance': float(account_balance),
            'currency': account_currency,
        }
        
        # 1. Financial Metrics
        try:
            metrics = self.metrics_engine.calculate_all_metrics(
                transactions=transactions,
                account_balance=account_balance,
                account_currency=account_currency,
            )
            report['metrics'] = metrics.to_dict()
        except Exception as e:
            self.logger.error(f"Error calculating metrics: {e}")
            report['metrics'] = {'error': str(e)}
        
        # 2. Merchant Analysis
        try:
            merchant_analysis = self.merchant_system.analyze_spending_by_merchant(
                transactions=transactions,
                top_n=10,
            )
            report['merchants'] = merchant_analysis
        except Exception as e:
            self.logger.error(f"Error analyzing merchants: {e}")
            report['merchants'] = {'error': str(e)}
        
        # 3. Subscription Analysis
        try:
            subscriptions = self.subscription_analyzer.detect_subscriptions(transactions)
            subscription_analysis = self.subscription_analyzer.analyze_subscription_costs(subscriptions)
            report['subscriptions'] = subscription_analysis
        except Exception as e:
            self.logger.error(f"Error analyzing subscriptions: {e}")
            report['subscriptions'] = {'error': str(e)}
        
        # 4. Cashflow Analysis
        try:
            cashflow = self.cashflow_analyzer.analyze_cashflow(
                transactions=transactions,
                account_balance=account_balance,
            )
            # Convert dataclass to dict
            cashflow_dict = {
                'inflow_velocity': cashflow.inflow_velocity,
                'outflow_velocity': cashflow.outflow_velocity,
                'cashflow_smoothness': cashflow.cashflow_smoothness,
                'peak_spending_month': cashflow.peak_spending_month,
                'peak_spending_amount': cashflow.peak_spending_amount,
                'trough_spending_month': cashflow.trough_spending_month,
                'trough_spending_amount': cashflow.trough_spending_amount,
                'liquidity_ratio': cashflow.liquidity_ratio,
                'has_seasonality': cashflow.has_seasonality,
                'seasonality_pattern': cashflow.seasonality_pattern,
                'average_monthly_inflow': cashflow.average_monthly_inflow,
                'average_monthly_outflow': cashflow.average_monthly_outflow,
                'inflow_consistency': cashflow.inflow_consistency,
                'outflow_consistency': cashflow.outflow_consistency,
            }
            report['cashflow'] = cashflow_dict
        except Exception as e:
            self.logger.error(f"Error analyzing cashflow: {e}")
            report['cashflow'] = {'error': str(e)}
        
        # 5. Runway Analysis
        try:
            if 'metrics' in report and 'burn_rate' in report['metrics']:
                burn_rate = report['metrics']['burn_rate']['value']
                runway_analysis = self.runway_engine.calculate_runway_analysis(
                    account_balance=account_balance,
                    monthly_burn_rate=burn_rate,
                    monthly_income=monthly_income,
                    transactions=transactions,
                )
                
                runway_dict = {
                    'primary_scenario': {
                        'scenario_name': runway_analysis.primary_scenario.scenario_name,
                        'burn_rate_monthly': runway_analysis.primary_scenario.burn_rate_monthly,
                        'runway_days': runway_analysis.primary_scenario.runway_days,
                        'runway_months': runway_analysis.primary_scenario.runway_months,
                        'exhaustion_date': runway_analysis.primary_scenario.exhaustion_date.isoformat(),
                    },
                    'emergency_fund_status': runway_analysis.emergency_fund_status,
                    'sustainability_score': runway_analysis.sustainability_score,
                    'recommendations': runway_analysis.recommendations,
                }
                report['runway'] = runway_dict
        except Exception as e:
            self.logger.error(f"Error analyzing runway: {e}")
            report['runway'] = {'error': str(e)}
        
        # 6. Spending Forecast
        try:
            forecast = self.forecasting_engine.forecast_spending(transactions)
            report['forecast'] = forecast
        except Exception as e:
            self.logger.error(f"Error forecasting: {e}")
            report['forecast'] = {'error': str(e)}
        
        # 7. Behavioral Insights
        try:
            insights = self.behavioral_analyzer.analyze_behavior(
                transactions=transactions,
                monthly_income=monthly_income,
            )
            report['behavioral_insights'] = [
                {
                    'type': i.insight_type,
                    'title': i.title,
                    'description': i.description,
                    'metric_value': i.metric_value,
                    'metric_unit': i.metric_unit,
                    'confidence': i.confidence,
                    'recommendation': i.recommendation,
                }
                for i in insights
            ]
        except Exception as e:
            self.logger.error(f"Error analyzing behavior: {e}")
            report['behavioral_insights'] = []
        
        return report
    
    def get_financial_health_score(
        self,
        transactions: List[Dict],
        account_balance: Decimal,
        monthly_income: Optional[float] = None,
    ) -> Dict:
        """
        Get overall financial health score and summary.
        
        Returns dict with health score (0-100) and key metrics.
        """
        try:
            metrics = self.metrics_engine.calculate_all_metrics(
                transactions=transactions,
                account_balance=account_balance,
            )
            
            health_score = metrics.financial_health_score.value
            
            return {
                'health_score': health_score,
                'health_status': self._score_to_status(health_score),
                'savings_rate': metrics.savings_rate.value,
                'burn_rate': metrics.burn_rate.value,
                'financial_health_score': health_score,
                'volatility_score': metrics.volatility_score.value,
                'confidence_score': metrics.financial_health_score.confidence,
            }
        except Exception as e:
            self.logger.error(f"Error calculating health score: {e}")
            return {
                'health_score': 50.0,
                'health_status': 'unknown',
                'error': str(e),
            }
    
    def get_metrics_summary(
        self,
        transactions: List[Dict],
        account_balance: Decimal,
    ) -> Dict:
        """Get quick metrics summary."""
        try:
            metrics = self.metrics_engine.calculate_all_metrics(
                transactions=transactions,
                account_balance=account_balance,
            )
            
            return {
                'savings_rate': {
                    'value': metrics.savings_rate.value,
                    'confidence': metrics.savings_rate.confidence,
                },
                'burn_rate': {
                    'value': metrics.burn_rate.value,
                    'confidence': metrics.burn_rate.confidence,
                },
                'health_score': {
                    'value': metrics.financial_health_score.value,
                    'confidence': metrics.financial_health_score.confidence,
                },
                'volatility': {
                    'value': metrics.volatility_score.value,
                    'confidence': metrics.volatility_score.confidence,
                },
            }
        except Exception as e:
            self.logger.error(f"Error getting metrics summary: {e}")
            return {'error': str(e)}
    
    def get_merchant_insights(
        self,
        transactions: List[Dict],
        top_n: int = 10,
    ) -> Dict:
        """Get merchant spending analysis."""
        try:
            return self.merchant_system.analyze_spending_by_merchant(
                transactions=transactions,
                top_n=top_n,
            )
        except Exception as e:
            self.logger.error(f"Error getting merchant insights: {e}")
            return {'error': str(e)}
    
    def get_subscription_insights(
        self,
        transactions: List[Dict],
    ) -> Dict:
        """Get subscription analysis."""
        try:
            subscriptions = self.subscription_analyzer.detect_subscriptions(transactions)
            return self.subscription_analyzer.analyze_subscription_costs(subscriptions)
        except Exception as e:
            self.logger.error(f"Error getting subscription insights: {e}")
            return {'error': str(e)}
    
    def get_cashflow_insights(
        self,
        transactions: List[Dict],
        account_balance: Optional[Decimal] = None,
    ) -> Dict:
        """Get cashflow analysis."""
        try:
            cashflow = self.cashflow_analyzer.analyze_cashflow(
                transactions=transactions,
                account_balance=account_balance,
            )
            
            return {
                'inflow_velocity': cashflow.inflow_velocity,
                'outflow_velocity': cashflow.outflow_velocity,
                'smoothness': cashflow.cashflow_smoothness,
                'peak_month': cashflow.peak_spending_month,
                'trough_month': cashflow.trough_spending_month,
                'has_seasonality': cashflow.has_seasonality,
                'average_monthly_inflow': cashflow.average_monthly_inflow,
                'average_monthly_outflow': cashflow.average_monthly_outflow,
            }
        except Exception as e:
            self.logger.error(f"Error getting cashflow insights: {e}")
            return {'error': str(e)}
    
    def get_runway_analysis(
        self,
        transactions: List[Dict],
        account_balance: Decimal,
        monthly_income: Optional[float] = None,
    ) -> Dict:
        """Get runway analysis."""
        try:
            # Calculate burn rate first
            metrics = self.metrics_engine.calculate_all_metrics(
                transactions=transactions,
                account_balance=account_balance,
            )
            burn_rate = metrics.burn_rate.value
            
            if burn_rate <= 0:
                return {'error': 'Cannot calculate runway with zero or negative burn rate'}
            
            analysis = self.runway_engine.calculate_runway_analysis(
                account_balance=account_balance,
                monthly_burn_rate=burn_rate,
                monthly_income=monthly_income,
            )
            
            return {
                'runway_months': analysis.primary_scenario.runway_months,
                'runway_days': analysis.primary_scenario.runway_days,
                'sustainability_score': analysis.sustainability_score,
                'emergency_fund_status': analysis.emergency_fund_status['status'],
                'recommendations': analysis.recommendations,
            }
        except Exception as e:
            self.logger.error(f"Error getting runway analysis: {e}")
            return {'error': str(e)}
    
    def get_forecast(
        self,
        transactions: List[Dict],
        forecast_months: int = 12,
    ) -> Dict:
        """Get spending forecast."""
        try:
            return self.forecasting_engine.forecast_spending(
                transactions=transactions,
                forecast_months=forecast_months,
            )
        except Exception as e:
            self.logger.error(f"Error getting forecast: {e}")
            return {'error': str(e)}
    
    def get_behavioral_insights(
        self,
        transactions: List[Dict],
        monthly_income: Optional[float] = None,
    ) -> List[Dict]:
        """Get behavioral insights."""
        try:
            insights = self.behavioral_analyzer.analyze_behavior(
                transactions=transactions,
                monthly_income=monthly_income,
            )
            
            return [
                {
                    'type': i.insight_type,
                    'title': i.title,
                    'description': i.description,
                    'confidence': i.confidence,
                    'recommendation': i.recommendation,
                }
                for i in insights
            ]
        except Exception as e:
            self.logger.error(f"Error getting behavioral insights: {e}")
            return []
    
    @staticmethod
    def _score_to_status(score: float) -> str:
        """Convert health score to status."""
        if score >= 80:
            return 'excellent'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'fair'
        else:
            return 'poor'
