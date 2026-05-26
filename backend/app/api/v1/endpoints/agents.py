"""
Multi-agent reasoning API endpoints.
Provides REST interface for financial analysis via Strategist and Critic agents.
"""

import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.database import User
from app.api.v1.endpoints.users import get_current_user
from app.services.agent_service import AgentService
from app.schemas import (
    BaseResponse,
    PaginationParams,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize service
def get_agent_service() -> AgentService:
    """Get agent service instance."""
    return AgentService()


@router.post("/agents/analyze")
async def analyze_finances(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: AgentService = Depends(get_agent_service),
):
    """
    Run complete financial analysis using multi-agent system.
    
    Combines:
    - Strategist Agent (Gemini Pro): Strategic recommendations
    - Critic Agent (Groq): Risk assessment
    - Synthesis Engine: Unified recommendations
    
    Args:
        days: Days of history to analyze (default: 30)
        current_user: Authenticated user
        db: Database session
        service: Agent service
        
    Returns:
        Comprehensive financial analysis and recommendations
    """
    if days < 1 or days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days must be between 1 and 365",
        )
    
    try:
        logger.info(f"Starting financial analysis for user {current_user.id}")
        
        # Run analysis
        synthesis = await service.analyze_user_finances(
            user_id=current_user.id,
            db=db,
            days=days,
        )
        
        if not synthesis:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Analysis failed - please try again later",
            )
        
        # Save report to database
        report = service.save_report_to_database(
            user_id=current_user.id,
            synthesis=synthesis,
            db=db,
        )
        
        response_data = synthesis.to_dict()
        if report:
            response_data["report_id"] = report.id
        
        return {
            "success": True,
            "data": response_data,
        }
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Financial analysis failed",
        )


@router.get("/agents/strategy")
async def get_strategy_recommendations(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: AgentService = Depends(get_agent_service),
):
    """
    Get strategic recommendations from Strategist Agent.
    
    Args:
        days: Days of history to analyze
        current_user: Authenticated user
        db: Database session
        service: Agent service
        
    Returns:
        Strategic recommendations for financial optimization
    """
    if not service.strategist:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Strategist service not available",
        )
    
    try:
        from app.ml.agents.types import FinancialMetrics, TransactionContext
        
        # Collect data
        metrics = service._get_financial_metrics(current_user.id, db, days)
        context = service._get_transaction_context(current_user.id, db, days)
        
        if not metrics or not context:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient financial data",
            )
        
        # Run strategist
        result = await service.strategist.analyze(metrics, context, current_user.id)
        
        return {
            "success": True,
            "data": result,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Strategy error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Strategy generation failed",
        )


@router.get("/agents/risk-assessment")
async def get_risk_assessment(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: AgentService = Depends(get_agent_service),
):
    """
    Get risk assessment from Critic Agent.
    
    Args:
        days: Days of history to analyze
        current_user: Authenticated user
        db: Database session
        service: Agent service
        
    Returns:
        Risk assessment and vulnerability report
    """
    if not service.critic:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Critic service not available",
        )
    
    try:
        # Collect data
        metrics = service._get_financial_metrics(current_user.id, db, days)
        context = service._get_transaction_context(current_user.id, db, days)
        
        if not metrics or not context:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient financial data",
            )
        
        # Run critic
        result = await service.critic.analyze(metrics, context, current_user.id)
        
        return {
            "success": True,
            "data": result,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Risk assessment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Risk assessment failed",
        )


@router.get("/agents/health")
async def agent_health_check(
    service: AgentService = Depends(get_agent_service),
):
    """
    Check health status of all agents.
    
    Returns:
        Health status and statistics for each agent
    """
    stats = service.get_agent_stats()
    
    is_healthy = (
        stats.get("strategist", {}).get("status") != "not_initialized" and
        stats.get("critic", {}).get("status") != "not_initialized"
    )
    
    return {
        "success": True,
        "healthy": is_healthy,
        "agents": stats,
    }


@router.get("/agents/stats")
async def get_agent_statistics(
    current_user: User = Depends(get_current_user),
    service: AgentService = Depends(get_agent_service),
):
    """
    Get detailed statistics about agent performance.
    
    Returns:
        Performance metrics for all agents
    """
    stats = service.get_agent_stats()
    
    return {
        "success": True,
        "data": stats,
    }


