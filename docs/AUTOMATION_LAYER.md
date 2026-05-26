# JimFinance Automation & Proactive Intelligence Layer

## Overview

The Automation & Proactive Intelligence Layer transforms JimFinance from a reactive financial tool into a proactive AI assistant that continuously monitors your finances and sends intelligent, low-fatigue notifications.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   JimFinance User                               │
│              (Receives Notifications)                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
        ┌───────▼────────┐      ┌────────▼─────────┐
        │ Telegram Bot   │      │   Dashboard      │
        │ (Real-time)    │      │   (Web UI)       │
        └────────────────┘      └──────────────────┘
                │                        │
                └────────────┬───────────┘
                             │
        ┌────────────────────▼────────────────────┐
        │    Notification Delivery Service        │
        │  (Throttling, Deduplication, Channel)  │
        └────────────────────┬────────────────────┘
                             │
        ┌────────────────────▼────────────────────┐
        │    Automation & Alert Engine Layer      │
        │                                        │
        │  ┌──────────────────────────────────┐ │
        │  │ Alert Detection Engine           │ │
        │  │ - Spending Anomalies             │ │
        │  │ - Burn Rate Warnings             │ │
        │  │ - Subscription Waste             │ │
        │  │ - Behavioral Anomalies           │ │
        │  │ - Savings Opportunities          │ │
        │  └──────────────────────────────────┘ │
        │                                        │
        │  ┌──────────────────────────────────┐ │
        │  │ Report Generation Engine         │ │
        │  │ - Weekly Financial Reports       │ │
        │  │ - AI Analysis & Insights         │ │
        │  │ - Recommendations                │ │
        │  └──────────────────────────────────┘ │
        │                                        │
        │  ┌──────────────────────────────────┐ │
        │  │ Financial Health Scoring         │ │
        │  │ - Composite Score (0-100)        │ │
        │  │ - Risk Assessment                │ │
        │  │ - Trend Analysis                 │ │
        │  └──────────────────────────────────┘ │
        └────────────────────┬────────────────────┘
                             │
        ┌────────────────────▼────────────────────┐
        │    Celery Task Queue & Scheduler        │
        │  (Redis Backend)                       │
        │                                        │
        │  ┌──────────────────────────────────┐ │
        │  │ Scheduled Tasks (Celery Beat)    │ │
        │  │ - Daily: Spending Alerts @ 9am   │ │
        │  │ - Weekly: Reports @ Mon 8am      │ │
        │  │ - Daily: Burn Rate @ 8:30am      │ │
        │  └──────────────────────────────────┘ │
        └────────────────────┬────────────────────┘
                             │
        ┌────────────────────▼────────────────────┐
        │    Data Layer (PostgreSQL + Redis)      │
        │  - Transaction History                 │
        │  - User Preferences                    │
        │  - Notification Logs                   │
        │  - Automation Rules                    │
        └────────────────────────────────────────┘
