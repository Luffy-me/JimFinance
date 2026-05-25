"""
Memory Engine API Endpoints.
Provides REST API for memory storage, retrieval, behavioral analysis, and insights.
"""

import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.security import get_current_user
from app.models.database import User, FinancialMemory
from app.schemas import UserResponse
from app.ml.memory_engine.memory_manager import MemoryManager
from app.ml.memory_engine.memory_retrieval import MemoryRetrievalService
from app.ml.memory_engine.behavioral_analyzer import BehavioralAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/memory", tags=["memory"])


# Pydantic schemas for API
from pydantic import BaseModel


class MemoryCreateRequest(BaseModel):
    """Request to create a new memory."""
    memory_type: str
    title: str
    description: str
    category: Optional[str] = None
    confidence_score: float = 0.8
    impact_score: float = 0.5
    behavioral_tags: Optional[List[str]] = None
    contextual_data: Optional[dict] = None


class MemoryResponse(BaseModel):
    """Memory response model."""
    id: int
    memory_type: str
    title: str
    description: str
    category: Optional[str]
    confidence: float
    impact: float
    retrieval_count: int
    date: Optional[str]
    tags: Optional[List[str]]
    explanation: Optional[str] = None


class MemorySearchRequest(BaseModel):
    """Request to search memories."""
    query: str
    limit: int = 5
    min_similarity: float = 0.5


class SpendingInsightsResponse(BaseModel):
    """Spending insights response."""
    insights: List[dict]
    analysis_period_days: int
    transaction_count: int
    total_spending: float


