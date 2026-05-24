"""
Base agent class for multi-agent reasoning system.
Defines common interface and utilities for all agents.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from app.ml.agents.types import (
    FinancialMetrics,
    TransactionContext,
    AgentError,
)

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all reasoning agents."""
    
    def __init__(self, name: str):
        """
        Initialize agent.
        
        Args:
            name: Agent name for logging and identification
        """
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.created_at = datetime.utcnow()
        self._call_count = 0
        self._error_count = 0
        
    @abstractmethod
    async def analyze(
        self,
        financial_metrics: FinancialMetrics,
        transaction_context: TransactionContext,
        user_id: int,
    ) -> Dict[str, Any]:
        """
        Analyze financial data and generate insights.
        
        Args:
            financial_metrics: Current financial metrics
            transaction_context: Transaction context and history
            user_id: User ID for personalization
            
        Returns:
            Analysis results as dictionary
            
        Raises:
            AgentError: If analysis fails
        """
        pass
    
    def validate_inputs(
        self,
        financial_metrics: FinancialMetrics,
        transaction_context: TransactionContext,
    ) -> bool:
        """
        Validate inputs before analysis.
        
        Args:
            financial_metrics: Financial metrics to validate
            transaction_context: Transaction context to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not financial_metrics:
            self.logger.warning("Missing financial metrics")
            return False
            
        if not transaction_context:
            self.logger.warning("Missing transaction context")
            return False
            
        if financial_metrics.total_expenses < 0:
            self.logger.warning("Invalid expense data")
            return False
            
        return True
    
    def log_call(self, success: bool = True, error: Optional[str] = None):
        """
        Log agent call for monitoring.
        
        Args:
            success: Whether call was successful
            error: Error message if failed
        """
        self._call_count += 1
        if not success:
            self._error_count += 1
            
        if error:
            self.logger.error(f"{self.name} call #{self._call_count} failed: {error}")
        else:
            self.logger.info(f"{self.name} call #{self._call_count} completed successfully")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get agent statistics.
        
        Returns:
            Statistics dictionary
        """
        success_rate = (
            ((self._call_count - self._error_count) / self._call_count * 100)
            if self._call_count > 0
            else 0
        )
        
        return {
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "total_calls": self._call_count,
            "successful_calls": self._call_count - self._error_count,
            "failed_calls": self._error_count,
            "success_rate": success_rate,
        }
    
    def format_financial_data(
        self,
        financial_metrics: FinancialMetrics,
        transaction_context: TransactionContext,
    ) -> str:
        """
        Format financial data for agent consumption.
        
        Args:
            financial_metrics: Financial metrics
            transaction_context: Transaction context
            
        Returns:
            Formatted string representation
        """
        metrics = financial_metrics.to_dict()
        context = transaction_context.to_dict()
        
        # Build formatted string
        formatted = f"""
        FINANCIAL PROFILE:
        - Total Monthly Income: ${metrics['total_income']:,.2f}
        - Total Monthly Expenses: ${metrics['total_expenses']:,.2f}
        - Savings Rate: {metrics['savings_rate']:.1%}
        - Average Monthly Expense: ${metrics['average_monthly_expense']:,.2f}
        - Transaction Count: {metrics['transaction_count']}
        - Recurring Expenses: ${metrics['recurring_expenses']:,.2f}
        
        SPENDING BY CATEGORY:
        {self._format_category_breakdown(metrics['expense_categories'])}
        
        ACCOUNT BALANCES:
        {self._format_balances(metrics['account_balances'])}
        
        SPENDING TRENDS:
        {self._format_trends(context['spending_trends'])}
        """
        
        return formatted.strip()
    
    @staticmethod
    def _format_category_breakdown(categories: Dict[str, float]) -> str:
        """Format spending by category."""
        if not categories:
            return "- No category data"
        
        lines = []
        for category, amount in sorted(
            categories.items(), key=lambda x: x[1], reverse=True
        ):
            lines.append(f"  - {category.title()}: ${amount:,.2f}")
        return "\n".join(lines)
    
    @staticmethod
    def _format_balances(balances: Dict[str, float]) -> str:
        """Format account balances."""
        if not balances:
            return "- No account data"
        
        lines = []
        total = 0
        for account, balance in sorted(balances.items()):
            lines.append(f"  - {account}: ${balance:,.2f}")
            total += balance
        lines.append(f"  - TOTAL: ${total:,.2f}")
        return "\n".join(lines)
    
    @staticmethod
    def _format_trends(trends: Dict[str, float]) -> str:
        """Format spending trends."""
        if not trends:
            return "- No trend data"
        
        lines = []
        for trend, value in sorted(
            trends.items(), key=lambda x: abs(x[1]), reverse=True
        ):
            direction = "↑" if value > 0 else "↓" if value < 0 else "→"
            lines.append(f"  - {trend}: {direction} {abs(value):.1%}")
        return "\n".join(lines)