```

## Key Features

### 1. Financial Health Scoring (0-100)

**Components:**
- **Savings Rate** (20% weight): Goal 30%+ of income
- **Cash Flow Stability** (20% weight): Low volatility preferred
- **Expense Trends** (15% weight): Stable or decreasing
- **Runway Health** (25% weight): 6+ months of expenses
- **Subscription Efficiency** (10% weight): <10% of monthly expenses
- **Emergency Fund** (10% weight): 6 months of expenses target

**Grade Scale:**
- A+ (95-100): Exceptional financial health
- A (90-94): Excellent
- B+ (80-89): Good
- C (60-79): Fair - needs improvement
- D (40-59): Poor - significant concerns
- F (<40): Critical - immediate action needed

### 2. Alert Types

#### Spending Anomalies
- **Week-over-week changes**: 40%+ increase in any category
- **Threshold**: Configurable per category
- **Example**: "Taxi spending increased 41% this week"

#### Burn Rate Warnings
- **Low Runway**: <3 months of expenses
- **High Burn Rate**: Spending >90% of income
- **Example**: "Your current burn rate reduces runway to 4.2 months"

#### Subscription Waste
- **Unused Subscriptions**: Not accessed in 30+ days
- **High Subscription %**: >15% of monthly expenses
- **Example**: "Netflix hasn't been used in 45 days"

#### Behavioral Anomalies
- **Unusual Patterns**: 2+ std dev from baseline
- **Triggers**: Weekend, post-paycheck, stress periods
- **Example**: "Your spending this week is 150% above average"

#### Savings Opportunities
- **Consolidation**: Multiple purchases from same merchant
- **Discretionary Cuts**: Non-essential spending opportunities
- **Negotiation**: Annual subscription discounts
- **Example**: "You could save $50/month by negotiating Netflix"

### 3. Weekly Financial Reports

**Components:**
- Executive Summary (AI-generated)
- Key Metrics Dashboard
- Spending Analysis by Category
- Top Merchants
- Trend Analysis
- Health Score & Risk Assessment
- Top 5 Recommendations
- Active Alerts Summary
- Charts & Visualizations
- PDF Export for offline viewing

**Example Report Data:**
```json
{
  "report_id": "report_2024_02_26",
  "period": "2024-02-19 to 2024-02-25",
  "summary": "Your financial health is good this week...",
  "key_metrics": {
    "health_score": 78,
    "health_grade": "B+",
    "weekly_spending": "$547.50",
    "spending_trend": "stable",
    "spending_change": "-5%"
  },
  "recommendations": [
    {
      "category": "Subscriptions",
      "recommendation": "Review unused subscriptions",
      "confidence": 0.85,
      "priority": "medium"
    }
  ]
}
```

### 4. Notification System

**Features:**
- **Multi-Channel Delivery**: Telegram, Email, In-App
- **Intelligent Throttling**: Configurable per alert type
  - Spending spikes: 3/day max
  - Burn rate warnings: 2/day max
  - Subscription waste: 1/day max
- **Deduplication**: 60-1440 min windows per alert type
- **Quiet Hours**: Custom do-not-disturb times
- **Confidence Filtering**: Minimum confidence threshold
- **Digest Mode**: Batch notifications at preferred times

**Default Thresholds:**
```python
THROTTLE_CONFIG = {
    "spending_spike": 3,           # 3 alerts per day
    "burn_rate_warning": 2,        # 2 alerts per day
    "subscription_waste": 1,       # 1 alert per day
    "savings_opportunity": 2,      # 2 alerts per day
    "behavioral_anomaly": 3,       # 3 alerts per day
    "low_runway": 1,               # 1 alert per day
    "high_volatility": 2,          # 2 alerts per day
}
```

### 5. Automation Rules Engine

**Capabilities:**
- Create custom alert conditions
- Trigger notifications on specific patterns
- Auto-categorize transactions
- Archive or flag specific merchants
- Schedule recurring reports

**Example Rule:**
```json
{
  "name": "High Travel Spending Alert",
  "condition_type": "spending_spike",
  "condition_value": {
    "category": "transport",
    "threshold": 0.5,
    "period": "weekly"
  },
  "action_type": "notify",
  "action_value": {
    "channels": ["telegram"],
    "severity": "warning"
  }
}
```

## API Endpoints

### Reports
- `GET /api/v1/automation/reports` - List reports
- `GET /api/v1/automation/reports/{report_id}` - Get detailed report
- `GET /api/v1/automation/reports/{report_id}/pdf` - Download PDF

### Alerts
- `GET /api/v1/automation/alerts` - List active alerts
- `POST /api/v1/automation/alerts/{alert_id}/acknowledge` - Mark alert as acknowledged
- `GET /api/v1/automation/alerts/summary` - Get alert counts

### Preferences
- `GET /api/v1/automation/preferences` - Get notification preferences
- `PUT /api/v1/automation/preferences` - Update preferences

### Automation Rules
- `GET /api/v1/automation/rules` - List rules
- `POST /api/v1/automation/rules` - Create rule
- `PUT /api/v1/automation/rules/{rule_id}` - Update rule
- `DELETE /api/v1/automation/rules/{rule_id}` - Delete rule

### Dashboard
- `GET /api/v1/automation/dashboard` - Get automation dashboard summary

## Celery Tasks

### Scheduled Tasks (Celery Beat)

```python
{
    "daily-spending-alerts": {
        "task": "app.tasks.alerts.check_daily_spending_alerts",
        "schedule": crontab(hour=9, minute=0),  # 9 AM UTC
    },
    "weekly-financial-reports": {
        "task": "app.tasks.reports.generate_weekly_reports",
        "schedule": crontab(day_of_week=1, hour=8, minute=0),  # Monday 8 AM UTC
    },
    "subscription-waste-check": {
        "task": "app.tasks.alerts.check_subscription_waste",
        "schedule": crontab(day_of_week=6, hour=10, minute=0),  # Sunday 10 AM UTC
    },
    "burn-rate-warnings": {
        "task": "app.tasks.alerts.check_burn_rate",
        "schedule": crontab(hour=8, minute=30),  # Daily 8:30 AM UTC
    },
    "behavioral-alerts": {
        "task": "app.tasks.alerts.check_behavioral_anomalies",
        "schedule": crontab(hour=9, minute=30),  # Daily 9:30 AM UTC
    },
    "savings-opportunities": {
        "task": "app.tasks.alerts.detect_savings_opportunities",
        "schedule": crontab(day_of_week=4, hour=7, minute=0),  # Friday 7 AM UTC
    },
}
```

### On-Demand Tasks

- `send_telegram_notification` - Send individual notification
- `send_report_via_telegram` - Send report with PDF
- `send_batch_notifications` - Send multiple notifications

## Database Models

### New Models Added

1. **Notification** - Tracks all notifications sent
2. **UserNotificationPreference** - User alert settings
3. **FinancialAlert** - Detected alerts
4. **FinancialReport** - Generated reports
5. **ReportDelivery** - Report delivery tracking
6. **AutomationRule** - Custom automation rules
7. **TelegramUserMapping** - Telegram account linking
8. **NotificationDeliveryLog** - Delivery attempt history

## Configuration

### Environment Variables

```env
# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook

