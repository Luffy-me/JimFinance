# Financial Memory Engine Documentation

## Overview

The Financial Memory Engine is a sophisticated system that creates and maintains long-term contextual financial intelligence for users. It uses vector embeddings, behavioral pattern recognition, and explainable AI to understand spending habits, detect behavioral triggers, and provide personalized financial insights.

## Architecture

### Core Components

#### 1. **Embedding Service** (`embedding_service.py`)
- Generates semantic embeddings for financial memories using OpenAI's text-embedding-3-small model (1536 dimensions)
- Uses pgvector for efficient vector similarity search in PostgreSQL
- Calculates cosine similarity between memories for contextual matching

**Features:**
- Async embedding generation with batch processing
- Structured text preparation that preserves financial semantics
- Similarity scoring and ranking

#### 2. **Memory Manager** (`memory_manager.py`)
- Creates and manages financial memories from transactions and user input
- Handles memory lifecycle: creation, validation, consolidation
- Extracts behavioral insights from transaction data
- Consolidates similar memories to reduce redundancy

**Key Methods:**
- `create_memory()`: Create new memory with embedding
- `create_memory_from_transaction()`: Auto-create memory from transaction
- `validate_memory()`: Mark memory as user-validated (increases confidence)
- `consolidate_similar_memories()`: Merge redundant memories
- `update_memory_confidence()`: Adjust confidence scores

#### 3. **Memory Retrieval Service** (`memory_retrieval.py`)
- Retrieves semantically similar memories using vector search
- Implements composite scoring algorithm for ranking:
  - Similarity score: 40%
  - Confidence score: 25%
  - Recency (decay over 30 days): 20%
  - Popularity (retrieval count): 15%
- Provides contextual retrieval for transaction processing
- Tracks memory interactions for analytics and ranking

**Key Methods:**
- `search_similar_memories()`: Semantic search with scoring
- `retrieve_contextual_memories()`: Get memories relevant to current transaction
- `retrieve_behavioral_memories()`: Get recent behavioral insights

#### 4. **Behavioral Analyzer** (`behavioral_analyzer.py`)
- Detects spending patterns, seasonal variations, and behavioral triggers
- Analyzes temporal patterns in spending
- Calculates risk tolerance based on financial behavior
- Generates explainable insights with evidence

**Key Methods:**
- `analyze_spending_patterns()`: Category and temporal analysis
- `detect_behavioral_triggers()`: Find spending triggers (weekend, post-paycheck, stress)
- `analyze_seasonal_patterns()`: Monthly spending variations
- `calculate_risk_tolerance()`: Profile user's risk appetite

### Database Schema

#### FinancialMemory
```
- id: Primary key
- user_id: User reference
- memory_type: spending_pattern, emotional_spending, salary_cycle, recurring_expense, subscription, behavioral_trigger, seasonal_spending, financial_goal, user_priority, risk_tolerance
- memory_category: Fine-grained categorization
- title: Memory title
- description: Memory description
- data: JSON structured financial data
- transaction_ids: References to source transactions
- embedding: Vector embedding (1536 dimensions)
- confidence_score: AI confidence (0-1)
- is_validated: User-validated memory
- impact_score: Financial impact (0-1)
- relevance_score: Current relevance (0-1)
- retrieval_count: Usage count for popularity ranking
- memory_date: When this memory occurred
- last_accessed_at: Last retrieval time
- contextual_data: Additional context (emotional state, etc.)
- behavioral_tags: Behavioral classification tags
- created_at/updated_at: Timestamps
```

#### MemoryInteraction
```
- id: Primary key
- memory_id: Memory reference
- user_id: User reference
- context: Interaction type (transaction_categorization, behavioral_analysis, etc.)
- retrieval_score: Score assigned during retrieval
- relevance_feedback: User feedback (-1, 0, 1)
- retrieved_at: When memory was retrieved
```

#### BehavioralProfile
```
- id: Primary key
- user_id: User reference (unique)
- risk_tolerance: conservative, moderate, aggressive
- risk_score: Calculated risk score (0-1)
- spending_triggers: List of identified triggers
- seasonal_patterns: Monthly spending variations
- emotional_spending_tendency: Propensity for emotional spending (0-1)
- priorities: Financial goals/priorities
- avg_spending_per_month: Average monthly spending
- spending_volatility: Standard deviation of spending
- profile_last_refined_at: Last update timestamp
```

## API Endpoints