@router.post("/store", response_model=dict)
async def store_memory(
    request: MemoryCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Store a new financial memory.
    
    - **memory_type**: Type of memory (spending_pattern, behavioral_trigger, etc.)
    - **title**: Memory title
    - **description**: Memory description
    - **category**: Memory category
    - **confidence_score**: AI confidence in the memory (0-1)
    - **impact_score**: Financial impact (0-1)
    - **behavioral_tags**: Tags for behavioral tracking
    - **contextual_data**: Additional context
    """
    try:
        manager = MemoryManager(db)
        
        memory = await manager.create_memory(
            user_id=current_user.id,
            memory_type=request.memory_type,
            title=request.title,
            description=request.description,
            category=request.category,
            confidence_score=request.confidence_score,
            impact_score=request.impact_score,
            behavioral_tags=request.behavioral_tags,
            contextual_data=request.contextual_data,
        )
        
        if not memory:
            raise HTTPException(status_code=500, detail="Failed to create memory")
        
        return {
            "id": memory.id,
            "title": memory.title,
            "memory_type": memory.memory_type,
            "created_at": memory.created_at.isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error storing memory: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to store memory")


@router.post("/search", response_model=List[MemoryResponse])
async def search_memories(
    request: MemorySearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search for similar memories using semantic similarity.
    
    Returns memories ranked by composite score (similarity + confidence + recency + popularity).
    """
    try:
        retrieval_service = MemoryRetrievalService(db)
        
        results = await retrieval_service.search_similar_memories(
            user_id=current_user.id,
            query_text=request.query,
            limit=request.limit,
            min_similarity=request.min_similarity,
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error searching memories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search memories")


@router.get("/contextual", response_model=List[MemoryResponse])
async def get_contextual_memories(
    category: str = Query(..., description="Transaction category"),
    amount: float = Query(..., description="Transaction amount"),
    merchant: Optional[str] = Query(None, description="Merchant name"),
    limit: int = Query(3, le=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve memories contextual to a transaction.
    
    Used during transaction processing to provide relevant behavioral context.
    """
    try:
        retrieval_service = MemoryRetrievalService(db)
        
        memories = await retrieval_service.retrieve_contextual_memories(
            user_id=current_user.id,
            transaction_category=category,
            transaction_amount=amount,
            merchant=merchant,
            limit=limit,
        )
        
        return memories
        
    except Exception as e:
        logger.error(f"Error retrieving contextual memories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve memories")


@router.get("/behavioral-profile", response_model=dict)
async def get_behavioral_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get user's behavioral profile.
    
    Includes spending patterns, emotional spending tendency, risk tolerance, and priorities.
    """
    try:
        analyzer = BehavioralAnalyzer(db)
        
        # Get comprehensive behavioral analysis
        spending_patterns = await analyzer.analyze_spending_patterns(current_user.id)
        behavioral_triggers = await analyzer.detect_behavioral_triggers(current_user.id)
        seasonal_patterns = await analyzer.analyze_seasonal_patterns(current_user.id)
        risk_profile = await analyzer.calculate_risk_tolerance(current_user.id)
        
        return {
            "user_id": current_user.id,
            "spending_patterns": spending_patterns,
            "behavioral_triggers": behavioral_triggers,
            "seasonal_patterns": seasonal_patterns,
            "risk_profile": risk_profile,
        }
        
    except Exception as e:
        logger.error(f"Error retrieving behavioral profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")


@router.get("/insights", response_model=dict)
async def get_behavioral_insights(
    days_back: int = Query(90, ge=7, le=365, description="Days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get explainable behavioral insights.
    
    Returns insights like:
    - "You overspend during stressful periods"
    - "Food spending spikes during winter months"
    - "Post-paycheck spending is 40% higher than average"
    
    Each insight includes evidence and supporting transactions.
    """
    try:
        analyzer = BehavioralAnalyzer(db)
        
        # Analyze spending patterns
        spending_analysis = await analyzer.analyze_spending_patterns(
            current_user.id,
            days_back=days_back
        )
        
        # Detect behavioral triggers
        triggers = await analyzer.detect_behavioral_triggers(
            current_user.id,
            days_back=min(days_back, 60)
        )
        
        # Analyze seasonal patterns
        seasonal = await analyzer.analyze_seasonal_patterns(
            current_user.id,
            months_back=min(days_back // 30, 12)
        )
        
        # Compile insights
        insights = []
        
        # Add pattern insights
        if spending_analysis.get("insights"):
            insights.extend(spending_analysis["insights"])
        
        # Add trigger insights
        for trigger in triggers:
            insights.append({
                "type": "behavioral_trigger",
                "title": trigger["trigger"].replace("_", " ").title(),
                "description": trigger["description"],
                "confidence": trigger["confidence"],
                "evidence": trigger.get("evidence"),
                "examples": trigger.get("examples"),
            })
        
        # Add seasonal insights
        for pattern in seasonal.get("seasonal_patterns", []):
            if pattern["deviation"] != "normal":
                insights.append({
                    "type": "seasonal_pattern",
                    "title": f"{pattern['month']} Spending Pattern",
                    "description": f"Your {pattern['month']} spending is {pattern['deviation']} "
                                  f"compared to other months",
                    "evidence": f"Average: ${pattern['average_spending']:.2f}",
                    "z_score": pattern["z_score"],
                })
        
        return {
            "insights": insights,
            "analysis_period_days": days_back,
            "transaction_count": spending_analysis.get("transaction_count", 0),
            "total_spending": spending_analysis.get("total_spending", 0),
        }
        
    except Exception as e:
        logger.error(f"Error retrieving insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve insights")


@router.post("/validate/{memory_id}", response_model=dict)
async def validate_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark a memory as validated by user.
    
    User validation increases the confidence score and helps improve memory quality.
    """
    try:
        # Verify ownership
        memory = db.query(FinancialMemory).filter(
            FinancialMemory.id == memory_id,
            FinancialMemory.user_id == current_user.id
        ).first()
        
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        manager = MemoryManager(db)
        success = await manager.validate_memory(memory_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to validate memory")
        
        return {"status": "validated", "memory_id": memory_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating memory: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to validate memory")


@router.get("/{memory_id}", response_model=dict)
async def get_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific memory with full details.
    """
    try:
        memory = db.query(FinancialMemory).filter(
            FinancialMemory.id == memory_id,
            FinancialMemory.user_id == current_user.id
        ).first()
        
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return {
            "id": memory.id,
            "memory_type": memory.memory_type,
            "category": memory.memory_category,
            "title": memory.title,
            "description": memory.description,
            "confidence": float(memory.confidence_score),
            "impact": float(memory.impact_score),
            "tags": memory.behavioral_tags,
            "retrieved_count": memory.retrieval_count,
            "created_at": memory.created_at.isoformat(),
            "updated_at": memory.updated_at.isoformat() if memory.updated_at else None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving memory: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve memory")