# Notification Preferences (Defaults)
NOTIFICATION_MIN_CONFIDENCE=0.5
NOTIFICATION_THROTTLE_ENABLED=true
NOTIFICATION_QUIET_HOURS_ENABLED=false
```

### Configuration Classes

**FinancialHealthScoringEngine**
```python
COMPONENT_WEIGHTS = {
    "savings_rate": 0.20,
    "cash_flow_stability": 0.20,
    "expense_trends": 0.15,
    "runway_health": 0.25,
    "subscription_efficiency": 0.10,
    "emergency_fund": 0.10,
}
```

**AlertDetectionEngine**
```python
THROTTLE_CONFIG = {...}  # Max alerts per day per type
DEDUPLICATION_WINDOW = {...}  # Time between similar alerts
```

## Usage Examples

### 1. Generate Weekly Report

```python
from app.services.report_generation import ReportGenerator
from app.services.pdf_generation import PDFReportGenerator

report_gen = ReportGenerator()
pdf_gen = PDFReportGenerator()

# Generate report
report = report_gen.generate_weekly_report(
    user_id="user123",
    transactions=user_transactions,
    account_balance=Decimal("5000"),
    monthly_income=5000,
)

# Generate PDF
pdf_bytes = pdf_gen.generate_weekly_report_pdf(report)

# Save or deliver PDF
with open("report.pdf", "wb") as f:
    f.write(pdf_bytes)
```

### 2. Check for Alerts

```python
from app.ml.alerts import AlertDetectionEngine
from app.services.notifications import NotificationService

alert_engine = AlertDetectionEngine()
notif_service = NotificationService()

# Detect all alerts
alerts = alert_engine.detect_all_alerts(
    user_id="user123",
    transactions=transactions,
    account_balance=Decimal("5000"),
    monthly_income=5000,
    subscriptions=subscriptions,
)

