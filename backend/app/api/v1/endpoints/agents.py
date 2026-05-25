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
