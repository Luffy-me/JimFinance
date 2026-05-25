"""
Debate Orchestration Engine - Manages multi-agent debate on financial decisions.
Routes decisions to agents and tracks reasoning chains.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from app.ml.agents.strategist import StrategistAgent
from app.ml.agents.critic import CriticAgent
from app.ml.agents.types import FinancialMetrics, TransactionContext
from app.ml.financial_reasoning.decision_analyzer import DecisionAnalyzer

logger = logging.getLogger(__name__)


class DebatePhase(str, Enum):
    """Phases of financial decision debate."""
    ANALYSIS = "analysis"
    STRATEGIST_OPENING = "strategist_opening"
    CRITIC_OPENING = "critic_opening"
    STRATEGIST_COUNTER = "strategist_counter"
    CRITIC_COUNTER = "critic_counter"
    SYNTHESIS = "synthesis"
    COMPLETE = "complete"


@dataclass
class AgentPosition:
    """Single agent's position on a decision."""
    agent_name: str
    phase: DebatePhase
    timestamp: datetime
    analysis: Dict[str, Any]
    confidence: float
    reasoning_chain: List[str]  # Step-by-step reasoning


@dataclass
class DebateRecord:
    """Complete debate record for a decision."""
    decision_id: str
    user_id: int
    decision_context: Dict[str, Any]
    quantitative_analysis: Dict[str, Any]
    positions: List[AgentPosition]
    synthesis: Optional[Dict[str, Any]]
    final_recommendation: str
    created_at: datetime