# Queue notifications (with throttling/dedup)
notifications = notif_service.queue_notifications(
    user_id="user123",
    alerts=alerts,
    user_preferences=preferences,
)

# Send via Telegram
for notif in notifications:
    send_telegram_notification.delay(
        user_id="user123",
        notification_dict=notif.__dict__,
    )
```

### 3. Calculate Financial Health

```python
from app.ml.financial_scoring import FinancialHealthScoringEngine

scoring = FinancialHealthScoringEngine()

score = scoring.calculate_health_score(
    transactions=transactions,
    account_balance=Decimal("10000"),
    monthly_income=5000,
    monthly_expenses=1500,
    subscriptions=subscriptions,
)

print(f"Health Score: {score.overall_score}/100 ({score.score_grade})")
print(f"Risk Level: {score.risk_level}")
for insight in score.insights:
    print(f"- {insight}")
for rec in score.recommendations:
    print(f"✓ {rec}")
```

## Performance Considerations

### Scaling

- **Report Generation**: Can be distributed across workers
- **Alert Checks**: Parallelized by user
- **Notification Delivery**: Rate-limited to prevent API throttling
- **Database**: Use indexes on frequently queried columns

### Optimization

- Cache historical metrics (1-week TTL)
- Batch notifications to reduce message count
- Use Redis for deduplication/throttling
- Archive old notifications (>30 days)

## Security & Privacy

### Data Protection

- Never store sensitive transaction details in logs
- Encrypt notification content at rest
- Use TLS for Telegram delivery
- User isolation via user_id foreign keys

### Rate Limiting

- API endpoints: 100 requests/hour per user
- Celery tasks: Built-in retry with exponential backoff
- Telegram: Rate limit to 30 messages/second

### Audit Trail

- Log all alert deliveries
- Track notification acknowledgments
- Record preference changes
- Monitor failed delivery attempts

## Testing

Run the test suite:

```bash
pytest backend/tests/test_automation_layer.py -v

# Specific test class
pytest backend/tests/test_automation_layer.py::TestFinancialHealthScoring -v

# With coverage
pytest backend/tests/test_automation_layer.py --cov=app.ml --cov=app.services.notifications
```

## Future Enhancements

1. **Machine Learning Personalization**
   - Learn individual spending patterns
   - Personalized alert thresholds
   - Anomaly detection using statistical models

2. **Advanced Analytics**
   - Peer benchmarking (anonymized)
   - Predictive financial planning
   - "What-if" scenario analysis

3. **Integrations**
   - Multi-language support
   - SMS delivery
   - WhatsApp integration
   - Calendar integration for budget planning

4. **Advanced Automation**
   - Auto-categorization of new merchants
   - Smart rule templates
   - Workflow automation (e.g., "If spending > threshold, notify and archive")

5. **Reports**
   - Monthly financial summaries
   - Year-end tax summaries
   - Custom report builder
   - Export to Excel/CSV

## Troubleshooting

### Celery Tasks Not Running

```bash
# Check Celery worker status
celery -A app.core.celery inspect active

# Check pending tasks
celery -A app.core.celery inspect reserved

# View Celery logs
celery -A app.core.celery worker --loglevel=debug
```

### Notifications Not Sending

1. Check Telegram bot token in `.env`
2. Verify user telegram_user_id mapping
3. Check notification preferences (enabled/disabled)
4. Check notification queue: `SELECT * FROM notifications WHERE status='pending'`

### Reports Not Generating

1. Verify Celery beat scheduler is running
2. Check transaction data exists: `SELECT COUNT(*) FROM transactions`
3. Check Celery task logs
4. Verify database migrations completed

## Support & Documentation

- [API Documentation](./api_docs.md)
- [Celery Documentation](https://docs.celeryproject.org/)
- [ReportLab Documentation](https://www.reportlab.com/)
- [Python Telegram Bot](https://python-telegram-bot.readthedocs.io/)

---

**Version**: 1.0.0
**Last Updated**: 2026-05-26
**Status**: Production Ready
