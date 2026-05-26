"""
Memory Manager - Creates and manages financial memories.
Handles memory creation from transactions, consolidation, and lifecycle management.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.database import FinancialMemory, Transaction, BehavioralProfile
from .embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages financial memory creation, updates, and consolidation."""
    
    def __init__(self, db: Session):
        """Initialize memory manager with database session."""
        self.db = db
        self.embedding_service = get_embedding_service()
    
    async def create_memory(
        self,
        user_id: int,
        memory_type: str,
        title: str,
        description: str,
        category: Optional[str] = None,
        data: Optional[Dict] = None,
        transaction_ids: Optional[List[int]] = None,
        confidence_score: float = 0.8,
        impact_score: float = 0.5,
        behavioral_tags: Optional[List[str]] = None,
        contextual_data: Optional[Dict] = None,
        memory_date: Optional[datetime] = None,
    ) -> Optional[FinancialMemory]:
        """
        Create a new financial memory.
        
        Args:
            user_id: User ID
            memory_type: Type of memory (spending_pattern, behavioral_trigger, etc.)
            title: Memory title
            description: Memory description
            category: Memory category
            data: Structured data
            transaction_ids: Associated transaction IDs
            confidence_score: AI confidence (0-1)
            impact_score: Financial impact (0-1)
            behavioral_tags: Tags for behavioral analysis
            contextual_data: Additional context
            memory_date: When this memory occurred
            
        Returns:
            Created memory object or None if creation fails
        """
        try:
            # Generate embedding
            memory_text = self.embedding_service.prepare_memory_text(
                title,
                description,
                memory_type,
                category or "general",
                contextual_data
            )
            embedding = await self.embedding_service.embed_memory(memory_text)
            
            # Create memory object
            memory = FinancialMemory(
                user_id=user_id,
                memory_type=memory_type,
                memory_category=category or "general",
                title=title,
                description=description,
                data=data or {},
                transaction_ids=transaction_ids or [],
                embedding=embedding,
                confidence_score=confidence_score,
                impact_score=impact_score,
                behavioral_tags=behavioral_tags or [],
                contextual_data=contextual_data or {},
                memory_date=memory_date or datetime.utcnow(),
            )
            
            self.db.add(memory)
            self.db.commit()
            self.db.refresh(memory)
            
            logger.info(f"Created memory {memory.id} for user {user_id}")
            return memory
            
        except Exception as e:
            logger.error(f"Error creating memory: {str(e)}")
            self.db.rollback()
            return None
    
    async def create_memory_from_transaction(
        self,
        user_id: int,
        transaction: Transaction,
        behavioral_analysis: Optional[Dict] = None,
    ) -> Optional[FinancialMemory]:
        """
        Create memory from a transaction.
        
        Args:
            user_id: User ID
            transaction: Transaction object
            behavioral_analysis: Behavioral insights from transaction
            
        Returns:
            Created memory or None
        """
        try:
            # Determine memory type based on transaction characteristics
            memory_type = self._determine_memory_type(transaction)
            
            # Build description from transaction
            description = f"Transaction: {transaction.merchant} - {transaction.description or ''}"
            
            # Gather contextual data
            contextual_data = {
                "transaction_id": transaction.id,
                "merchant": transaction.merchant,
                "amount": float(transaction.amount),
                "category": transaction.category.category_type if transaction.category else "unknown",
            }
            
            if behavioral_analysis:
                contextual_data.update(behavioral_analysis)
            
            # Create memory
            memory = await self.create_memory(
                user_id=user_id,
                memory_type=memory_type,
                title=f"{transaction.merchant} - {transaction.transaction_type}",
                description=description,
                category=transaction.category.category_type if transaction.category else None,
                data={"transaction": {
                    "amount": float(transaction.amount),
                    "currency": transaction.currency.value,
                    "date": transaction.transaction_date.isoformat() if transaction.transaction_date else None,
                    "category": transaction.category.category_type if transaction.category else None,
                }},
                transaction_ids=[transaction.id],
                confidence_score=float(transaction.confidence_score or 0.8),
                impact_score=self._calculate_impact_score(transaction),
                contextual_data=contextual_data,
                memory_date=transaction.transaction_date,
            )
            
            return memory
            
        except Exception as e:
            logger.error(f"Error creating memory from transaction: {str(e)}")
            return None
    
    async def update_memory_confidence(
        self,
        memory_id: int,
        new_confidence: float,
    ) -> bool:
        """
        Update confidence score for a memory.
        
        Args:
            memory_id: Memory ID
            new_confidence: New confidence score (0-1)
            
        Returns:
            Success status
        """
        try:
            memory = self.db.query(FinancialMemory).get(memory_id)
            if not memory:
                return False
            
            memory.confidence_score = max(0, min(1, new_confidence))
            memory.updated_at = datetime.utcnow()
            self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating memory confidence: {str(e)}")
            self.db.rollback()
            return False
    
    async def validate_memory(self, memory_id: int) -> bool:
        """
        Mark memory as user-validated.
        
        Args:
            memory_id: Memory ID
            
        Returns:
            Success status
        """
        try:
            memory = self.db.query(FinancialMemory).get(memory_id)
            if not memory:
                return False
            
            memory.is_validated = True
            memory.confidence_score = min(1.0, memory.confidence_score + 0.1)  # Boost confidence
            memory.updated_at = datetime.utcnow()
            self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating memory: {str(e)}")
            self.db.rollback()
            return False
    
    def _determine_memory_type(self, transaction: Transaction) -> str:
        """Determine memory type based on transaction characteristics."""
        category = transaction.category.category_type if transaction.category else None
        
        if transaction.is_recurring:
            return "recurring_expense"
        
        if category == "subscriptions":
            return "subscription"
        
        if category == "salary":
            return "salary_cycle"
        
        if transaction.is_anomaly:
            return "behavioral_trigger"
        
        # Default to spending pattern
        return "spending_pattern"
    
    def _calculate_impact_score(self, transaction: Transaction) -> float:
        """
        Calculate financial impact score for transaction.
        Based on amount and category significance.
        """
        # Normalize amount to 0-1 score (max impact at $1000)
        amount_score = min(1.0, float(transaction.amount) / 1000)
        
        # Category weights
        category_weights = {
            "subscriptions": 0.9,
            "salary": 0.95,
            "investment": 0.8,
            "utilities": 0.7,
            "shopping": 0.6,
            "entertainment": 0.5,
            "food": 0.4,
            "transport": 0.5,
            "healthcare": 0.8,
            "transfer": 0.7,
            "other": 0.5,
        }
        
        category_weight = 0.5
        if transaction.category:
            category_weight = category_weights.get(
                transaction.category.category_type,
                0.5
            )
        
        # Type adjustment (income has higher impact)
        type_weight = 1.0 if transaction.transaction_type == "income" else 0.8
        
        impact = (amount_score * 0.5 + category_weight * 0.5) * type_weight
        return min(1.0, impact)
    
    async def consolidate_similar_memories(
        self,
        user_id: int,
        similarity_threshold: float = 0.85,
    ) -> int:
        """
        Consolidate similar memories to reduce redundancy.
        
        Args:
            user_id: User ID
            similarity_threshold: Threshold for similarity (0-1)
            
        Returns:
            Number of consolidated memories
        """
        try:
            memories = self.db.query(FinancialMemory).filter(
                FinancialMemory.user_id == user_id,
                FinancialMemory.embedding.isnot(None)
            ).all()
            
            consolidated_count = 0
            processed_ids = set()
            
            for i, mem1 in enumerate(memories):
                if mem1.id in processed_ids:
                    continue
                
                similar_group = [mem1]
                
                # Find similar memories
                for mem2 in memories[i+1:]:
                    if mem2.id in processed_ids:
                        continue
                    
                    if mem1.embedding and mem2.embedding:
                        similarity = self.embedding_service.calculate_similarity(
                            mem1.embedding,
                            mem2.embedding
                        )
                        
                        if similarity >= similarity_threshold:
                            similar_group.append(mem2)
                            processed_ids.add(mem2.id)
                
                # Consolidate if multiple similar memories found
                if len(similar_group) > 1:
                    await self._merge_memories(similar_group)
                    consolidated_count += len(similar_group) - 1
                    processed_ids.add(mem1.id)
            
            return consolidated_count
            
        except Exception as e:
            logger.error(f"Error consolidating memories: {str(e)}")
            return 0
    
    async def _merge_memories(self, memories: List[FinancialMemory]) -> None:
        """Merge multiple similar memories into one."""
        try:
            # Keep the most confident/validated memory
            primary = max(
                memories,
                key=lambda m: (m.is_validated, m.confidence_score, m.retrieval_count)
            )
            
            # Aggregate transaction IDs and tags
            all_transaction_ids = []
            all_tags = set()
            total_confidence = 0
            
            for memory in memories:
                all_transaction_ids.extend(memory.transaction_ids or [])
                all_tags.update(memory.behavioral_tags or [])
                total_confidence += memory.confidence_score
            
            # Update primary memory
            primary.transaction_ids = list(set(all_transaction_ids))
            primary.behavioral_tags = list(all_tags)
            primary.confidence_score = min(1.0, total_confidence / len(memories))
            
            # Delete other memories
            for memory in memories:
                if memory.id != primary.id:
                    self.db.delete(memory)
            
            self.db.commit()
            logger.info(f"Merged {len(memories)} memories into memory {primary.id}")
            
        except Exception as e:
            logger.error(f"Error merging memories: {str(e)}")
            self.db.rollback()
