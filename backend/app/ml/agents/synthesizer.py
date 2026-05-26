"""
Synthesis Engine for multi-agent reasoning.
Combines outputs from Strategist and Critic agents.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from app.ml.agents.types import (
    StrategistOutput,
    CriticOutput,
    SynthesisOutput,
    FinancialInsight,
    InsightType,
    SynthesisError,
    RiskLevel,
)

logger = logging.getLogger(__name__)


class SynthesisEngine:
    """
    Combines and synthesizes outputs from multiple agents.
    Creates unified recommendations and insights.
    """
    
    def __init__(self):
        """Initialize Synthesis Engine."""
        self.logger = logging.getLogger(f"{__name__}.SynthesisEngine")
    
    def synthesize(
        self,
        strategist_output: StrategistOutput,
        critic_output: CriticOutput,
    ) -> SynthesisOutput:
        """
        Synthesize agent outputs into comprehensive report.
        
        Args:
            strategist_output: Output from Strategist Agent
            critic_output: Output from Critic Agent
            
        Returns:
            Synthesized comprehensive output
            
        Raises:
            SynthesisError: If synthesis fails
        """
        try:
            # Generate executive summary
            executive_summary = self._generate_executive_summary(
                strategist_output, critic_output
            )
            
            # Extract key insights
            key_insights = self._extract_key_insights(
                strategist_output, critic_output
            )
            
            # Generate action items
            action_items = self._generate_action_items(
                strategist_output, critic_output
            )
            
            # Determine priority
            priority_level = self._determine_priority(critic_output)
            
            # Calculate overall confidence
            overall_confidence = (
                strategist_output.confidence_score + 
                critic_output.confidence_score
            ) / 2
            
            # Create synthesis output
            output = SynthesisOutput(
                executive_summary=executive_summary,
                key_insights=key_insights,
                action_items=action_items,
                priority_level=priority_level,
                strategist_perspective={
                    "recommendations": strategist_output.recommendations,
                    "budget_suggestions": strategist_output.budget_suggestions,
                    "confidence_score": strategist_output.confidence_score,
                },
                critic_perspective={
                    "risk_level": critic_output.risk_level.value,
                    "risk_score": critic_output.risk_score,
                    "critical_issues": critic_output.critical_issues,
                    "confidence_score": critic_output.confidence_score,
                },
                overall_confidence=overall_confidence,
                generated_at=datetime.utcnow(),
            )
            
            self.logger.info("Synthesis completed successfully")
            return output
            
        except Exception as e:
            error_msg = f"Synthesis failed: {str(e)}"
            self.logger.error(error_msg)
            raise SynthesisError(error_msg)
    
    def _generate_executive_summary(
        self,
        strategist_output: StrategistOutput,
        critic_output: CriticOutput,
    ) -> str:
        """
        Generate executive summary combining both perspectives.
        
        Args:
            strategist_output: Strategist output
            critic_output: Critic output
            
        Returns:
            Executive summary text
        """
        # Analyze confidence levels
        avg_confidence = (
            strategist_output.confidence_score + 
            critic_output.confidence_score
        ) / 2
        
        confidence_level = "high" if avg_confidence > 0.75 else (
            "medium" if avg_confidence > 0.5 else "low"
        )
        
        # Build summary based on risk level
        if critic_output.risk_level == RiskLevel.CRITICAL:
            mood = "Your financial situation requires immediate attention."
        elif critic_output.risk_level == RiskLevel.HIGH:
            mood = "Your financial health has several areas of concern."
        elif critic_output.risk_level == RiskLevel.MEDIUM:
            mood = "Your finances are generally stable with room for improvement."
        else:
            mood = "Your financial health is strong."
        
        # Get top opportunities
        top_opportunity = ""
        if strategist_output.savings_opportunities:
            top_opp = strategist_output.savings_opportunities[0]
            top_opportunity = f" The biggest opportunity is in {top_opp.get('area', 'unknown')}, where you could save ${top_opp.get('monthly_savings', 0):.2f}/month."
        
        summary = f"""{mood}

After analyzing your financial data with {confidence_level} confidence:
- Your risk level is {critic_output.risk_level.value.upper()}
- Your financial health score is {critic_output.financial_health_score:.0f}/100
- Your savings rate is {strategist_output.spending_analysis.get('savings_rate', 'unknown')}{top_opportunity}