@router.get("/agents/reports")
async def get_user_reports(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get historical agent analysis reports for user.
    
    Args:
        limit: Maximum number of reports (default: 10)
        offset: Pagination offset (default: 0)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of historical agent reports with pagination
    """
    from app.models.database import AgentReport
    
    if limit < 1 or limit > 100:
        limit = 10
    if offset < 0:
        offset = 0
    
    try:
        # Get total count
        total = db.query(AgentReport).filter(
            AgentReport.user_id == current_user.id
        ).count()
        
        # Get reports
        reports = db.query(AgentReport).filter(
            AgentReport.user_id == current_user.id
        ).order_by(
            AgentReport.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return {
            "success": True,
            "data": {
                "reports": [
                    {
                        "id": r.id,
                        "report_type": r.report_type,
                        "executive_summary": r.executive_summary,
                        "priority_level": r.priority_level,
                        "overall_confidence": r.overall_confidence,
                        "period_start": r.period_start.isoformat(),
                        "period_end": r.period_end.isoformat(),
                        "created_at": r.created_at.isoformat(),
                        "insights_count": len(r.insights),
                        "risk_assessments_count": len(r.risk_assessments),
                    }
                    for r in reports
                ],
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": total,
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to fetch reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reports",
        )


@router.get("/agents/reports/{report_id}")
async def get_report_details(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed information for a specific report.
    
    Args:
        report_id: Report ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Complete report with all insights and risk assessments
    """
    from app.models.database import AgentReport
    
    try:
        report = db.query(AgentReport).filter(
            AgentReport.id == report_id,
            AgentReport.user_id == current_user.id,
        ).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found",
            )
        
        return {
            "success": True,
            "data": {
                "id": report.id,
                "report_type": report.report_type,
                "executive_summary": report.executive_summary,
                "priority_level": report.priority_level,
                "overall_confidence": report.overall_confidence,
                "period_start": report.period_start.isoformat(),
                "period_end": report.period_end.isoformat(),
                "created_at": report.created_at.isoformat(),
                "is_reviewed": report.is_reviewed,
                "strategist_perspective": report.strategist_perspective,
                "critic_perspective": report.critic_perspective,
                "key_insights": report.key_insights,
                "action_items": report.action_items,
                "insights": [
                    {
                        "id": i.id,
                        "insight_type": i.insight_type,
                        "title": i.title,
                        "description": i.description,
                        "impact": i.impact,
                        "confidence": i.confidence,
                        "action": i.action,
                        "is_acknowledged": i.is_acknowledged,
                    }
                    for i in report.insights
                ],
                "risk_assessments": [
                    {
                        "id": r.id,
                        "risk_level": r.risk_level,
                        "risk_score": r.risk_score,
                        "financial_health_score": r.financial_health_score,
                        "title": r.title,
                        "description": r.description,
                        "vulnerabilities": r.vulnerabilities,
                        "alerts": r.alerts,
                        "recommendations": r.recommendations,
                        "is_acknowledged": r.is_acknowledged,
                    }
                    for r in report.risk_assessments
                ],
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch report details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch report details",
        )


@router.post("/agents/decide")
async def analyze_financial_decision(
    decision_name: str,
    description: str,
    purchase_price: float,
    monthly_payment: Optional[float] = None,
    months_to_pay: int = 1,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: AgentService = Depends(get_agent_service),
):
    """
    Analyze a specific financial decision with quantitative and AI reasoning.
    
    Provides:
    - Quantitative affordability analysis
    - Scenario analysis (conservative/balanced/aggressive)
    - Multi-agent debate (if agents available)
    - Final recommendation with confidence
    
    Example: Can I afford this iPhone for ₽120,000?
    
    Args:
        decision_name: Name of the decision (e.g., "iPhone Purchase")
        description: Detailed description
        purchase_price: Price of the item
        monthly_payment: Optional monthly payment for financed purchases
        months_to_pay: Financing period in months
        days: Days of financial history to analyze
        current_user: Authenticated user
        db: Database session
        service: Agent service
        
    Returns:
        Decision analysis with quantitative metrics, scenarios, and recommendation
    """
    if days < 1 or days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days must be between 1 and 365",
        )
    
    if purchase_price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Purchase price must be positive",
        )
    
    try:
        import uuid
        decision_id = str(uuid.uuid4())
        
        logger.info(f"Starting decision analysis for user {current_user.id}: {decision_name}")
        
        # Run analysis
        analysis = await service.analyze_financial_decision(
            user_id=current_user.id,
            decision_id=decision_id,
            decision_name=decision_name,
            decision_description=description,
            purchase_price=purchase_price,
            db=db,
            monthly_payment=monthly_payment,
            months_to_pay=months_to_pay,
            days=days,
        )
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Decision analysis failed",
            )
        
        return {
            "success": True,
            "data": analysis,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Decision analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Financial decision analysis failed",
        )


