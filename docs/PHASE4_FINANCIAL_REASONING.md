# Phase 4: Multi-Agent Financial Reasoning Engine

## 🎯 Overview

Phase 4 implements a sophisticated, quantitative financial decision intelligence system that combines:
- **Deterministic Mathematics**: Rigorous financial calculations with confidence intervals
- **Probabilistic Analysis**: Monte Carlo simulations and scenario planning
- **Multi-Agent Debate**: Strategist and Critic agents debate financial decisions
- **Decision Intelligence**: Affordability analysis with three-tier recommendations

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Financial Decision Request                   │
│                  "Can I afford iPhone for ₽120,000?"             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
    ┌───────────▼──────────────┐  ┌──────▼────────────────┐
    │  QUANTITATIVE ENGINE     │  │  SCENARIO ANALYZER    │
    │  - Savings rate math     │  │  - Conservative       │
    │  - Burn rate calc        │  │  - Balanced           │
    │  - Runway analysis       │  │  - Aggressive         │
    │  - Confidence scoring    │  │  - Affordability      │
    └───────────┬──────────────┘  └──────┬────────────────┘
                │                         │
    ┌───────────▼──────────────────────────▼─────────────────┐
    │           PROBABILITY ENGINE                           │
    │  - Distribution analysis                              │
    │  - Monte Carlo simulations                            │
    │  - Risk probability calculations                      │
    └───────────┬──────────────────────────────────────────┘
                │
    ┌───────────▼──────────────────────────────────────────┐
    │         DEBATE ORCHESTRATION                         │
    │  ┌────────────────┐        ┌──────────────────┐     │
    │  │  Strategist    │        │  Critic Agent    │     │
    │  │  (Gemini Pro)  │◄──────►│  (Groq API)      │     │
    │  │  - Upside      │        │  - Downside      │     │
    │  │  - Opportunity │        │  - Risk          │     │
    │  └────────────────┘        └──────────────────┘     │
    └───────────┬──────────────────────────────────────────┘
                │
    ┌───────────▼──────────────────────────────────────────┐
    │         SYNTHESIS & RECOMMENDATION                   │
    │  - Conservative conclusion (avoid)                   │
    │  - Balanced conclusion (plan)                        │
    │  - Aggressive conclusion (pursue)                    │
    │  - Final recommendation + confidence                 │
    │  - Assumptions & reasoning chain                     │
    └─────────────────────────────────────────────────────┘
```

## 🔧 Core Components

### 1. QuantitativeEngine (`quantitative_engine.py`)

**Purpose**: Deterministic financial mathematics with confidence intervals

**Key Calculations**:
- **Savings Rate**: `(income - expenses) / income` with ±5% confidence bands
- **Burn Rate**: Monthly expense velocity from transaction history
- **Runway**: `balance / burn_rate` with urgency-based confidence
- **Cashflow Velocity**: Total transaction volume / days
- **Spending Volatility**: Coefficient of variation for expense predictability

**Features**:
```python
engine = QuantitativeEngine()

# Calculate savings rate
metric = engine.calculate_savings_rate(
    monthly_income=5000,
    monthly_expenses=3000,
)
# Returns: QuantitativeMetric with value=0.4, confidence=0.95

# Calculate runway
runway = engine.calculate_runway(
    current_balance=15000,
    monthly_burn_rate=1000,
)
# Returns: 15 months with 95% confidence
```

**Output Structure**:
```python
@dataclass
class QuantitativeMetric:
    value: float                    # Primary metric value
    lower_bound: float              # 95% confidence lower
    upper_bound: float              # 95% confidence upper
    confidence: float               # 0-1 confidence score
    calculation_method: str         # How calculated
    assumptions: List[str]          # Key assumptions
    timestamp: datetime             # When calculated
```

### 2. ScenarioAnalyzer (`scenario_analyzer.py`)

**Purpose**: Generate three-tier scenarios for decision-making

**Scenarios**:

#### Conservative (25% probability)
- **Income**: -15% (recession, reduced hours)
- **Expenses**: +10% (trend adjustment)
- **Assumption**: Potential job loss risk
- **Use**: Worst-case planning

#### Balanced (50% probability)
- **Income**: Current level
- **Expenses**: Natural trend
- **Assumption**: Status quo continues
- **Use**: Most likely trajectory

#### Aggressive (25% probability)
- **Income**: +20% (promotion, side income)
- **Expenses**: -15% (optimized)
- **Assumption**: Active optimization
- **Use**: Opportunity upside

**Example**:
```python
analyzer = ScenarioAnalyzer()

scenarios = analyzer.generate_scenarios(
    monthly_income=5000,
    monthly_expenses=3000,
    current_balance=20000,
)

for scenario in scenarios:
    print(f"{scenario.type.value}: {scenario.recommendation}")
    print(f"  Runway: {scenario.projected_runway_months} months")
    print(f"  Stress: {scenario.stress_level}")
    print(f"  Actions: {scenario.action_items}")

