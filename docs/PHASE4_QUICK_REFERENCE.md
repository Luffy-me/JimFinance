# Phase 4: Multi-Agent Reasoning - Quick Reference

## 🚀 Quick Start

### 1. Setup Environment Variables
```bash
# .env file
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

### 2. Run Analysis
```bash
# Full analysis
curl -X POST http://localhost:8000/api/v1/agents/analyze?days=30

# Strategy only
curl -X GET http://localhost:8000/api/v1/agents/strategy?days=30

# Risk assessment
curl -X GET http://localhost:8000/api/v1/agents/risk-assessment?days=30

# Health check
curl -X GET http://localhost:8000/api/v1/agents/health
```

### 3. API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/agents/analyze` | POST | Full financial analysis (Strategist + Critic) |
| `/api/v1/agents/strategy` | GET | Strategy recommendations only |
| `/api/v1/agents/risk-assessment` | GET | Risk analysis only |
| `/api/v1/agents/health` | GET | Health check of agents |
| `/api/v1/agents/stats` | GET | Performance statistics |

## 📊 Agent Capabilities

### Strategist Agent (Gemini Pro)
- Spending pattern analysis
- Budget optimization recommendations
- Savings opportunities identification
- Financial goals suggestions
- Personalized strategies

### Critic Agent (Groq)
- Risk level assessment (low/medium/high/critical)
- Financial health scoring (0-100)
- Vulnerability identification
- Alert generation
- Emergency fund adequacy checking

### Synthesis Engine
- Combines both perspectives
- Generates executive summary
- Creates prioritized action items
- Calculates overall confidence
- Produces comprehensive insights

## 🔧 Development

### Run Tests
```bash
cd backend
pytest tests/test_agents.py -v
pytest tests/test_agent_api.py -v
```

### Add New Agent
1. Extend `BaseAgent` class
2. Implement `analyze()` method
3. Create type definitions for output
4. Add tests
5. Register in `AgentService`

### Understanding Output Format

**StrategistOutput:**
```python
{
    "recommendations": ["actionable recommendations"],
    "budget_suggestions": {"category": amount},
    "savings_opportunities": [{"area": ..., "monthly_savings": ...}],
    "goals_suggestions": [{"goal": ..., "timeline_months": ...}],
    "spending_analysis": {...},
    "confidence_score": 0.85
}
```

**CriticOutput:**
```python
{
    "risk_level": "high",  # low, medium, high, critical
    "risk_score": 72,  # 0-100
    "vulnerabilities": [...],
    "alerts": [...],
    "financial_health_score": 65,  # 0-100
    "critical_issues": [...],
    "recommendations": [...],
    "confidence_score": 0.80
}
```

**SynthesisOutput:**
```python
{
    "executive_summary": "Combined analysis summary",
    "key_insights": [...],
    "action_items": [...],
    "priority_level": "high",  # critical, high, medium, low
    "strategist_perspective": {...},
    "critic_perspective": {...},
    "overall_confidence": 0.825
}
```

## 💡 Usage Examples

### Example 1: Get Financial Analysis
```python
from app.services.agent_service import AgentService
from sqlalchemy.orm import Session

service = AgentService()

# In an async function
synthesis = await service.analyze_user_finances(
    user_id=1,
    db=session,
    days=30
)

# Access results
print(synthesis.executive_summary)
print(synthesis.key_insights)
print(synthesis.action_items)
```

### Example 2: Check Agent Health
```python
from app.services.agent_service import AgentService

service = AgentService()
stats = service.get_agent_stats()

if stats["strategist"]["successful_calls"] > 0:
    print("Strategist is working")

if stats["critic"]["successful_calls"] > 0:
    print("Critic is working")
```

### Example 3: Get Strategy Recommendations
```python
# GET /api/v1/agents/strategy?days=30
# Returns strategist output with budget suggestions and recommendations
```

## 🔐 Security Notes

1. API keys stored in environment variables only
2. Never expose keys in logs or error messages
3. User data scoped per user
4. Input validation on all endpoints
5. Error messages sanitized

## 📈 Performance Tips

1. Cache results for 1 hour
2. Use smaller date ranges for faster analysis (7-14 days)
3. Parallel agent execution possible (both agents run independently)
4. Database query optimization: add indexes on user_id and transaction_date

## 🐛 Troubleshooting

### "Service not available"
- Check if GEMINI_API_KEY or GROQ_API_KEY are set
- Verify API keys are valid
- Check network connectivity

### "Insufficient financial data"
- Ensure user has transactions in the period
- Try extending days parameter
- Create sample transactions for testing

### "Analysis failed"
- Check logs for detailed error message
- Verify API service status
- Try again (may be temporary timeout)

## 📚 Related Documentation

- [Phase 4 Full Documentation](./PHASE4_MULTI_AGENT_REASONING.md)
- [Phase 2 Transaction Intelligence](./PHASE2_TRANSACTION_INTELLIGENCE.md)
- [Phase 3 Telegram Bot](./PHASE3_TELEGRAM_BOT.md)

## 🎯 Next Steps

1. **Phase 4.2**: Add database models for storing insights
2. **Phase 4.3**: Implement caching with Redis
3. **Phase 4.4**: Telegram Bot integration
4. **Phase 4.5**: Dashboard integration
5. **Phase 4.6**: Advanced features (predictions, trends)

---

**Version**: 0.1.0  
**Status**: Phase 4.1 Complete ✅  
**Last Updated**: May 24, 2024
