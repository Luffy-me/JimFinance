"""
Critic Agent using Groq API.
Focuses on risk assessment and critical financial analysis.
"""

import json
import logging
from typing import Dict, Any, Optional
from groq import Groq

from app.core.config import settings
from app.ml.agents.base import BaseAgent
from app.ml.agents.types import (
    FinancialMetrics,
    TransactionContext,
    CriticOutput,
    RiskLevel,
    RiskAssessmentError,
)

logger = logging.getLogger(__name__)


class CriticAgent(BaseAgent):
    """
    Critic Agent powered by Groq API.
    Focuses on risk assessment and vulnerability identification.
    """
    
    def __init__(self):
        """Initialize Critic Agent."""
        super().__init__("CriticAgent")
        
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not configured")
        
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.system_prompt = self._build_system_prompt()
    
    @staticmethod
    def _build_system_prompt() -> str:
        """Build system prompt for critic."""
        return """You are a critical financial analyst AI.

Your role is to:
1. Identify financial vulnerabilities and risks
2. Assess financial health and stability
3. Detect concerning spending patterns
4. Flag potential financial emergencies
5. Provide risk mitigation strategies

Focus on:
- Risk identification and quantification
- Early warning signs
- Financial emergency preparedness
- Vulnerability assessment
- Critical issue prioritization

Be thorough but fair. Provide specific, evidence-based concerns with recommended actions."""
    
    async def analyze(
        self,
        financial_metrics: FinancialMetrics,
        transaction_context: TransactionContext,
        user_id: int,
    ) -> Dict[str, Any]:
        """
        Analyze financial data for risks and vulnerabilities.
        
        Args:
            financial_metrics: Current financial metrics
            transaction_context: Transaction context and history
            user_id: User ID for personalization
            
        Returns:
            Risk assessment and vulnerability report
            
        Raises:
            RiskAssessmentError: If analysis fails
        """
        try:
            if not self.validate_inputs(financial_metrics, transaction_context):
                raise RiskAssessmentError("Invalid input data")
            
            # Format data for analysis
            financial_data = self.format_financial_data(
                financial_metrics, transaction_context
            )
            
            # Build analysis prompt
            prompt = self._build_analysis_prompt(
                financial_data, financial_metrics, transaction_context
            )
            
            # Call Groq API
            self.logger.info(f"Assessing risk for user {user_id}")
            message = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1500,
            )
            
            response_text = message.choices[0].message.content
            
            if not response_text:
                raise RiskAssessmentError("Empty response from Groq")
            
            # Parse response
            output = self._parse_response(response_text, financial_metrics)
            
            self.log_call(success=True)
            return output.to_dict()
            
        except Exception as e:
            error_msg = f"Risk assessment failed: {str(e)}"
            self.logger.error(error_msg)
            self.log_call(success=False, error=error_msg)
            raise RiskAssessmentError(error_msg)
    
    def _build_analysis_prompt(
        self,
        financial_data: str,
        financial_metrics: FinancialMetrics,
        transaction_context: TransactionContext,
    ) -> str:
        """
        Build detailed analysis prompt for Groq.
        
        Args:
            financial_data: Formatted financial data
            financial_metrics: Financial metrics
            transaction_context: Transaction context
            
        Returns:
            Complete analysis prompt
        """
        savings_rate = financial_metrics.savings_rate or 0
        
        prompt = f"""Perform critical financial risk assessment:

{financial_data}

Provide assessment in JSON format:
{{
    "risk_level": "low|medium|high|critical",
    "risk_score": 0-100,
    "financial_health_score": 0-100,
    "vulnerabilities": [
        {{
            "type": "vulnerability type",
            "severity": "low|medium|high|critical",
            "description": "what the vulnerability is",
            "potential_impact": "what could happen"
        }}
    ],
    "alerts": [
        {{
            "type": "alert type",
            "message": "specific alert message",
            "recommended_action": "what to do about it"
        }}
    ],
    "critical_issues": [
        "most critical issue 1",
        "most critical issue 2"
    ],
    "recommendations": [
        "immediate risk mitigation action 1",
        "immediate risk mitigation action 2",
        "medium-term risk mitigation action"
    ],
    "confidence_score": 0.0-1.0
}}

Assess based on:
1. Savings rate: {savings_rate:.1%}
2. Emergency fund adequacy (should have 3-6 months expenses)
3. Recurring vs variable expense ratio
4. Spending volatility and stability
5. Debt and account health
6. Transaction anomalies
7. Category concentration risk

Be direct about critical issues."""
        
        return prompt
    
    def _parse_response(
        self,
        response_text: str,
        financial_metrics: FinancialMetrics,
    ) -> CriticOutput:
        """
        Parse Groq response into structured format.
        
        Args:
            response_text: Raw response from Groq
            financial_metrics: Financial metrics for context
            
        Returns:
            Structured CriticOutput
            
        Raises:
            RiskAssessmentError: If parsing fails
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
                "risk_level",
                "risk_score",
                "financial_health_score",
                "vulnerabilities",
                "alerts",
                "critical_issues",
                "recommendations",
                "confidence_score",
            ]
            
            for field in required_fields:
                if field not in data:
                    raise RiskAssessmentError(f"Missing field: {field}")
            
            # Convert risk_level string to enum
            try:
                risk_level = RiskLevel(data["risk_level"].lower())
            except (ValueError, AttributeError):
                risk_level = RiskLevel.MEDIUM
            
            # Create output
            output = CriticOutput(
                risk_level=risk_level,
                risk_score=float(data.get("risk_score", 50)),
                vulnerabilities=data.get("vulnerabilities", []),
                alerts=data.get("alerts", []),
                financial_health_score=float(data.get("financial_health_score", 50)),
                critical_issues=data.get("critical_issues", []),
                recommendations=data.get("recommendations", []),
                confidence_score=float(data.get("confidence_score", 0.75)),
                thinking_process=None,
            )
            
            return output
            
        except json.JSONDecodeError as e:
            raise RiskAssessmentError(f"Failed to parse JSON response: {str(e)}")
        except (ValueError, KeyError) as e:
            raise RiskAssessmentError(f"Invalid response structure: {str(e)}")
    
    def _calculate_risk_score(self, financial_metrics: FinancialMetrics) -> int:
        """
        Calculate risk score based on financial metrics.
        
        Args:
            financial_metrics: Financial metrics
            
        Returns:
            Risk score 0-100
        """
        score = 50  # Base neutral score
        
        # Penalize low savings rate
        savings_rate = financial_metrics.savings_rate or 0
        if savings_rate < 0.05:
            score += 25  # Critical
        elif savings_rate < 0.15:
            score += 15  # High
        elif savings_rate < 0.25:
            score += 5   # Medium
        
        # Check for very high expenses
        if financial_metrics.total_expenses > financial_metrics.total_income * 1.1:
            score += 20  # Overspending
        
        # Penalize high recurring expenses
        recurring_ratio = (
            financial_metrics.recurring_expenses / 
            financial_metrics.total_expenses 
            if financial_metrics.total_expenses > 0 
            else 0
        )
        if recurring_ratio > 0.8:
            score += 10  # High fixed costs
        
        return min(100, max(0, score))