@router.post("/agents/scenarios")
async def analyze_scenarios(
    monthly_income: float,
    monthly_expenses: float,
    current_balance: float,
    days_of_data: int = 30,
    current_user: User = Depends(get_current_user),
):
    """
    Generate three-tier scenario analysis for current financial position.
    
    Provides:
    - Conservative scenario (worst case planning)
    - Balanced scenario (most likely case)
    - Aggressive scenario (best case upside)
    
    Args:
        monthly_income: Monthly gross income
        monthly_expenses: Monthly total expenses
        current_balance: Current account balance
        days_of_data: Days of financial data available
        current_user: Authenticated user
        
    Returns:
        Three scenarios with projections and recommendations
    """
    try:
        from app.ml.financial_reasoning.scenario_analyzer import ScenarioAnalyzer
        
        analyzer = ScenarioAnalyzer()
        scenarios = analyzer.generate_scenarios(
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            current_balance=current_balance,
            burn_rate_trend=0.0,  # Can be enhanced with historical data
        )
        
        return {
            "success": True,
            "data": {
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "current_balance": current_balance,
                "scenarios": [
                    {
                        "type": s.type.value,
                        "probability": s.probability,
                        "description": s.description,
                        "runway_months": s.projected_runway_months,
                        "stress_level": s.stress_level,
                        "recommendation": s.recommendation,
                        "monthly_savings_target": s.monthly_savings_target,
                        "action_items": s.action_items,
                    }
                    for s in scenarios
                ],
            },
        }
        
    except Exception as e:
        logger.error(f"Scenario analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Scenario analysis failed",
        )


@router.get("/agents/decision/{decision_id}/debate")
async def get_decision_debate(
    decision_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve full debate record for a financial decision.
    
    Shows:
    - Strategist's position and reasoning chain
    - Critic's position and reasoning chain
    - Synthesis and final recommendation
    - Quantitative analysis summary
    - Scenario comparisons
    
    Args:
        decision_id: Unique decision identifier
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Complete debate record with reasoning chains
    """
    try:
        from app.ml.reasoning_memory.memory_service import ReasoningMemoryService
        
        memory_service = ReasoningMemoryService()
        memory = memory_service.get_debate_record(db, current_user.id, decision_id)
        
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Debate record not found",
            )
        
        return {
            "success": True,
            "data": {
                "decision_id": memory.decision_id,
                "decision": {
                    "name": memory.decision_name,
                    "description": memory.decision_description,
                    "type": memory.decision_type,
                    "price": float(memory.purchase_price) if memory.purchase_price else None,
                    "monthly_payment": float(memory.monthly_payment) if memory.monthly_payment else None,
                },
                "financial_context": {
                    "monthly_income": float(memory.user_monthly_income),
                    "monthly_expenses": float(memory.user_monthly_expenses),
                    "current_balance": float(memory.user_current_balance),
                    "recurring_expenses": float(memory.user_recurring_expenses),
                },
                "debate": {
                    "strategist": {
                        "position": memory.strategist_position,
                        "reasoning_chain": memory.strategist_reasoning_chain,
                    },
                    "critic": {
                        "position": memory.critic_position,
                        "reasoning_chain": memory.critic_reasoning_chain,
                    },
                },
                "synthesis": memory.synthesis,
                "quantitative_analysis": memory.quantitative_analysis,
                "scenario_analysis": memory.scenario_analysis,
                "final_recommendation": memory.final_recommendation,
                "confidence_score": memory.confidence_score,
                "outcome": {
                    "actual_outcome": memory.actual_outcome,
                    "outcome_date": memory.outcome_date.isoformat() if memory.outcome_date else None,
                    "outcome_notes": memory.outcome_notes,
                },
                "created_at": memory.created_at.isoformat(),
            },
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving debate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve debate record",
        )


@router.get("/agents/decision/{decision_id}/reasoning-chain")
async def get_reasoning_chain(
    decision_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve detailed reasoning chain for a decision.
    
    Shows step-by-step thinking from both agents.
    
    Args:
        decision_id: Unique decision identifier
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Detailed reasoning chain formatted for visualization
    """
    try:
        from app.ml.reasoning_memory.memory_service import ReasoningMemoryService
        
        memory_service = ReasoningMemoryService()
        memory = memory_service.get_debate_record(db, current_user.id, decision_id)
        
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Debate record not found",
            )
        
        return {
            "success": True,
            "data": {
                "decision_id": decision_id,
                "decision_summary": {
                    "name": memory.decision_name,
                    "type": memory.decision_type,
                },
                "reasoning_chains": {
                    "strategist": {
                        "agent": "Strategist (Gemini Pro)",
                        "focus": "Opportunity analysis, long-term utility, wealth optimization",
                        "reasoning_steps": memory.strategist_reasoning_chain or [],
                        "conclusion": memory.strategist_position.get("recommendation") if memory.strategist_position else None,
                        "confidence": (
                            memory.strategist_position.get("confidence_score")
                            if memory.strategist_position else None
                        ),
                    },
                    "critic": {
                        "agent": "Critic (Groq)",
                        "focus": "Downside analysis, risk assessment, financial stress",
                        "reasoning_steps": memory.critic_reasoning_chain or [],
                        "conclusion": memory.critic_position.get("recommendation") if memory.critic_position else None,
                        "confidence": (
                            memory.critic_position.get("confidence_score")
                            if memory.critic_position else None
                        ),
                    },
                },
                "synthesis": {
                    "combined_reasoning": (
                        memory.synthesis.get("executive_summary")
                        if memory.synthesis else None
                    ),
                    "key_tensions": (
                        memory.synthesis.get("key_insights")
                        if memory.synthesis else []
                    ),
                    "final_recommendation": memory.final_recommendation,
                    "confidence": memory.confidence_score,
                },
            },
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving reasoning chain: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reasoning chain",
        )