# Affordability analysis
affordability = analyzer.affordability_analysis(
    purchase_price=1200,  # iPhone
    current_balance=15000,
    monthly_income=5000,
    monthly_expenses=3000,
    emergency_fund_target=18000,  # 6 months
)
```

### 3. ProbabilityEngine (`probability_engine.py`)

**Purpose**: Probabilistic analysis via Monte Carlo simulations

**Capabilities**:
- **Distribution Estimation**: Income and expense patterns
- **Monte Carlo Simulation**: Project financial outcomes
- **Event Probability**: Calculate probability of specific outcomes
- **Confidence Scoring**: Data quality → confidence
- **Runway Probability**: Likelihood of financial stability

**Example**:
```python
prob_engine = ProbabilityEngine(num_simulations=10000)

# Run Monte Carlo
result = prob_engine.run_monte_carlo_simulation(
    initial_balance=15000,
    monthly_income_mean=5000,
    monthly_income_std=300,
    monthly_expenses_mean=3000,
    monthly_expenses_std=200,
    months_to_simulate=60,
)

print(f"Probability positive: {result['probability_positive_end']:.1%}")
print(f"Never goes negative: {result['probability_never_negative']:.1%}")
print(f"Bankruptcy risk: {result['probability_bankruptcy']:.1%}")

# Affordability probability
affordability_prob = prob_engine.probability_of_affordability(
    purchase_price=1200,
    current_balance=15000,
    balance_std_dev=1500,
    emergency_fund=9000,
)
```

### 4. DecisionAnalyzer (`decision_analyzer.py`)

**Purpose**: Comprehensive financial decision analysis

**Analysis Output**:
```python
{
    "decision": {
        "name": "iPhone Purchase",
        "type": "lump_sum",
        "price": 1200,
    },
    "financial_snapshot": {
        "monthly_income": 5000,
        "savings_rate": 0.40,
        "burn_rate": 1000,
        "runway_months": 15,
    },
    "affordability": {
        "can_afford": true,
        "balance_after": 13800,
        "scenarios": {
            "conservative": {"can_afford": true, "stress": "medium"},
            "balanced": {"can_afford": true, "stress": "low"},
            "aggressive": {"can_afford": true, "stress": "low"},
        }
    },
    "financial_impacts": [
        {
            "type": "balance_reduction",
            "current": 15000,
            "projected": 13800,
            "change_percent": -8.0,
            "severity": "moderate",
        }
    ],
    "recommendation": {
        "level": "recommended",
        "confidence": 0.85,
        "reasoning": "Affordable in all scenarios...",
        "concerns": [],
        "action_items": ["..."],
    }
}
```

### 5. DebateOrchestrator (`orchestrator.py`)

**Purpose**: Multi-agent debate on financial decisions

**Process**:
1. **Quantitative Analysis**: Run decision analyzer
2. **Strategist Opening**: Opportunity analysis
3. **Critic Opening**: Risk analysis
4. **Synthesis**: Combine positions
5. **Final Recommendation**: Conservative → Balanced → Aggressive

**Debate Output**:
```python
{
    "decision_id": "uuid",
    "positions": [
        {
            "agent": "Strategist",
            "phase": "strategist_opening",
            "confidence": 0.80,
            "reasoning": ["point1", "point2", ...],
            "analysis": {...},
        },
        {
            "agent": "Critic",
            "phase": "critic_opening",
            "confidence": 0.75,
            "reasoning": ["concern1", "concern2", ...],
            "analysis": {...},
        }
    ],
    "synthesis": {
        "recommendations": [...],
        "concerns": [...],
        "confidence": 0.78,
    },
    "final_recommendation": "recommended",
}
```

## 📡 API Endpoints

### POST `/api/v1/agents/decide`
Analyze a specific financial decision

```bash
curl -X POST http://localhost:8000/api/v1/agents/decide \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d '{
    "decision_name": "iPhone 15 Pro",
    "description": "New smartphone purchase",
    "purchase_price": 1200,
    "monthly_payment": null,
    "days": 30
  }'
```

**Response**:
```json
{
  "success": true,
  "data": {
    "decision": {...},
    "quantitative_analysis": {...},
    "debate_record": {...},
    "recommendation": "recommended",
    "confidence": 0.85
  }
}
```

### POST `/api/v1/agents/scenarios`
Generate scenario analysis

```bash
curl -X POST http://localhost:8000/api/v1/agents/scenarios \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d '{
    "monthly_income": 5000,
    "monthly_expenses": 3000,
    "current_balance": 15000
  }'