### 1. Store Memory
**POST** `/api/v1/memory/store`

Create a new financial memory.

**Request:**
```json
{
  "memory_type": "behavioral_trigger",
  "title": "Weekend Overspending",
  "description": "I tend to spend more on weekends",
  "category": "shopping",
  "confidence_score": 0.85,
  "impact_score": 0.7,
  "behavioral_tags": ["weekend", "impulse"],
  "contextual_data": {
    "days": ["Saturday", "Sunday"],
    "amount_increase": "40%"
  }
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Weekend Overspending",
  "memory_type": "behavioral_trigger",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 2. Search Memories
**POST** `/api/v1/memory/search`

Search for similar memories using semantic similarity.

**Request:**
```json
{
  "query": "I spend too much on food when stressed",
  "limit": 5,
  "min_similarity": 0.5
}
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Stress-Related Spending",
    "description": "Higher spending during stressful work periods",
    "memory_type": "behavioral_trigger",
    "category": "food",
    "similarity_score": 0.87,
    "composite_score": 0.82,
    "confidence": 0.9,
    "impact": 0.75,
    "retrieval_count": 23,
    "date": "2024-01-10T08:00:00Z",
    "explanation": "This memory is highly relevant (similarity: 87%). Tags: stress, food, seasonal. This has high financial impact."
  }
]
```

### 3. Get Contextual Memories
**GET** `/api/v1/memory/contextual?category=food&amount=75&merchant=Restaurant`

Retrieve memories relevant to current transaction context.

**Response:**
Similar to search, but filtered by context.

### 4. Get Behavioral Profile
**GET** `/api/v1/memory/behavioral-profile`

Get comprehensive user behavioral profile.

**Response:**
```json
{
  "user_id": 123,
  "spending_patterns": {
    "analysis_period_days": 90,
    "transaction_count": 245,
    "total_spending": 8500.00,
    "by_category": [
      {
        "category": "food",
        "total": 2100,
        "count": 85,
        "average": 24.71,
        "stdev": 15.32
      }
    ],
    "by_month": {"2024-01": 2800, "2024-02": 2600, "2024-03": 3100},
    "by_day_of_week": {
      "Monday": {"count": 32, "total": 1200, "average": 37.50},
      "Saturday": {"count": 42, "total": 1800, "average": 42.86}
    }
  },
  "behavioral_triggers": [
    {
      "trigger": "weekend_spending",
      "confidence": 0.85,
      "description": "You tend to spend more on weekends",
      "evidence": "28 out of 42 weekend transactions exceeded daily average"
    }
  ],
  "seasonal_patterns": {
    "seasonal_patterns": [
      {
        "month": "January",
        "average_spending": 2800,
        "total_spending": 2800,
        "transaction_count": 95,
        "z_score": 0.45,
        "deviation": "normal"
      }
    ]
  },
  "risk_profile": {
    "risk_tolerance": "moderate",
    "risk_score": 0.55,
    "spending_volatility": 0.42,
    "anomaly_ratio": 0.15
  }
}
```

### 5. Get Behavioral Insights
**GET** `/api/v1/memory/insights?days_back=90`

Get explainable behavioral insights with evidence.

**Response:**
```json
{
  "insights": [
    {
      "type": "top_categories",
      "description": "Your highest spending categories are: food, entertainment, shopping",
      "priority": "high"
    },
    {
      "type": "behavioral_trigger",
      "title": "Post Paycheck Spending",
      "description": "You tend to spend more right after receiving your paycheck",
      "confidence": 0.82,
      "evidence": "15 anomalies occurred within a week of paychecks",
      "examples": [
        {
          "merchant": "Best Buy",
          "amount": 250,
          "date": "2024-01-05",
          "category": "shopping"
        }
      ]
    },
    {
      "type": "seasonal_pattern",
      "title": "December Spending Pattern",
      "description": "Your December spending is high compared to other months",
      "evidence": "Average: $580.00",
      "z_score": 1.85
    }
  ],
  "analysis_period_days": 90,
  "transaction_count": 245,
  "total_spending": 8500.00
}
```

### 6. Validate Memory
**POST** `/api/v1/memory/validate/{memory_id}`

Mark a memory as validated by user, increasing its confidence.

**Response:**
```json
{
  "status": "validated",
  "memory_id": 1
}
```

### 7. Get Memory Details
**GET** `/api/v1/memory/{memory_id}`

Get full details of a specific memory.

## Memory Types

1. **spending_pattern**: Regular spending behaviors by category
2. **emotional_spending**: Spending triggered by emotions or stress
3. **salary_cycle**: Income-related spending patterns
4. **recurring_expense**: Identified subscription or recurring costs
5. **subscription**: Subscription services identified
6. **behavioral_trigger**: Spending triggers (stress, weekend, holidays)
7. **seasonal_spending**: Seasonal spending variations
8. **financial_goal**: User's financial goals and targets
9. **user_priority**: Financial priorities (savings, investment, etc.)
10. **risk_tolerance**: User's risk appetite and profile

## Behavioral Tags

- `stress_spending`: Correlated with stressful periods
- `seasonal`: Occurs during specific seasons
- `weekend`: Weekend-specific spending
- `post_paycheck`: Occurs after paychecks
- `impulsive`: Unplanned/anomalous spending
- `recurring`: Regular/cyclical spending
- `emotional`: Emotionally-driven spending
- `discretionary`: Optional/non-essential spending
- `essential`: Necessary/required spending

## Memory Scoring Algorithm

### Composite Score Calculation
```
composite_score = (
    similarity_score * 0.40 +        # How similar to current context
    confidence_score * 0.25 +        # AI confidence in memory
    recency_score * 0.20 +           # How recent (decay over 30 days)
    popularity_score * 0.15          # How many times retrieved
)
```

### Recency Score
- Decays linearly over 30 days
- New memories (0 days old): score = 1.0
- 30-day-old memories: score = 0.0

### Popularity Score
- Based on retrieval count
- Capped at 100 retrievals for normalization
- 0 retrievals: score = 0.0
- 100+ retrievals: score = 1.0

## Integration Points

### Transaction Processing
When a new transaction is created:
1. Retrieve contextual memories related to the transaction
2. Check behavioral triggers for anomaly detection
3. Create new memory if significant pattern detected

### Behavioral Analysis
Triggered periodically to:
1. Consolidate similar memories
2. Update behavioral profile
3. Refine memory confidence scores
4. Generate actionable insights

### Dashboard Display
Memory engine provides:
1. Personalized spending insights
2. Behavioral pattern summaries
3. Risk profile information
4. Anomaly alerts

## Example Usage Scenarios

### Scenario 1: Detect Stress Spending
1. User has unusual spending spike on Tuesday evening
2. Retrieval service searches for similar high-amount transactions
3. Behavioral analyzer identifies other Tuesday evening spikes
4. Detects correlation with work deadlines (external context)
5. Creates memory: "Stress-related spending on weekday evenings"
6. Returns insight: "You tend to overspend during stressful work periods"

### Scenario 2: Seasonal Pattern Recognition
1. System analyzes 12 months of transaction history
2. Detects higher food spending in November-December (holiday season)
3. Creates memory: "Seasonal spending increase during winter holidays"
4. When user spends on food in November, system highlights this pattern
5. Provides recommendation: "Your food spending typically increases 35% during holidays"

### Scenario 3: Post-Paycheck Spending
1. System identifies salary transactions
2. Analyzes anomalies in days following paychecks
3. Detects 60% of anomalies occur within 7 days of paychecks
4. Creates memory: "Post-paycheck spending surge"
5. Alerts user before next paycheck with behavioral insight

## Performance Considerations

- **Vector Similarity Search**: pgvector with cosine distance O(n) for scan, indexed O(log n) for HNSW
- **Memory Consolidation**: Runs async, can handle 10K+ memories per user
- **Embedding Generation**: Batch processing for efficiency (OpenAI API)
- **Composite Scoring**: In-memory calculation, no DB overhead
- **Caching**: Memory interactions tracked for ranking optimization

## Configuration

Add to `.env`:
```
OPENAI_API_KEY=your_api_key_here
EMBEDDING_MODEL=text-embedding-3-small
MEMORY_SIMILARITY_THRESHOLD=0.5
MEMORY_CONSOLIDATION_THRESHOLD=0.85
```

## Future Enhancements

1. **Multi-modal embeddings**: Include transaction images, receipts, merchants
2. **Temporal memory patterns**: Track when memories become relevant/irrelevant
3. **Social comparison**: Compare behaviors with anonymized peer data
4. **Predictive memory**: Forecast future spending based on historical patterns
5. **Counterfactual analysis**: "What if" scenarios based on memory patterns
6. **Memory explanations**: Generate natural language explanations using LLMs
7. **Memory feedback loop**: User corrections improve memory quality over time
