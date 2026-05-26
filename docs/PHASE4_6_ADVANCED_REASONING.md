# Phase 4.6: Advanced Multi-Agent Financial Reasoning System

## Overview

Phase 4.6 extends the Phase 4.1-4.5 multi-agent financial reasoning engine with five advanced capabilities:

1. **Inflation-Adjusted Forecasting** - Real vs. nominal value projections
2. **Reasoning Memory System** - Persistent debate storage and learning
3. **Debate Visualization APIs** - Detailed reasoning chain endpoints
4. **Advanced Scenario Modeling** - Employment shocks, tax impacts, debt
5. **Behavioral Integration** - Link spending patterns to decisions

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│         Financial Decision with Advanced Context           │
│            (Purchase, Investment, Spending Cut)            │
└────────────────┬─────────────────────────────────────────┘
                 │
        ┌────────┴────────────────┬────────────────┐
        │                         │                │
    ┌───▼───────┐    ┌──────────▼──┐    ┌────────▼──┐
    │ INFLATION │    │ BEHAVIORAL  │    │ ADVANCED  │
    │ ADJUSTMENT│    │ ANALYSIS    │    │ SCENARIOS │
    └───┬───────┘    └──────┬──────┘    └────┬─────┘
        │                   │              │
        └───────────────────┼──────────────┘
                            │
                ┌───────────▼───────────┐
                │  MULTI-AGENT DEBATE  │
                │  (Strategist/Critic) │
                └───────────┬───────────┘
                            │
                ┌───────────▼────────────────┐
                │   REASONING MEMORY         │
                │   - Store debate record    │
                │   - Track outcomes         │
                │   - Enable learning        │
                └────────────────────────────┘
```

## Component Details

### 1. Inflation-Adjusted Forecasting Engine

**File**: `backend/app/ml/financial_reasoning/forecast_engine.py`

**Features**:
- Historical CPI data (US, Russia, EU)
- Forward-looking inflation guidance
- Real vs. nominal value calculations
- Inflation-adjusted runway analysis
- Purchase affordability with inflation impact

**Key Methods**:
```python
engine = ForecastingEngine(country="US")

# Convert nominal to real value
metric = engine.nominal_to_real(
    nominal_amount=1000,
    start_date=datetime.utcnow(),
    end_date=datetime.utcnow() + timedelta(days=365),
    inflation_scenario=InflationScenario.MODERATE,
)

# Calculate runway with inflation
result = engine.inflation_adjusted_runway(
    current_balance=10000,
    monthly_expenses=500,
    inflation_scenario=InflationScenario.MODERATE,
    months=60,
)
```

**Scenarios Supported**:
- LOW: 1% annual inflation
- MODERATE: 3% annual inflation (historical average)
- HIGH: 5% annual inflation
- HYPERINFLATION: 10%+ annual inflation

### 2. Reasoning Memory System

**Files**:
- `backend/app/models/database.py` - ReasoningMemory model
- `backend/app/ml/reasoning_memory/memory_service.py` - Service layer

**Database Model**:
- Stores complete debate records
- Tracks financial context
- Records agent positions and reasoning chains
- Enables outcome tracking for learning

**Key Methods**:
```python
service = ReasoningMemoryService()

# Store debate record
memory = service.store_debate_record(
    db=db,
    user_id=user_id,
    debate_record=debate_record,
    quantitative_analysis=analysis,
    scenario_analysis=scenarios,
)

# Find similar past debates
similar = service.find_similar_debates(
    db=db,
    user_id=user_id,
    decision_type="purchase",
    purchase_price=1200,
    limit=5,
)

# Record decision outcome
success = service.record_outcome(
    db=db,
    user_id=user_id,
    decision_id=decision_id,
    outcome="purchased",  # or "not_purchased", "regretted", "satisfied"
    notes="Very satisfied with purchase",
)

# Get decision statistics
stats = service.get_decision_statistics(db, user_id, days_back=365)

# Get recommendation accuracy
accuracy = service.get_recommendation_accuracy(
    db, user_id, recommendation="recommended", days_back=365
)
```

### 3. Debate Visualization APIs

**File**: `backend/app/api/v1/endpoints/agents.py`

**New Endpoints**:

#### GET `/api/v1/agents/decision/{decision_id}/debate`
Retrieve full debate record with all positions and reasoning.

**Response**:
```json
{
  "success": true,
  "data": {
    "decision_id": "uuid",
    "decision": {
      "name": "iPhone Purchase",
      "price": 1200,
      "type": "purchase"
    },
    "financial_context": {
      "monthly_income": 5000,
      "monthly_expenses": 3000,
      "current_balance": 8000
    },
    "debate": {
      "strategist": {
        "position": {...},
        "reasoning_chain": [...]
      },
      "critic": {
        "position": {...},
        "reasoning_chain": [...]
      }
    },
    "synthesis": {...},
    "final_recommendation": "recommended",
    "confidence_score": 0.75
  }
}
```

#### GET `/api/v1/agents/decision/{decision_id}/reasoning-chain`
Retrieve step-by-step reasoning from both agents.

#### GET `/api/v1/agents/debates/similar`
Find similar past debates for comparison and learning.

#### POST `/api/v1/agents/decision/{decision_id}/outcome`
Record the actual outcome of a decision (purchased, regretted, etc.).

#### GET `/api/v1/agents/decision-statistics`
Get statistics on past decisions and recommendation accuracy.

### 4. Advanced Scenario Modeling

**File**: `backend/app/ml/financial_reasoning/advanced_scenarios.py`

**Analyzers**:

#### Employment Shock Analyzer
```python
analyzer = EmploymentShockAnalyzer()