This report combines strategic opportunities with critical risk assessments to provide actionable guidance."""
        
        return summary.strip()
    
    def _extract_key_insights(
        self,
        strategist_output: StrategistOutput,
        critic_output: CriticOutput,
    ) -> List[Dict[str, Any]]:
        """
        Extract key insights from both agents.
        
        Args:
            strategist_output: Strategist output
            critic_output: Critic output
            
        Returns:
            List of key insights
        """
        insights = []
        
        # Extract from strategist
        if strategist_output.savings_opportunities:
            top_opportunity = strategist_output.savings_opportunities[0]
            insights.append({
                "title": "Top Savings Opportunity",
                "description": f"Reduce {top_opportunity.get('area')} expenses from ${top_opportunity.get('current'):.2f} to ${top_opportunity.get('suggested'):.2f}",
                "potential_savings": top_opportunity.get("monthly_savings", 0),
                "source": "strategist",
            })
        
        # Extract critical issues from critic
        if critic_output.critical_issues:
            for issue in critic_output.critical_issues[:2]:  # Top 2
                insights.append({
                    "title": "Critical Issue",
                    "description": issue,
                    "risk_level": critic_output.risk_level.value,
                    "source": "critic",
                })
        
        # Add alerts
        if critic_output.alerts:
            for alert in critic_output.alerts[:2]:  # Top 2
                insights.append({
                    "title": "Alert",
                    "description": alert.get("message", ""),
                    "action": alert.get("recommended_action", ""),
                    "source": "critic",
                })
        
        # Add budget suggestions
        if strategist_output.budget_suggestions:
            highest_budget = max(
                strategist_output.budget_suggestions.items(),
                key=lambda x: x[1],
                default=None,
            )
            if highest_budget:
                insights.append({
                    "title": "Budget Recommendation",
                    "description": f"Allocate ${highest_budget[1]:.2f}/month to {highest_budget[0]}",
                    "source": "strategist",
                })
        
        return insights
    
    def _generate_action_items(
        self,
        strategist_output: StrategistOutput,
        critic_output: CriticOutput,
    ) -> List[Dict[str, Any]]:
        """
        Generate prioritized action items.
        
        Args:
            strategist_output: Strategist output
            critic_output: Critic output
            
        Returns:
            List of action items
        """
        action_items = []
        priority = 1
        
        # Critical actions from critic
        if critic_output.critical_issues:
            for issue in critic_output.critical_issues:
                action_items.append({
                    "priority": priority,
                    "action": f"Address: {issue}",
                    "type": "critical",
                    "timeline": "Immediate",
                })
                priority += 1
        
        # Recommendations from critic
        if critic_output.recommendations:
            for rec in critic_output.recommendations[:2]:
                action_items.append({
                    "priority": priority,
                    "action": rec,
                    "type": "defensive",
                    "timeline": "This week",
                })
                priority += 1
        
        # Strategic recommendations
        if strategist_output.recommendations:
            for rec in strategist_output.recommendations[:2]:
                action_items.append({
                    "priority": priority,
                    "action": rec,
                    "type": "strategic",
                    "timeline": "This month",
                })
                priority += 1
        
        return action_items
    
    def _determine_priority(self, critic_output: CriticOutput) -> str:
        """
        Determine overall priority level.
        
        Args:
            critic_output: Critic output
            
        Returns:
            Priority level string
        """
        if critic_output.risk_level == RiskLevel.CRITICAL:
            return "critical"
        elif critic_output.risk_level == RiskLevel.HIGH:
            return "high"
        elif critic_output.risk_level == RiskLevel.MEDIUM:
            return "medium"
        else:
            return "low"
    
    def generate_insights(
        self,
        strategist_output: StrategistOutput,
        critic_output: CriticOutput,
    ) -> List[FinancialInsight]:
        """
        Generate individual financial insights.
        
        Args:
            strategist_output: Strategist output
            critic_output: Critic output
            
        Returns:
            List of individual insights
        """
        insights = []
        
        # Savings opportunities
        for opp in strategist_output.savings_opportunities:
            insights.append(
                FinancialInsight(
                    type=InsightType.SAVINGS_OPPORTUNITY,
                    title=f"Save on {opp.get('area', 'unknown')}",
                    description=opp.get("reasoning", ""),
                    impact="positive",
                    confidence=strategist_output.confidence_score,
                    action=f"Reduce to ${opp.get('suggested', 0):.2f}",
                    metric_value=opp.get("monthly_savings", 0),
                )
            )
        
        # Risk alerts
        for alert in critic_output.alerts:
            insights.append(
                FinancialInsight(
                    type=InsightType.RISK_ALERT,
                    title=alert.get("type", "Risk"),
                    description=alert.get("message", ""),
                    impact="negative",
                    confidence=critic_output.confidence_score,
                    action=alert.get("recommended_action", ""),
                )
            )
        
        # Goal suggestions
        for goal in strategist_output.goals_suggestions:
            insights.append(
                FinancialInsight(
                    type=InsightType.GOAL_SUGGESTION,
                    title=goal.get("goal", "Financial goal"),
                    description=goal.get("reasoning", ""),
                    impact="positive",
                    confidence=strategist_output.confidence_score,
                    action=f"Save ${goal.get('monthly_amount', 0):.2f}/month",
                    metric_value=goal.get("monthly_amount", 0),
                )
            )
        
        return insights
