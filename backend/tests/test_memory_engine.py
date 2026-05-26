"""
Tests for Financial Memory Engine.
Tests embedding, retrieval, behavioral analysis, and memory management.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.database import (
    User, Transaction, Category, Account, FinancialMemory,
    MemoryInteraction, BehavioralProfile, TransactionCategory,
    TransactionType, AccountType, Currency
)
from app.ml.memory_engine.embedding_service import EmbeddingService
from app.ml.memory_engine.memory_manager import MemoryManager
from app.ml.memory_engine.memory_retrieval import MemoryRetrievalService
from app.ml.memory_engine.behavioral_analyzer import BehavioralAnalyzer


@pytest.fixture
def db_session():
    """Create test database session."""
    from app.db.base import SessionLocal
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_user(db_session):
    """Create test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        full_name="Test User",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_account(db_session, test_user):
    """Create test account."""
    account = Account(
        user_id=test_user.id,
        name="Test Account",
        account_type=AccountType.CHECKING,
        currency=Currency.USD,
        balance=5000.00,
        is_active=True
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account


@pytest.fixture
def test_category(db_session, test_user):
    """Create test category."""
    category = Category(
        user_id=test_user.id,
        name="Food",
        category_type=TransactionCategory.FOOD,
        color="#FF5733"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_transaction(db_session, test_user, test_account, test_category):
    """Create test transaction."""
    transaction = Transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        category_id=test_category.id,
        amount=50.00,
        currency=Currency.USD,
        merchant="Test Restaurant",
        description="Lunch",
        transaction_type=TransactionType.EXPENSE,
        transaction_date=datetime.utcnow(),
        confidence_score=0.95,
        source_type="manual"
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)
    return transaction


class TestEmbeddingService:
    """Test embedding service."""
    
    @pytest.mark.asyncio
    async def test_embed_memory(self):
        """Test memory embedding generation."""
        service = EmbeddingService()
        text = "You overspent on food during winter months"
        embedding = await service.embed_memory(text)
        
        assert embedding is not None
        assert len(embedding) == 1536  # OpenAI embedding dimension
        assert all(isinstance(x, float) for x in embedding)
    
    @pytest.mark.asyncio
    async def test_embed_batch(self):
        """Test batch embedding generation."""
        service = EmbeddingService()
        texts = [
            "You overspent on food",
            "Weekend spending is higher",
            "Post-paycheck purchases",
        ]
        embeddings = await service.embed_batch(texts)
        
        assert len(embeddings) == 3
        assert all(e is not None for e in embeddings)
        assert all(len(e) == 1536 for e in embeddings)
    
    def test_prepare_memory_text(self):
        """Test memory text preparation."""
        service = EmbeddingService()
        text = service.prepare_memory_text(
            title="Weekend Spending",
            description="Spend more on weekends",
            memory_type="behavioral_trigger",
            category="shopping",
            context_data={"tags": ["weekend", "impulse"], "amount": 200}
        )
        
        assert "behavioral_trigger" in text
        assert "Weekend Spending" in text
        assert "shopping" in text
        assert "weekend" in text
    
    def test_calculate_similarity(self):
        """Test similarity calculation."""
        service = EmbeddingService()
        v1 = [0.1, 0.2, 0.3] * 512  # Same dimension as embedding
        v2 = [0.1, 0.2, 0.3] * 512  # Identical vector
        
        similarity = service.calculate_similarity(v1, v2)
        assert similarity > 0.99  # Should be very similar


class TestMemoryManager:
    """Test memory management."""
    
    @pytest.mark.asyncio
    async def test_create_memory(self, db_session, test_user):
        """Test memory creation."""
        manager = MemoryManager(db_session)
        
        memory = await manager.create_memory(
            user_id=test_user.id,
            memory_type="spending_pattern",
            title="Weekend Spending",
            description="You spend more on weekends",
            category="shopping",
            confidence_score=0.85,
            impact_score=0.7,
            behavioral_tags=["weekend", "impulse"],
        )
        
        assert memory is not None
        assert memory.title == "Weekend Spending"
        assert memory.user_id == test_user.id
        assert memory.confidence_score == 0.85
        assert memory.embedding is not None
    
    @pytest.mark.asyncio
    async def test_create_memory_from_transaction(self, db_session, test_user, test_transaction):
        """Test memory creation from transaction."""
        manager = MemoryManager(db_session)
        
        memory = await manager.create_memory_from_transaction(
            user_id=test_user.id,
            transaction=test_transaction,
        )
        
        assert memory is not None
        assert test_transaction.id in memory.transaction_ids
        assert memory.user_id == test_user.id
    
    @pytest.mark.asyncio
    async def test_validate_memory(self, db_session, test_user):
        """Test memory validation."""
        manager = MemoryManager(db_session)
        
        memory = await manager.create_memory(
            user_id=test_user.id,
            memory_type="spending_pattern",
            title="Test Memory",
            description="Test description",
            confidence_score=0.8,
        )
        
        original_confidence = memory.confidence_score
        success = await manager.validate_memory(memory.id)
        
        assert success
        
        # Verify confidence increased
        updated_memory = db_session.query(FinancialMemory).get(memory.id)
        assert updated_memory.is_validated
        assert updated_memory.confidence_score > original_confidence


class TestMemoryRetrieval:
    """Test memory retrieval."""
    
    @pytest.mark.asyncio
    async def test_search_similar_memories(self, db_session, test_user):
        """Test semantic memory search."""
        # Create test memories
        manager = MemoryManager(db_session)
        
        memory1 = await manager.create_memory(
            user_id=test_user.id,
            memory_type="behavioral_trigger",
            title="Weekend Overspending",
            description="You spend more on weekends, especially on entertainment",
            category="entertainment",
            confidence_score=0.9,
            impact_score=0.8,
        )
        
        memory2 = await manager.create_memory(
            user_id=test_user.id,
            memory_type="spending_pattern",
            title="Summer Vacation Spending",
            description="Higher spending during summer vacation period",
            category="travel",
            confidence_score=0.8,
            impact_score=0.7,
        )
        
        # Search for similar memories
        retrieval_service = MemoryRetrievalService(db_session)
        results = await retrieval_service.search_similar_memories(
            user_id=test_user.id,
            query_text="I spend a lot on entertainment during weekends",
            limit=5,
            min_similarity=0.4,
        )
        
        assert len(results) > 0
        # First result should be most similar (weekend spending)
        assert results[0]["id"] in [memory1.id, memory2.id]
    
    @pytest.mark.asyncio
    async def test_retrieve_contextual_memories(self, db_session, test_user):
        """Test contextual memory retrieval."""
        manager = MemoryManager(db_session)
        
        memory = await manager.create_memory(
            user_id=test_user.id,
            memory_type="spending_pattern",
            title="Food Spending Pattern",
            description="Higher food spending during winter months",
            category="food",
            confidence_score=0.9,
        )
        
        retrieval_service = MemoryRetrievalService(db_session)
        contextual_memories = await retrieval_service.retrieve_contextual_memories(
            user_id=test_user.id,
            transaction_category="food",
            transaction_amount=75.00,
            merchant="Restaurant",
            limit=5,
        )
        
        # Should retrieve food-related memories
        assert any(m["category"] == "food" for m in contextual_memories)


class TestBehavioralAnalyzer:
    """Test behavioral analysis."""
    
    @pytest.mark.asyncio
    async def test_analyze_spending_patterns(self, db_session, test_user, test_account, test_category):
        """Test spending pattern analysis."""
        # Create multiple transactions
        for i in range(10):
            transaction = Transaction(
                user_id=test_user.id,
                account_id=test_account.id,
                category_id=test_category.id,
                amount=25.00 + (i * 5),
                currency=Currency.USD,
                merchant=f"Restaurant {i}",
                transaction_type=TransactionType.EXPENSE,
                transaction_date=datetime.utcnow() - timedelta(days=i),
                confidence_score=0.95,
                source_type="manual"
            )
            db_session.add(transaction)
        
        db_session.commit()
        
        analyzer = BehavioralAnalyzer(db_session)
        patterns = await analyzer.analyze_spending_patterns(test_user.id, days_back=30)
        
        assert patterns["transaction_count"] == 10
        assert patterns["total_spending"] > 0
        assert len(patterns["by_category"]) > 0
        assert "insights" in patterns
    
    @pytest.mark.asyncio
    async def test_calculate_risk_tolerance(self, db_session, test_user, test_account, test_category):
        """Test risk tolerance calculation."""
        # Create transactions
        for i in range(5):
            transaction = Transaction(
                user_id=test_user.id,
                account_id=test_account.id,
                category_id=test_category.id,
                amount=50.00 + (i * 100),  # Varying amounts
                currency=Currency.USD,
                merchant=f"Store {i}",
                transaction_type=TransactionType.EXPENSE,
                transaction_date=datetime.utcnow() - timedelta(days=i),
                confidence_score=0.95,
                source_type="manual"
            )
            db_session.add(transaction)
        
        db_session.commit()
        
        analyzer = BehavioralAnalyzer(db_session)
        risk_profile = await analyzer.calculate_risk_tolerance(test_user.id)
        
        assert risk_profile["risk_tolerance"] in ["conservative", "moderate", "aggressive"]
        assert 0 <= risk_profile["risk_score"] <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