# Job loss scenario
scenario = analyzer.model_job_loss(
    current_monthly_income=5000,
    monthly_expenses=3000,
    current_balance=15000,
    unemployment_benefit_percent=0.60,  # 60% replacement
)

# Salary cut scenario
scenario = analyzer.model_salary_cut(
    current_monthly_income=5000,
    monthly_expenses=3000,
    current_balance=10000,
    salary_reduction_percent=0.20,
    duration_months=6,
)
```

#### Tax Impact Analyzer
```python
analyzer = TaxImpactAnalyzer(regime=TaxRegime.US)

# Calculate net income
result = analyzer.calculate_net_income(
    gross_income=60000,
    deductions=6000,
)

# Tax scenario with income change
scenario = analyzer.income_tax_scenario(
    current_gross_income=60000,
    monthly_expenses=3000,
    current_balance=15000,
    projected_income_change=0.20,  # 20% raise
)
```

Supported Regimes:
- US: Progressive tax brackets (2024)
- RUSSIA: 13% flat rate
- EU: Average progressive brackets
- SIMPLE: 20% flat rate

#### Debt Scenario Analyzer
```python
analyzer = DebtScenarioAnalyzer()

# Student loan impact
scenario = analyzer.model_student_loan(
    loan_amount=100000,
    monthly_expenses=3000,
    monthly_income=5000,
    current_balance=5000,
    interest_rate=0.045,
    repayment_years=10,
)

# Credit card debt impact
scenario = analyzer.model_credit_card_debt(
    balance=5000,
    monthly_expenses=2000,
    monthly_income=4000,
    current_balance=1000,
    interest_rate=0.20,
)

# Medical emergency impact
analyzer_life = LifeEventAnalyzer()
scenario = analyzer_life.model_medical_emergency(
    emergency_cost=10000,
    monthly_expenses=3000,
    monthly_income=5000,
    current_balance=8000,
    recovery_months=3,
)
```

### 5. Behavioral Integration

**File**: `backend/app/ml/reasoning_memory/behavioral_integration.py`

**Features**:
- Extract behavioral factors from transactions
- Adjust confidence based on behavioral predictability
- Detect spending triggers (stress, emotional, post-paycheck)
- Calculate impulse spending score
- Measure seasonal volatility
- Assess risk tolerance from spending patterns

**Key Methods**:
```python
engine = BehavioralIntegrationEngine()

# Extract behavioral factors
factors = engine.extract_behavioral_factors(
    transactions=transactions,
)

# Adjust recommendation based on behavior
result = engine.adjust_decision_recommendation(
    base_recommendation="recommended",
    base_confidence=0.8,
    behavioral_factors=factors,
    decision_type="purchase",
)

# Assess behavioral risk level
warning = engine.get_behavioral_warning_level(factors)
# Returns: "low", "medium", or "high"
```

**Behavioral Factors**:
- Risk Tolerance (0-100): How much financial volatility the user accepts
- Impulse Spending Score (0-1): Tendency toward impulsive purchases
- Stress Spending Tendency (0-1): Likelihood of emotional spending
- Seasonal Volatility (0-1): Seasonal spending variations
- Decision Confidence Adjustment (-0.2 to +0.2): Modifier for base confidence

## Integration Points

### With Existing Systems

1. **Strategist Agent** (Gemini Pro)
   - Uses inflation scenarios for opportunity analysis
   - Integrates behavioral factors for personalization

2. **Critic Agent** (Groq)
   - Uses advanced scenarios for downside modeling
   - References past similar decisions via reasoning memory

3. **Synthesis Engine**
   - Incorporates behavioral warnings into final recommendations
   - References similar decision outcomes for calibration

4. **Quantitative Engine**
   - Inflation-adjusted runway in affordability analysis
   - Tax-adjusted income in income calculations

### Database Migrations

New table: `reasoning_memory`
- Stores complete debate records
- Enables learning from past decisions
- Tracks decision outcomes

```sql
CREATE TABLE reasoning_memory (
  id INTEGER PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  decision_id VARCHAR UNIQUE,
  decision_name VARCHAR,
  decision_description TEXT,
  decision_type VARCHAR,
  strategist_position JSON,
  critic_position JSON,
  synthesis JSON,
  strategist_reasoning_chain JSON,
  critic_reasoning_chain JSON,
  quantitative_analysis JSON,
  scenario_analysis JSON,
  final_recommendation VARCHAR,
  confidence_score FLOAT,
  actual_outcome VARCHAR,
  outcome_date DATETIME,
  created_at DATETIME DEFAULT NOW()
);
```

## Testing

**File**: `backend/tests/test_phase_4_6_enhancements.py`

**Test Coverage**:
- Inflation calculations (nominal ↔ real conversion)
- Runway with inflation impact
- Employment shocks (job loss, salary cut)
- Tax scenarios (US, Russia, EU)
- Debt scenarios (student loans, credit cards)
- Behavioral factor extraction
- Recommendation adjustment based on behavior

## Example Usage Flow

### Complete Decision Analysis with All Features

```python
from datetime import datetime, timedelta
from app.ml.financial_reasoning.forecast_engine import ForecastingEngine, InflationScenario
from app.ml.financial_reasoning.advanced_scenarios import (
    EmploymentShockAnalyzer, TaxImpactAnalyzer
)
from app.ml.reasoning_memory.memory_service import ReasoningMemoryService
from app.ml.reasoning_memory.behavioral_integration import BehavioralIntegrationEngine

