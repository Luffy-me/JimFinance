"""
Memory Retrieval Service - Retrieves and scores financial memories.
Implements vector similarity search with contextual ranking and explainability.
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models.database import FinancialMemory, MemoryInteraction, Transaction
from .embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


class MemoryRetrievalService:
    """Retrieves and scores financial memories with semantic and contextual ranking."""
    
    def __init__(self, db: Session):
        """Initialize retrieval service with database session."""
        self.db = db
        self.embedding_service = get_embedding_service()
    
    async def search_similar_memories(
        self,
        user_id: int,
        query_text: str,
        limit: int = 5,
        min_similarity: float = 0.5,
        memory_types: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Search for similar memories using semantic similarity.
        
        Args:
            user_id: User ID
            query_text: Text to search for
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold
            memory_types: Filter by memory types
            
        Returns:
            List of similar memories with scores and explanations
        """
        try:
            # Generate embedding for query
            query_embedding = await self.embedding_service.embed_memory(query_text)
            if query_embedding is None:
                logger.warning(f"Failed to embed query text")
                return []
            
            # Get user memories
            query = self.db.query(FinancialMemory).filter(
                FinancialMemory.user_id == user_id,
                FinancialMemory.embedding.isnot(None)
            )
            
            if memory_types:
                query = query.filter(FinancialMemory.memory_type.in_(memory_types))
            
            memories = query.all()
            
            # Calculate similarity scores
            scored_memories = []
            for memory in memories:
                if memory.embedding:
                    similarity = self.embedding_service.calculate_similarity(
                        query_embedding,
                        memory.embedding
                    )
                    
                    if similarity >= min_similarity:
                        score = self._calculate_composite_score(
                            memory,
                            similarity,
                            query_text
                        )
                        scored_memories.append({
                            "id": memory.id,
                            "title": memory.title,
                            "description": memory.description,
                            "memory_type": memory.memory_type,
                            "category": memory.memory_category,
                            "similarity_score": float(similarity),
                            "composite_score": float(score),
                            "confidence": float(memory.confidence_score),
                            "impact": float(memory.impact_score),
                            "retrieval_count": memory.retrieval_count,
                            "date": memory.memory_date.isoformat() if memory.memory_date else None,
                            "explanation": self._generate_explanation(memory, similarity),
                        })
            
            # Sort by composite score
            scored_memories.sort(key=lambda x: x["composite_score"], reverse=True)
            
            # Record interaction for each retrieved memory
            for mem in scored_memories[:limit]:
                await self._record_interaction(user_id, mem["id"], mem["composite_score"])
            
            return scored_memories[:limit]
            
        except Exception as e:
            logger.error(f"Error searching similar memories: {str(e)}")
            return []
    
    async def retrieve_contextual_memories(
        self,
        user_id: int,
        transaction_category: str,
        transaction_amount: float,
        merchant: Optional[str] = None,
        limit: int = 3,
    ) -> List[Dict]:
        """
        Retrieve memories contextual to current transaction.
        
        Args:
            user_id: User ID
            transaction_category: Transaction category
            transaction_amount: Transaction amount
            merchant: Merchant name
            limit: Maximum number of results
            
        Returns:
            Relevant memories for current context
        """
        try:
            # Build context query text
            context_parts = [f"category: {transaction_category}", f"amount: {transaction_amount}"]
            if merchant:
                context_parts.append(f"merchant: {merchant}")
            context_text = " ".join(context_parts)
            
            # Search for similar memories
            similar_memories = await self.search_similar_memories(
                user_id,
                context_text,
                limit=limit,
                min_similarity=0.4,  # Lower threshold for contextual matching
                memory_types=[
                    "spending_pattern",
                    "behavioral_trigger",
                    "emotional_spending",
                    "seasonal_spending"
                ]
            )
            
            # Add contextual scoring
            for memory in similar_memories:
                memory["contextual_relevance"] = self._score_contextual_relevance(
                    memory,
                    transaction_category,
                    transaction_amount
                )
            
            # Re-sort by contextual relevance
            similar_memories.sort(key=lambda x: x.get("contextual_relevance", 0), reverse=True)
            
            return similar_memories
            
        except Exception as e:
            logger.error(f"Error retrieving contextual memories: {str(e)}")
            return []
    
    async def retrieve_behavioral_memories(
        self,
        user_id: int,
        days_back: int = 30,
        limit: int = 10,
    ) -> List[Dict]:
        """
        Retrieve behavioral memories from recent period.
        
        Args:
            user_id: User ID
            days_back: Days to look back
            limit: Maximum number of results
            
        Returns:
            Recent behavioral memories
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            memories = self.db.query(FinancialMemory).filter(
                and_(
                    FinancialMemory.user_id == user_id,
                    FinancialMemory.memory_type.in_([
                        "behavioral_trigger",
                        "emotional_spending",
                        "seasonal_spending"
                    ]),
                    FinancialMemory.created_at >= cutoff_date
                )
            ).order_by(
                desc(FinancialMemory.created_at)
            ).limit(limit).all()
            
            return [self._memory_to_dict(m) for m in memories]
            
        except Exception as e:
            logger.error(f"Error retrieving behavioral memories: {str(e)}")
            return []
    
    def _calculate_composite_score(
        self,
        memory: FinancialMemory,
        similarity_score: float,
        query_text: str = ""
    ) -> float:
        """
        Calculate composite score for memory retrieval ranking.
        Formula: similarity (40%) + confidence (25%) + recency (20%) + popularity (15%)
        """
        # Recency score (decay over time, max 30 days)
        days_old = (datetime.utcnow() - memory.created_at).days if memory.created_at else 0
        recency_score = max(0, 1 - (days_old / 30))
        
        # Popularity score (based on retrieval count)
        popularity_score = min(1.0, memory.retrieval_count / 100)
        
        # Combine scores
        composite = (
            similarity_score * 0.40 +
            memory.confidence_score * 0.25 +
            recency_score * 0.20 +
            popularity_score * 0.15
        )
        
        return composite
    
    def _score_contextual_relevance(
        self,
        memory: Dict,
        transaction_category: str,
        transaction_amount: float,
    ) -> float:
        """Score how relevant memory is to current transaction context."""
        score = memory.get("similarity_score", 0)
        
        # Boost if memory is about same category
        if memory.get("category") == transaction_category:
            score *= 1.3
        
        # Adjust based on amount similarity
        if memory.get("impact"):
            amount_relevance = 1 - abs(memory["impact"] - (transaction_amount / 1000)) / 1000
            score *= (1 + amount_relevance * 0.2)
        
        return min(1.0, score)
    
    def _generate_explanation(self, memory: FinancialMemory, similarity: float) -> str:
        """Generate human-readable explanation for memory retrieval."""
        if similarity > 0.8:
            match_quality = "highly relevant"
        elif similarity > 0.6:
            match_quality = "relevant"
        else:
            match_quality = "somewhat relevant"
        
        explanation = f"This memory is {match_quality} (similarity: {similarity:.1%}). "
        
        if memory.behavioral_tags:
            explanation += f"Tags: {', '.join(memory.behavioral_tags)}. "
        
        if memory.impact_score > 0.7:
            explanation += "This has high financial impact. "
        
        return explanation
    
    def _memory_to_dict(self, memory: FinancialMemory) -> Dict:
        """Convert memory object to dictionary."""
        return {
            "id": memory.id,
            "title": memory.title,
            "description": memory.description,
            "memory_type": memory.memory_type,
            "category": memory.memory_category,
            "confidence": float(memory.confidence_score),
            "impact": float(memory.impact_score),
            "retrieval_count": memory.retrieval_count,
            "date": memory.memory_date.isoformat() if memory.memory_date else None,
            "tags": memory.behavioral_tags,
        }
    
    async def _record_interaction(
        self,
        user_id: int,
        memory_id: int,
        relevance_score: float,
    ) -> None:
        """Record memory interaction for analytics and ranking."""
        try:
            interaction = MemoryInteraction(
                memory_id=memory_id,
                user_id=user_id,
                context="search",
                retrieval_score=relevance_score,
            )
            self.db.add(interaction)
            
            # Update retrieval count
            memory = self.db.query(FinancialMemory).get(memory_id)
            if memory:
                memory.retrieval_count += 1
                memory.last_accessed_at = datetime.utcnow()
            
            self.db.commit()
        except Exception as e:
            logger.error(f"Error recording interaction: {str(e)}")
            self.db.rollback()