@router.get("/agents/debates/similar")
async def find_similar_debates(
    decision_type: str = "purchase",
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Find similar past debates for comparison and learning.
    
    Args:
        decision_type: Type of decision to match (purchase, investment, etc.)
        limit: Maximum number of results
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of similar past debates with outcomes
    """
    try:
        from app.ml.reasoning_memory.memory_service import ReasoningMemoryService
        
        memory_service = ReasoningMemoryService()
        similar = memory_service.find_similar_debates(
            db=db,
            user_id=current_user.id,
            decision_type=decision_type,
            limit=limit,
        )
        
        return {
            "success": True,
            "data": {
                "decision_type": decision_type,
                "similar_debates": [
                    {
                        "decision_id": s.decision_id,
                        "decision_name": s.decision_name,
                        "decision_type": s.decision_type,
                        "price": float(s.purchase_price) if s.purchase_price else None,
                        "final_recommendation": s.final_recommendation,
                        "confidence": s.confidence_score,
                        "actual_outcome": s.actual_outcome,
                        "created_at": s.created_at.isoformat(),
                        "outcome_satisfaction": (
                            "positive" if s.actual_outcome in ["purchased", "satisfied"]
                            else "negative" if s.actual_outcome in ["not_purchased", "regretted"]
                            else None
                        ),
                    }
                    for s in similar
                ],
                "total_similar": len(similar),
            },
        }
        
    except Exception as e:
        logger.error(f"Error finding similar debates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find similar debates",
        )


@router.post("/agents/decision/{decision_id}/outcome")
async def record_decision_outcome(
    decision_id: str,
    outcome: str,
    notes: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Record the actual outcome of a decision.
    
    Used for learning and improving recommendations over time.
    
    Args:
        decision_id: Unique decision identifier
        outcome: "purchased", "not_purchased", "regretted", "satisfied"
        notes: Optional notes about the outcome
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success confirmation
    """
    try:
        from app.ml.reasoning_memory.memory_service import ReasoningMemoryService
        
        if outcome not in ["purchased", "not_purchased", "regretted", "satisfied"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid outcome. Must be one of: purchased, not_purchased, regretted, satisfied",
            )
        
        memory_service = ReasoningMemoryService()
        success = memory_service.record_outcome(
            db=db,
            user_id=current_user.id,
            decision_id=decision_id,
            outcome=outcome,
            notes=notes,
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Decision not found",
            )
        
        return {
            "success": True,
            "data": {
                "decision_id": decision_id,
                "outcome": outcome,
                "message": "Outcome recorded successfully",
            },
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording outcome: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record outcome",
        )


@router.get("/agents/decision-statistics")
async def get_decision_statistics(
    days_back: int = 365,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get statistics on past decisions and their outcomes.
    
    Shows:
    - Total decisions and outcomes
    - Recommendation accuracy
    - Decision types
    - Average confidence scores
    
    Args:
        days_back: Period to analyze (default: 1 year)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Decision statistics and insights
    """
    try:
        from app.ml.reasoning_memory.memory_service import ReasoningMemoryService
        
        memory_service = ReasoningMemoryService()
        stats = memory_service.get_decision_statistics(
            db=db,
            user_id=current_user.id,
            days_back=days_back,
        )
        
        # Calculate recommendation accuracy by type
        accuracy_by_type = {}
        for rec_type in ["recommended", "not_recommended", "neutral"]:
            accuracy = memory_service.get_recommendation_accuracy(
                db=db,
                user_id=current_user.id,
                recommendation=rec_type,
                days_back=days_back,
            )
            if accuracy.get("sample_size", 0) > 0:
                accuracy_by_type[rec_type] = accuracy
        
        return {
            "success": True,
            "data": {
                "period_days": days_back,
                "statistics": stats,
                "accuracy_by_recommendation": accuracy_by_type,
            },
        }
        
    except Exception as e:
        logger.error(f"Error getting decision statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics",
        )