class DebateOrchestrator:
    """
    Orchestrates multi-agent debate on financial decisions.
    Manages agent interactions and tracks reasoning chains.
    """
    
    def __init__(self):
        """Initialize orchestrator."""
        self.logger = logger
        self.strategist = None
        self.critic = None
        self.decision_analyzer = DecisionAnalyzer()
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize reasoning agents."""
        try:
            self.strategist = StrategistAgent()
            self.logger.info("Strategist agent initialized")
        except Exception as e:
            self.logger.warning(f"Could not initialize Strategist: {e}")
        
        try:
            self.critic = CriticAgent()
            self.logger.info("Critic agent initialized")
        except Exception as e:
            self.logger.warning(f"Could not initialize Critic: {e}")
    
    async def orchestrate_debate(
        self,
        decision_id: str,
        user_id: int,
        decision_name: str,
        decision_description: str,
        purchase_price: float,
        monthly_payment: Optional[float] = None,
        months_to_pay: int = 1,
        # Financial context
        financial_metrics: Optional[Dict[str, Any]] = None,
        transaction_context: Optional[Dict[str, Any]] = None,
        transactions: List[Dict] = None,
        user_financial_data: Optional[Dict[str, Any]] = None,
    ) -> DebateRecord:
        """
        Orchestrate full debate on a financial decision.
        
        Args:
            decision_id: Unique decision identifier
            user_id: User ID for context
            decision_name: Name of decision
            decision_description: Description of purchase/decision
            purchase_price: Price of item
            monthly_payment: Optional monthly payment for financing
            months_to_pay: Financing period
            financial_metrics: User's financial metrics
            transaction_context: Transaction context
            transactions: Transaction history
            user_financial_data: Additional user financial data
            
        Returns:
            Complete DebateRecord with all positions and synthesis
        """
        transactions = transactions or []
        user_financial_data = user_financial_data or {}
        
        self.logger.info(f"Starting debate orchestration for decision {decision_id}")
        
        # Step 1: Quantitative analysis
        quantitative_analysis = self.decision_analyzer.analyze_decision(
            decision_name=decision_name,
            decision_description=decision_description,
            purchase_price=purchase_price,
            monthly_payment=monthly_payment,
            months_to_pay=months_to_pay,
            monthly_income=user_financial_data.get("monthly_income", 0),
            monthly_expenses=user_financial_data.get("monthly_expenses", 0),
            current_balance=user_financial_data.get("current_balance", 0),
            recurring_expenses=user_financial_data.get("recurring_expenses", 0),
            transactions=transactions,
        )
        
        # Initialize debate record
        debate_record = DebateRecord(
            decision_id=decision_id,
            user_id=user_id,
            decision_context={
                "name": decision_name,
                "description": decision_description,
                "type": "financed" if monthly_payment else "lump_sum",
                "price": purchase_price,
                "monthly_payment": monthly_payment,
            },
            quantitative_analysis=quantitative_analysis,
            positions=[],
            synthesis=None,
            final_recommendation="pending",
            created_at=datetime.utcnow(),
        )
        
        # Step 2: Strategist opening position
        if self.strategist and financial_metrics and transaction_context:
            strategist_position = await self._get_strategist_position(
                decision_id=decision_id,
                quantitative_analysis=quantitative_analysis,
                financial_metrics=financial_metrics,
                transaction_context=transaction_context,
                user_id=user_id,
            )
            if strategist_position:
                debate_record.positions.append(strategist_position)
        
        # Step 3: Critic opening position
        if self.critic and financial_metrics and transaction_context:
            critic_position = await self._get_critic_position(
                decision_id=decision_id,
                quantitative_analysis=quantitative_analysis,
                financial_metrics=financial_metrics,
                transaction_context=transaction_context,
                user_id=user_id,
                strategist_position=debate_record.positions[-1] if debate_record.positions else None,
            )
            if critic_position:
                debate_record.positions.append(critic_position)
        
        # Step 4: Generate synthesis
        debate_record.synthesis = self._synthesize_debate(
            quantitative_analysis=quantitative_analysis,
            positions=debate_record.positions,
            decision_context=debate_record.decision_context,
        )
        
        # Step 5: Final recommendation
        debate_record.final_recommendation = self._determine_final_recommendation(
            quantitative_analysis=quantitative_analysis,
            positions=debate_record.positions,
            synthesis=debate_record.synthesis,
        )
        
        self.logger.info(
            f"Debate complete for {decision_id}: {debate_record.final_recommendation}"
        )
        
        return debate_record
    
    async def _get_strategist_position(
        self,
        decision_id: str,
        quantitative_analysis: Dict[str, Any],
        financial_metrics: Dict[str, Any],
        transaction_context: Dict[str, Any],
        user_id: int,
    ) -> Optional[AgentPosition]:
        """Get strategist's position on the decision."""
        try:
            if not self.strategist:
                return None
            
            # Build strategist prompt
            prompt = self._build_strategist_prompt(
                decision_id=decision_id,
                quantitative_analysis=quantitative_analysis,
                purchase_description=quantitative_analysis.get("decision", {}).get("description", ""),
            )
            
            # Get analysis
            analysis = await self.strategist.analyze(
                financial_metrics=self._dict_to_metrics(financial_metrics),
                transaction_context=self._dict_to_context(transaction_context),
                user_id=user_id,
            )
            
            reasoning_chain = self._extract_reasoning_chain(
                agent="strategist",
                prompt=prompt,
                analysis=analysis,
            )
            
            return AgentPosition(
                agent_name="Strategist",
                phase=DebatePhase.STRATEGIST_OPENING,
                timestamp=datetime.utcnow(),
                analysis=analysis,
                confidence=analysis.get("confidence_score", 0.75),
                reasoning_chain=reasoning_chain,
            )
            
        except Exception as e:
            self.logger.error(f"Strategist position failed: {e}")
            return None
    
    async def _get_critic_position(
        self,
        decision_id: str,
        quantitative_analysis: Dict[str, Any],
        financial_metrics: Dict[str, Any],
        transaction_context: Dict[str, Any],
        user_id: int,
        strategist_position: Optional[AgentPosition] = None,
    ) -> Optional[AgentPosition]:
        """Get critic's position on the decision."""
        try:
            if not self.critic:
                return None
            
            # Build critic prompt
            prompt = self._build_critic_prompt(
                decision_id=decision_id,
                quantitative_analysis=quantitative_analysis,
                strategist_position=strategist_position,
            )
            
            # Get analysis
            analysis = await self.critic.analyze(
                financial_metrics=self._dict_to_metrics(financial_metrics),
                transaction_context=self._dict_to_context(transaction_context),
                user_id=user_id,
            )
            
            reasoning_chain = self._extract_reasoning_chain(
                agent="critic",
                prompt=prompt,
                analysis=analysis,
            )
            
            return AgentPosition(
                agent_name="Critic",
                phase=DebatePhase.CRITIC_OPENING,
                timestamp=datetime.utcnow(),
                analysis=analysis,
                confidence=analysis.get("confidence_score", 0.75),
                reasoning_chain=reasoning_chain,
            )
            
        except Exception as e:
            self.logger.error(f"Critic position failed: {e}")
            return None
    
    def _synthesize_debate(
        self,
        quantitative_analysis: Dict[str, Any],
        positions: List[AgentPosition],
        decision_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Synthesize all positions into recommendation."""
        synthesis = {
            "timestamp": datetime.utcnow().isoformat(),
            "quantitative_score": self._score_quantitative_analysis(quantitative_analysis),
            "agent_consensus": self._measure_consensus(positions),
            "key_points": [],
            "concerns": [],
            "recommendations": [],
            "confidence": 0.75,
        }
        
        # Extract key points from quantitative analysis
        afford = quantitative_analysis.get("recommendation", {})
        if afford.get("level"):
            synthesis["recommendations"].append(afford.get("reasoning", ""))
        
        synthesis["concerns"] = afford.get("key_concerns", [])
        
        # Extract agent insights
        for position in positions:
            analysis = position.analysis
            
            if position.agent_name == "Strategist":
                if analysis.get("recommendations"):
                    synthesis["recommendations"].extend(
                        analysis.get("recommendations", [])[:2]  # Top 2
                    )
            
            elif position.agent_name == "Critic":
                if analysis.get("critical_issues"):
                    synthesis["concerns"].extend(
                        analysis.get("critical_issues", [])[:2]  # Top 2
                    )
        
        # Calculate final confidence
        synthesis["confidence"] = sum(
            p.confidence for p in positions
        ) / len(positions) if positions else 0.70
        
        return synthesis
    
    def _determine_final_recommendation(
        self,
        quantitative_analysis: Dict[str, Any],
        positions: List[AgentPosition],
        synthesis: Optional[Dict[str, Any]],
    ) -> str:
        """Determine final recommendation."""
        quant_rec = quantitative_analysis.get("recommendation", {}).get("level", "neutral")
        
        # Adjust based on agent positions
        critic_risk = None
        for pos in positions:
            if pos.agent_name == "Critic":
                critic_risk = pos.analysis.get("risk_level", "medium")
        
        if critic_risk == "critical":
            return "strongly_not_recommended"
        elif critic_risk == "high":
            return "not_recommended"
        else:
            return quant_rec
    
    @staticmethod
    def _build_strategist_prompt(
        decision_id: str,
        quantitative_analysis: Dict[str, Any],
        purchase_description: str,
    ) -> str:
        """Build prompt for strategist on this decision."""
        return f"""
        Analyze this financial decision from a STRATEGIC OPPORTUNITY perspective:
        
        Decision: {decision_id}
        Description: {purchase_description}
        
        Quantitative Analysis:
        - Purchase Price: ${quantitative_analysis.get('decision', {}).get('price', 0):,.2f}
        - Payment Type: {quantitative_analysis.get('decision', {}).get('type', 'unknown')}
        
        Scenario Analysis:
        {json.dumps(quantitative_analysis.get('scenario_analysis', []), indent=2)}
        
        Question: What are the STRATEGIC OPPORTUNITIES and LONG-TERM BENEFITS of this purchase?
        Consider:
        1. Opportunity cost vs alternatives
        2. Long-term value creation
        3. Wealth optimization potential
        4. Quality of life improvements
        5. Financial goal alignment
        """
    
    @staticmethod
    def _build_critic_prompt(
        decision_id: str,
        quantitative_analysis: Dict[str, Any],
        strategist_position: Optional[AgentPosition] = None,
    ) -> str:
        """Build prompt for critic on this decision."""
        strategist_summary = ""
        if strategist_position:
            strategist_summary = f"""
        
        Strategist's Position:
        - Confidence: {strategist_position.confidence:.0%}
        - Key Points: {', '.join(strategist_position.reasoning_chain[:2])}
        """
        
        return f"""
        Analyze this financial decision from a RISK and VULNERABILITY perspective:
        
        Decision: {decision_id}
        
        Quantitative Analysis:
        {json.dumps(quantitative_analysis.get('affordability', {}), indent=2)}
        
        Financial Impacts:
        {json.dumps(quantitative_analysis.get('financial_impacts', []), indent=2)}{strategist_summary}
        
        Question: What are the CRITICAL RISKS and DOWNSIDE SCENARIOS to consider?
        Focus on:
        1. Runway reduction and financial stress
        2. Emergency fund depletion
        3. Debt-to-income ratio impact
        4. Income loss scenarios
        5. Behavioral spending pattern changes
        """
    
    @staticmethod
    def _measure_consensus(positions: List[AgentPosition]) -> float:
        """Measure consensus between agents (0-1)."""
        if len(positions) < 2:
            return 0.5
        
        # Average confidence as proxy for consensus
        avg_confidence = sum(p.confidence for p in positions) / len(positions)
        
        return min(1.0, avg_confidence)
    
    @staticmethod
    def _score_quantitative_analysis(analysis: Dict[str, Any]) -> float:
        """Score the quantitative analysis (0-100)."""
        rec = analysis.get("recommendation", {}).get("level", "neutral")
        
        scores = {
            "highly_recommended": 85,
            "recommended": 70,
            "neutral": 50,
            "not_recommended": 30,
            "strongly_not_recommended": 15,
        }
        
        return scores.get(rec, 50)
    
    @staticmethod
    def _extract_reasoning_chain(
        agent: str,
        prompt: str,
        analysis: Dict[str, Any],
    ) -> List[str]:
        """Extract reasoning chain from agent analysis."""
        chain = []
        
        if agent == "strategist":
            recommendations = analysis.get("recommendations", [])
            chain = recommendations[:3] if recommendations else []
        
        elif agent == "critic":
            issues = analysis.get("critical_issues", [])
            chain = issues[:3] if issues else []
        
        return chain
    
    @staticmethod
    def _dict_to_metrics(data: Dict[str, Any]) -> "FinancialMetrics":
        """Convert dict to FinancialMetrics."""
        from app.ml.agents.types import FinancialMetrics
        
        return FinancialMetrics(
            total_income=float(data.get("total_income", 0)),
            total_expenses=float(data.get("total_expenses", 0)),
            savings_rate=float(data.get("savings_rate", 0)),
            average_monthly_expense=float(data.get("average_monthly_expense", 0)),
            expense_categories=data.get("expense_categories", {}),
            account_balances=data.get("account_balances", {}),
            recurring_expenses=float(data.get("recurring_expenses", 0)),
            average_transaction_size=float(data.get("average_transaction_size", 0)),
            transaction_count=int(data.get("transaction_count", 0)),
        )
    
    @staticmethod
    def _dict_to_context(data: Dict[str, Any]) -> "TransactionContext":
        """Convert dict to TransactionContext."""
        from app.ml.agents.types import TransactionContext
        
        return TransactionContext(
            recent_transactions=data.get("recent_transactions", []),
            spending_trends=data.get("spending_trends", {}),
            category_breakdown=data.get("category_breakdown", {}),
            recurring_patterns=data.get("recurring_patterns", []),
            anomalies_detected=data.get("anomalies_detected", []),
            time_period=data.get("time_period", "30_days"),
        )
    
    def to_dict(self, record: DebateRecord) -> Dict[str, Any]:
        """Convert debate record to dictionary."""
        return {
            "decision_id": record.decision_id,
            "user_id": record.user_id,
            "decision_context": record.decision_context,
            "quantitative_analysis": record.quantitative_analysis,
            "positions": [
                {
                    "agent": pos.agent_name,
                    "phase": pos.phase.value,
                    "timestamp": pos.timestamp.isoformat(),
                    "confidence": pos.confidence,
                    "reasoning": pos.reasoning_chain,
                    "analysis": pos.analysis,
                }
                for pos in record.positions
            ],
            "synthesis": record.synthesis,
            "final_recommendation": record.final_recommendation,
            "created_at": record.created_at.isoformat(),
        }
