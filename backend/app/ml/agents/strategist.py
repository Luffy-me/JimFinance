"""
Strategist Agent using Google Gemini Pro.
Analyzes financial patterns and generates strategic recommendations.
"""

import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai

from app.core.config import settings
from app.ml.agents.base import BaseAgent
from app.ml.agents.types import (
    FinancialMetrics,
    TransactionContext,
    StrategistOutput,
    StrategyGenerationError,
)

logger = logging.getLogger(__name__)


class StrategistAgent(BaseAgent):
    """
    Strategist Agent powered by Google Gemini Pro.
    Focuses on positive financial strategies and opportunities.
    """
    
    def __init__(self):
        """Initialize Strategist Agent."""
        super().__init__("StrategistAgent")
        
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-pro")
        self.system_prompt = self._build_system_prompt()
    
    @staticmethod
    def _build_system_prompt() -> str:
        """Build system prompt for strategist."""
        return """You are a financial strategist AI analyzing personal finances.
        
Your role is to:
1. Identify spending patterns and opportunities
2. Suggest budget optimizations
3. Recommend savings strategies
4. Propose financial goals
5. Provide actionable recommendations

Focus on:
- Positive, constructive advice
- Realistic, achievable goals
- Quick wins for immediate impact
- Long-term financial health
- Personalization based on spending patterns

Always provide specific, quantified recommendations.
Output should be clear, structured, and actionable."""
    
    async def analyze(
        self,
        financial_metrics: FinancialMetrics,
        transaction_context: TransactionContext,
        user_id: int,
    ) -> Dict[str, Any]:
        """
        Analyze financial data and generate strategic recommendations.
        
        Args:
            financial_metrics: Current financial metrics
            transaction_context: Transaction context and history
            user_id: User ID for personalization
            
        Returns:
            Strategic analysis and recommendations
            
        Raises:
            StrategyGenerationError: If analysis fails
        """
        try:
            if not self.validate_inputs(financial_metrics, transaction_context):
                raise StrategyGenerationError("Invalid input data")
            
            # Format data for analysis
            financial_data = self.format_financial_data(
                financial_metrics, transaction_context
            )
            
            # Build analysis prompt
            prompt = self._build_analysis_prompt(
                financial_data, financial_metrics, transaction_context
            )
            
            # Call Gemini Pro
            self.logger.info(f"Analyzing finances for user {user_id}")
            response = self.model.generate_content(prompt)
            
            if not response.text:
                raise StrategyGenerationError("Empty response from Gemini Pro")
            
            # Parse response
            output = self._parse_response(response.text)
            
            self.log_call(success=True)
            return output.to_dict()
            
        except Exception as e:
            error_msg = f"Strategy generation failed: {str(e)}"
            self.logger.error(error_msg)
            self.log_call(success=False, error=error_msg)
            raise StrategyGenerationError(error_msg)
    
    def _build_analysis_prompt(
        self,
        financial_data: str,
        financial_metrics: FinancialMetrics,
        transaction_context: TransactionContext,
    ) -> str:
        """
        Build detailed analysis prompt for Gemini Pro.
        
        Args:
            financial_data: Formatted financial data
            financial_metrics: Financial metrics
            transaction_context: Transaction context
            
        Returns:
            Complete analysis prompt
        """
        savings_rate = financial_metrics.savings_rate or 0
        expense_avg = financial_metrics.average_monthly_expense or 0
        
        prompt = f"""Analyze the following personal financial profile and provide strategic recommendations:

{financial_data}

Please provide analysis in the following JSON format:
{{
    "spending_analysis": {{
        "highest_category": "category with most spending",
        "lowest_category": "category with least spending",
        "major_expenses": ["top 3 expense categories"],
        "spending_stability": "stable/variable/highly_variable"
    }},
    "budget_suggestions": {{
        "category_1": suggested_monthly_budget,
        "category_2": suggested_monthly_budget
    }},
    "savings_opportunities": [
        {{
            "area": "spending area",
            "current": current_amount,
            "suggested": suggested_amount,
            "monthly_savings": potential_savings,
            "reasoning": "why this optimization"
        }}
    ],
    "goals_suggestions": [
        {{
            "goal": "financial goal",
            "timeline_months": estimated_months,
            "monthly_amount": required_monthly_savings,
            "priority": "high/medium/low",
            "reasoning": "why this goal"
        }}
    ],
    "recommendations": [
        "specific, actionable recommendation 1",
        "specific, actionable recommendation 2",
        "specific, actionable recommendation 3"
    ],
    "confidence_score": 0.0-1.0
}}

Focus on:
1. Current savings rate: {savings_rate:.1%}
2. Average monthly expense: ${expense_avg:,.2f}
3. Recurring expense efficiency
4. Category-specific optimization
5. Quick wins (< 1 month) vs long-term strategies

Provide realistic, quantified recommendations based on the spending patterns shown."""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> StrategistOutput:
        """
        Parse Gemini Pro response into structured format.
        
        Args:
            response_text: Raw response from Gemini Pro
            
        Returns:
            Structured StrategistOutput
            
        Raises:
            StrategyGenerationError: If parsing fails
        """
        try:
            # Extract JSON from response
            json_str = response_text
            
            # Find JSON block if wrapped in markdown
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
            
            # Parse JSON
            data = json.loads(json_str.strip())
            
            # Validate required fields
            required_fields = [
                "spending_analysis",
                "budget_suggestions",
                "savings_opportunities",
                "goals_suggestions",
                "recommendations",
                "confidence_score",
            ]
            
            for field in required_fields:
                if field not in data:
                    raise StrategyGenerationError(f"Missing field: {field}")
            
            # Create output
            output = StrategistOutput(
                recommendations=data.get("recommendations", []),
                budget_suggestions=data.get("budget_suggestions", {}),
                savings_opportunities=data.get("savings_opportunities", []),
                goals_suggestions=data.get("goals_suggestions", []),
                spending_analysis=data.get("spending_analysis", {}),
                confidence_score=float(data.get("confidence_score", 0.75)),
                thinking_process=None,
            )
            
            return output
            
        except json.JSONDecodeError as e:
            raise StrategyGenerationError(f"Failed to parse JSON response: {str(e)}")
        except (ValueError, KeyError) as e:
            raise StrategyGenerationError(f"Invalid response structure: {str(e)}")
