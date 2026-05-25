"""
Embedding Service - Generates vector embeddings for financial memories.
Uses OpenAI's embedding API for semantic understanding of financial data.
"""

import logging
from typing import List, Optional
import numpy as np
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generates and manages embeddings for financial memories."""
    
    def __init__(self):
        """Initialize embedding service with OpenAI client."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"  # Cost-effective, 1536 dimensions
        
    async def embed_memory(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for memory text.
        
        Args:
            text: Memory description to embed
            
        Returns:
            Vector embedding as list of floats, or None if embedding fails
        """
        try:
            if not text or len(text.strip()) == 0:
                logger.warning("Empty text provided for embedding")
                return None
                
            # Call OpenAI embedding API
            response = self.client.embeddings.create(
                input=text,
                model=self.model,
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding of dimension {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None
    
    async def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts (more efficient).
        
        Args:
            texts: List of memory descriptions
            
        Returns:
            List of embeddings
        """
        try:
            if not texts:
                return []
            
            # Filter empty texts
            valid_texts = [t for t in texts if t and len(t.strip()) > 0]
            if not valid_texts:
                return [None] * len(texts)
            
            # Call OpenAI batch embedding API
            response = self.client.embeddings.create(
                input=valid_texts,
                model=self.model,
            )
            
            embeddings = [data.embedding for data in response.data]
            logger.debug(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            return [None] * len(texts)
    
    def prepare_memory_text(
        self,
        title: str,
        description: str,
        memory_type: str,
        category: str,
        context_data: Optional[dict] = None
    ) -> str:
        """
        Prepare structured text for embedding that preserves financial semantics.
        
        Args:
            title: Memory title
            description: Memory description
            memory_type: Type of memory (spending_pattern, behavioral_trigger, etc.)
            category: Transaction category if applicable
            context_data: Additional context
            
        Returns:
            Formatted text optimized for embedding
        """
        parts = [
            f"Type: {memory_type}",
            f"Category: {category}",
            f"Title: {title}",
            f"Description: {description}",
        ]
        
        if context_data:
            if "tags" in context_data:
                parts.append(f"Tags: {', '.join(context_data['tags'])}")
            if "period" in context_data:
                parts.append(f"Period: {context_data['period']}")
            if "amount" in context_data:
                parts.append(f"Amount: {context_data['amount']}")
        
        return " | ".join(parts)
    
    def calculate_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First vector
            embedding2: Second vector
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Convert to numpy arrays
            v1 = np.array(embedding1)
            v2 = np.array(embedding2)
            
            # Calculate cosine similarity
            similarity = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            # Normalize to 0-1 range
            return (similarity + 1) / 2
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0


# Singleton instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