```

**Response**:
```json
{
  "success": true,
  "data": {
    "scenarios": [
      {
        "type": "conservative",
        "probability": 0.25,
        "runway_months": 8.5,
        "stress_level": "medium",
        "recommendation": "Build emergency fund"
      },
      {
        "type": "balanced",
        "probability": 0.50,
        "runway_months": 10.0,
        "stress_level": "low",
        "recommendation": "Continue current savings"
      },
      {
        "type": "aggressive",
        "probability": 0.25,
        "runway_months": 15.0,
        "stress_level": "low",
        "recommendation": "Pursue wealth building"
      }
    ]
  }
}
```

### POST `/api/v1/agents/analyze` (Existing)
Full financial analysis with synthesized recommendations

## 📊 Database Models

### FinancialDecision
Stores user's financial decisions and analysis results

```python
class FinancialDecision(Base):
    id: int
    user_id: int
    decision_id: str  # UUID
    decision_name: str
    description: str
    purchase_price: Decimal
    monthly_payment: Optional[Decimal]
    quantitative_analysis: JSON
    affordability_verdict: str
    confidence_score: float
    debate_record: Optional[JSON]
    user_acknowledged: bool
    actual_purchase: Optional[bool]
```

### DecisionAnalysis
Individual analysis components for each decision

```python
class DecisionAnalysis(Base):
    id: int
    decision_id: int
    analysis_type: str
    savings_rate: Optional[float]
    burn_rate: Optional[float]
    runway_months: Optional[float]
    assumptions: JSON
    confidence: float
```

## 🧮 Mathematical Foundations

### Savings Rate
```
savings_rate = (income - expenses) / income
confidence = 0.95 (with ±5% margin)
```

### Burn Rate
```
daily_burn = sum(expenses) / days
monthly_burn = daily_burn * 30
confidence = min(0.95, num_transactions / 100)
```

### Runway
```
runway_months = (balance - emergency_fund) / monthly_burn
confidence based on:
  - If runway < 1 month: 0.98 (very urgent)
  - If runway < 3 months: 0.90 (critical)
  - If runway < 6 months: 0.85 (important)
  - Otherwise: 0.80 (good)
```

### Scenario Multipliers

**Conservative**:
- Income: 0.85 (15% reduction)
- Expenses: 1.10 (10% increase) × trend_multiplier
- Job risk factor: 1.2-1.5

**Balanced**:
- Income: 1.0 (unchanged)
- Expenses: 1.0 × trend_multiplier
- Job risk factor: 1.0

**Aggressive**:
- Income: 1.20 (20% increase)
- Expenses: 0.85 (15% reduction)
- Job risk factor: 1.0

### Affordability Decision Rules

**Lump Sum Purchase**:
```
can_afford = (balance - purchase_price) >= emergency_fund
```

**Financed Purchase**:
```
can_afford = (monthly_payment <= surplus * 0.75) AND 
             (payment_to_income <= 0.20)
```

## 🎯 Example: "Can I afford iPhone for ₽120,000?"

### Input
```json
{
  "decision_name": "iPhone 15 Pro",
  "description": "Latest iPhone purchase",
  "purchase_price": 120000,
  "monthly_income": 150000,
  "monthly_expenses": 80000,
  "current_balance": 200000,
  "emergency_fund_target": 240000
}
```

### Analysis Flow
1. **Quantitative**: Savings rate = 46.7%, runway = 2.5 months before emergency fund
2. **Scenarios**: Conservative (can afford, stress=medium), Balanced (can afford, stress=low), Aggressive (can afford, stress=low)
3. **Affordability**: Can afford lump sum in all scenarios
4. **Debate**: Strategist says "good opportunity", Critic says "monitor emergency fund"
5. **Recommendation**: "recommended" with 82% confidence

### Output
```json
{
  "recommendation": {
    "level": "recommended",
    "confidence": 0.82,
    "reasoning": "Affordable in all scenarios | No critical impacts | Good balance of opportunity and safety",
    "concerns": [],
    "action_items": [
      "Can proceed with this purchase",
      "Consider financing to preserve cash flow",
      "Monitor spending for next 60 days"
    ]
  }
}
```

## 🔒 Security Considerations

- All financial calculations use `Decimal` for precision
- No sensitive data logged (only aggregates)
- Confidence scores prevent false certainty
- Assumptions tracked and disclosed
- No hardcoded thresholds (all configurable)

## 🧪 Testing

Comprehensive test suite covers:
- All quantitative metrics
- Scenario generation and comparison
- Probability calculations
- Decision analysis edge cases
- Integration scenarios

Run tests:
```bash
python -m pytest backend/tests/test_financial_reasoning.py -v
```

## 📈 Metrics & Monitoring

Each metric includes:
- **Value**: The calculated value
- **Bounds**: 95% confidence interval
- **Confidence**: 0-1 score
- **Method**: How it was calculated
- **Assumptions**: Key assumptions
- **Timestamp**: When calculated

## 🚀 Future Enhancements

1. **Extended Forecasting**: 6-12 month projections
2. **Goal Integration**: Link decisions to financial goals
3. **Behavioral Factors**: Incorporate psychological spending patterns
4. **What-If Analysis**: Interactive scenario planning
5. **Backtesting**: Validate recommendations against actual outcomes
6. **Machine Learning**: Learn from user decisions

## 📚 References

- Modern Portfolio Theory
- Value-at-Risk (VaR) analysis
- Monte Carlo simulation methods
- Behavioral economics
- Financial engineering principles