# 1. Gather user context
user_data = {
    "monthly_income": 5000,
    "monthly_expenses": 3000,
    "current_balance": 8000,
    "transactions": [...],  # Last 90 days
}

# 2. Extract behavioral factors
behavioral_engine = BehavioralIntegrationEngine()
behavioral_factors = behavioral_engine.extract_behavioral_factors(
    transactions=user_data["transactions"]
)

# 3. Run inflation-adjusted analysis
forecast_engine = ForecastingEngine(country="US")
affordability = forecast_engine.purchase_affordability_inflation_adjusted(
    purchase_price_today=1200,  # iPhone
    months_until_purchase=1,
    monthly_income=user_data["monthly_income"],
    monthly_expenses=user_data["monthly_expenses"],
    current_balance=user_data["current_balance"],
    inflation_scenario=InflationScenario.MODERATE,
)

# 4. Generate advanced scenarios
employment_analyzer = EmploymentShockAnalyzer()
job_loss_scenario = employment_analyzer.model_job_loss(
    current_monthly_income=user_data["monthly_income"],
    monthly_expenses=user_data["monthly_expenses"],
    current_balance=user_data["current_balance"],
)

# 5. Run multi-agent debate (existing)
debate_record = await orchestrator.orchestrate_debate(...)

# 6. Adjust recommendation for behavior
adjusted = behavioral_engine.adjust_decision_recommendation(
    base_recommendation=debate_record.final_recommendation,
    base_confidence=debate_record.synthesis["overall_confidence"],
    behavioral_factors=behavioral_factors,
    decision_type="purchase",
)

# 7. Store for learning
memory_service = ReasoningMemoryService()
memory = memory_service.store_debate_record(
    db=db,
    user_id=user_id,
    debate_record=debate_record,
    quantitative_analysis=affordability,
    scenario_analysis={"job_loss": job_loss_scenario},
    decision_type="purchase",
)

# 8. Later: record outcome for improvement
memory_service.record_outcome(
    db=db,
    user_id=user_id,
    decision_id=debate_record.decision_id,
    outcome="satisfied",
    notes="Great purchase, no regrets",
)

# 9. Future decisions: find similar past decisions
similar = memory_service.find_similar_debates(
    db=db,
    user_id=user_id,
    decision_type="purchase",
    purchase_price=1200,
    limit=5,
)
```

## Performance Considerations

- Inflation calculations: O(1) for known years, O(n) for date ranges
- Behavioral analysis: O(n) where n = number of transactions
- Database queries: Indexed on user_id, decision_id, created_at
- Memory storage: ~2KB per debate record

## Security & Privacy

- All reasoning memory isolated by user_id
- No financial data shared between users
- Debate records encrypted at rest (via db permissions)
- No PII stored in reasoning chains
- Audit trail maintained for all decisions

## Future Enhancements

1. **Counterfactual Analysis**: "What if" scenarios with specific changes
2. **Peer Benchmarking**: Anonymous comparison with similar users
3. **Machine Learning Calibration**: Improve recommendations based on outcome accuracy
4. **Multi-step Decisions**: Complex decisions spanning multiple steps
5. **Natural Language Generation**: NLG for reasoning chain explanations
6. **Mobile Support**: Optimize APIs for mobile client consumption

## Files Summary

### New Files (5)
- `forecast_engine.py` (450 lines) - Inflation modeling
- `advanced_scenarios.py` (600 lines) - Employment, tax, debt, life event scenarios
- `memory_service.py` (350 lines) - Reasoning memory persistence
- `behavioral_integration.py` (400 lines) - Behavioral analysis integration
- `test_phase_4_6_enhancements.py` (250 lines) - Comprehensive tests

### Modified Files (2)
- `database.py` - Added ReasoningMemory model
- `agents.py` - Added 5 new API endpoints

### Total New Code: ~2,050 lines

## Status

✅ **Phase 4.6 COMPLETE**

All five components implemented, tested, and documented:
- [x] Inflation-Adjusted Forecasting
- [x] Reasoning Memory System
- [x] Debate Visualization APIs
- [x] Advanced Scenario Modeling
- [x] Behavioral Integration

Ready for Phase 5 (Dashboard Integration) or Phase 4.7 (Advanced Features)
