# Financial Memory Engine - Quick Reference Guide

## 🎯 What It Does
The Financial Memory Engine creates long-term financial intelligence by remembering spending patterns, behavioral triggers, and user priorities using vector embeddings and explainable AI.

## 🚀 Quick Start

### Basic API Usage

#### 1. Store a Memory
```bash
curl -X POST "http://localhost:8000/api/v1/memory/store" \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d {
    "memory_type": "behavioral_trigger",
    "title": "Weekend Overspending",
    "description": "I spend 40% more on weekends",
    "category": "shopping",
    "confidence_score": 0.85,
    "impact_score": 0.7,
    "behavioral_tags": ["weekend", "impulse"]
  }
```

#### 2. Search Memories
```bash
curl -X POST "http://localhost:8000/api/v1/memory/search" \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d {
    "query": "I spend too much during stressful periods",
    "limit": 5,
    "min_similarity": 0.5
  }
```

#### 3. Get Contextual Memories (During Transaction)
```bash
curl "http://localhost:8000/api/v1/memory/contextual?category=food&amount=75&merchant=Restaurant" \
  -H "Authorization: ******"
```

#### 4. Get Behavioral Profile
```bash
curl "http://localhost:8000/api/v1/memory/behavioral-profile" \
  -H "Authorization: ******"
```

#### 5. Get Insights
```bash
curl "http://localhost:8000/api/v1/memory/insights?days_back=90" \
  -H "Authorization: ******"
```

## 📊 Memory Types

| Type | Usage | Example |
|------|-------|---------|
| `spending_pattern` | Regular spending habits | "Food spending averages $50/week" |
| `behavioral_trigger` | Spending triggers | "You overspend when stressed" |
| `seasonal_spending` | Seasonal variations | "Higher spending in December" |
| `emotional_spending` | Emotion-driven spending | "Stress-related weekend purchases" |
| `salary_cycle` | Income-related patterns | "Post-paycheck spending surge" |
| `recurring_expense` | Regular costs | "Netflix subscription $15/month" |
| `financial_goal` | User goals | "Save $1000 for vacation" |
| `user_priority` | Financial priorities | "Prioritize emergency fund" |
| `risk_tolerance` | Risk profile | "Moderate risk tolerance" |
| `subscription` | Subscription services | "Spotify, Netflix, etc." |

## 🏷️ Behavioral Tags

Use tags to categorize memories for better analysis:
- `stress_spending` - Spending during stressful periods
- `seasonal` - Occurs during specific seasons
- `weekend` - Weekend-specific behavior
- `post_paycheck` - After receiving income
- `impulsive` - Unplanned purchases
- `recurring` - Regular/cyclical spending
- `emotional` - Emotionally-driven
- `discretionary` - Optional spending
- `essential` - Necessary expenses

## 🔍 Composite Scoring Formula

Memory relevance is scored as:
```
Score = (Similarity × 0.40) + (Confidence × 0.25) + (Recency × 0.20) + (Popularity × 0.15)
```

Where:
- **Similarity**: How closely the memory matches your search
- **Confidence**: AI confidence in the memory (0-1)
- **Recency**: How recent the memory is (decays over 30 days)
- **Popularity**: How often the memory has been retrieved

## 📈 Behavioral Analysis Features

### Spending Pattern Analysis
- By category (Food, Transport, Entertainment, etc.)
- By day of week (Monday-Sunday)
- By month (January-December)
- Statistics: average, total, count, std deviation

### Behavioral Trigger Detection
- Weekend vs weekday spending
- Post-paycheck spending patterns
- Stress-related spending
- Holiday/seasonal triggers
- Unusual spending patterns

### Risk Tolerance Calculation
- **Conservative**: Low spending volatility, minimal anomalies
- **Moderate**: Average volatility, occasional anomalies
- **Aggressive**: High volatility, frequent anomalies

### Seasonal Pattern Analysis
- Monthly spending variations
- Z-score analysis for anomaly detection
- Seasonal insights with statistical significance

## 🔒 Security & Privacy

- **User Isolation**: Each user can only access their own memories
- **Error Handling**: Generic error messages prevent information leakage
- **Authorization**: All endpoints require authentication
- **Logging**: Detailed errors logged server-side only

## 🛠️ Integration Examples

### Auto-Memory from Transaction
```python
from app.ml.memory_engine.memory_manager import MemoryManager
from app.db.base import SessionLocal

db = SessionLocal()
manager = MemoryManager(db)

# Create memory from transaction
memory = await manager.create_memory_from_transaction(
    user_id=user.id,
    transaction=transaction_obj,
    behavioral_analysis={
        "tags": ["stress_spending"],
        "context": "high_workload"
    }
)
```

### Contextual Retrieval During Categorization
```python
from app.ml.memory_engine.memory_retrieval import MemoryRetrievalService

retrieval = MemoryRetrievalService(db)
contextual_memories = await retrieval.retrieve_contextual_memories(
    user_id=user.id,
    transaction_category="food",
    transaction_amount=75.00,
    merchant="Restaurant",
    limit=3
)
# Use these memories to suggest category or alert about spending
```

### Behavioral Profile Update
```python
from app.ml.memory_engine.behavioral_analyzer import BehavioralAnalyzer

analyzer = BehavioralAnalyzer(db)
risk_profile = await analyzer.calculate_risk_tolerance(user_id=user.id)
# Update user settings based on risk profile
```

## 📊 API Response Examples

### Search Memory Response
```json
[
  {
    "id": 42,
    "title": "Weekend Overspending",
    "description": "Higher spending on weekends",
    "similarity_score": 0.87,
    "composite_score": 0.82,
    "confidence": 0.9,
    "impact": 0.75,
    "retrieval_count": 23,
    "explanation": "This memory is highly relevant (87% similar). Tags: weekend, impulse. High financial impact."
  }
]
```

### Behavioral Profile Response
```json
{
  "spending_patterns": {
    "transaction_count": 245,
    "total_spending": 8500,
    "by_category": [
      {
        "category": "food",
        "total": 2100,
        "average": 24.71,
        "stdev": 15.32
      }
    ]
  },
  "behavioral_triggers": [
    {
      "trigger": "weekend_spending",
      "confidence": 0.85,
      "description": "You spend more on weekends"
    }
  ],
  "risk_profile": {
    "risk_tolerance": "moderate",
    "risk_score": 0.55
  }
}
```

### Insights Response
```json
{
  "insights": [
    {
      "type": "behavioral_trigger",
      "title": "Post Paycheck Spending",
      "description": "You tend to spend more after receiving paycheck",
      "confidence": 0.82,
      "examples": [
        {
          "merchant": "Best Buy",
          "amount": 250,
          "date": "2024-01-05"
        }
      ]
    },
    {
      "type": "seasonal_pattern",
      "title": "December Spending",
      "description": "Your December spending is high (z-score: 1.85)"
    }
  ]
}
```

## 🔧 Configuration

Add to `.env` file:
```env
# OpenAI Configuration
OPENAI_API_KEY=sk-...

# Memory Engine Settings (Optional)
EMBEDDING_MODEL=text-embedding-3-small
MEMORY_SIMILARITY_THRESHOLD=0.5
MEMORY_CONSOLIDATION_THRESHOLD=0.85
```

## 📚 Documentation

- **Full Documentation**: See `MEMORY_ENGINE_DOCUMENTATION.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **API Endpoint Tests**: See `tests/test_memory_engine.py`

## ⚡ Performance Tips

1. **Use Batch Retrieval**: Get multiple memories in one call
2. **Set Appropriate Similarity Threshold**: 0.5 for broad search, 0.7+ for precise
3. **Validate User Memories**: Validated memories get higher confidence (better ranking)
4. **Regular Consolidation**: Reduce redundancy, improve search speed
5. **Index Vector Searches**: Use pgvector's HNSW index for 10K+ memories

## 🐛 Debugging

### Check Memory Count
```sql
SELECT COUNT(*) FROM financial_memory WHERE user_id = ?;
```

### View Recent Memories
```sql
SELECT id, title, memory_type, confidence_score, created_at 
FROM financial_memory 
WHERE user_id = ? 
ORDER BY created_at DESC 
LIMIT 10;
```

### Check Embeddings
```sql
SELECT id, title, embedding IS NOT NULL as has_embedding 
FROM financial_memory 
WHERE user_id = ? 
LIMIT 5;
```

## 📞 Support

For issues or questions:
1. Check the full documentation: `MEMORY_ENGINE_DOCUMENTATION.md`
2. Review test cases: `tests/test_memory_engine.py`
3. Check implementation: `backend/app/ml/memory_engine/`
4. Review API code: `backend/app/api/v1/endpoints/memory_engine.py`

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0
**Status**: Production Ready
