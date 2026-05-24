# JimFinance System Architecture

## Overview

JimFinance is built using a modular, scalable architecture that separates concerns into distinct layers:

```
┌─────────────────────────────────────────────────────────┐
│              Frontend Layer                              │
│  (Next.js, TailwindCSS, Telegram Bot, Google Sheets)   │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│              API Layer (FastAPI)                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Authentication │ Users │ Accounts │ Transactions│   │
│  │ Categories │ Subscriptions │ Dashboard │ Reports │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│              Services Layer                              │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Transaction │ User │ Account │ Financial Memory  │   │
│  │ Services                                          │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│              Intelligence Layer                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ OCR Pipeline │ AI Agents │ Financial Reasoning  │   │
│  │ Categorization │ Anomaly Detection               │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│              Data Layer                                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │ PostgreSQL Database    │    Redis Cache           │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Architecture Components

### 1. Frontend Layer

#### Telegram Bot
- Entry point for transaction capture
- Handles expense logging
- Real-time feedback and analytics
- Multi-language support (Russian, English)

#### Web Dashboard (Planned)
- Built with Next.js + TypeScript
- Real-time data visualization
- Premium UI using shadcn/ui + TailwindCSS
- Dark/light mode support

#### Google Sheets Integration
- Source of truth for financial data
- Automatic bidirectional sync
- User data ownership
- Export and backup layer

### 2. API Layer

FastAPI provides high-performance REST endpoints:

```
/api/v1/
├── auth/          - Authentication & tokens
├── users/         - User management
├── accounts/      - Financial accounts
├── transactions/  - Transaction CRUD
├── categories/    - Category management
├── subscriptions/ - Subscription tracking
├── dashboard/     - Aggregated financial data
└── health         - Health check
```

**Features:**
- Automatic OpenAPI/Swagger documentation
- Request/response validation with Pydantic
- Dependency injection for clean code
- Async request handling
- CORS support

### 3. Services Layer

Business logic layer that handles:
- Transaction processing and categorization
- User account management
- Financial calculations
- Subscription monitoring
- Memory management

### 4. Intelligence Layer

#### OCR Pipeline
```
Image → Tesseract/PaddleOCR → Text Extraction → Normalization
```

#### Transaction Intelligence
```
Raw Input → Normalization → AI Classification → Enrichment → DB Storage
```

#### Multi-Agent Reasoning
```
Financial Data → Gemini Pro (Strategy) →  Analysis
              ↘ Groq (Critic/Risk)    ↙
                 ↓
            Synthesis Engine → Recommendations
```

#### Financial Memory
- Persistent behavioral patterns
- Spending insights
- Recurring patterns
- Anomaly detection

### 5. Data Layer

#### PostgreSQL
- Primary data store
- Normalized schema
- ACID compliance
- Full-text search capability

#### Redis
- Session caching
- Token blacklist
- Rate limiting
- Temporary data

## Data Flow

### Transaction Creation Flow

```
User Input (Telegram/Manual)
    ↓
OCR/Text Extraction (if image/PDF)
    ↓
Normalization (standardize format)
    ↓
AI Categorization (Gemini/Groq)
    ↓
Confidence Scoring
    ↓
Duplicate Detection
    ↓
Store in Database
    ↓
Update Financial Memory
    ↓
Trigger Analytics
```

### Financial Analysis Flow

```
Raw Transactions
    ↓
Aggregate by Category/Time Period
    ↓
Calculate Metrics (savings rate, burn rate, etc.)
    ↓
Gemini Pro Strategist Analysis
    ↓
Groq Critic Risk Assessment
    ↓
Synthesis Engine (confidence-weighted outputs)
    ↓
Generate Report/Recommendation
```

## Security Architecture

### Authentication
```
Credentials → Hash with bcrypt → Compare → Generate JWT
                                           ↓
                                    Access Token (short-lived)
                                    + Refresh Token (long-lived)
```

### Authorization
```
Request with JWT → Verify Signature → Extract User ID → Check Permissions
                                                        ↓
                                                    Allow/Deny Access
```

### Data Protection
- Passwords hashed with bcrypt
- Secrets stored in environment variables
- SQL injection prevention via ORM
- CORS and host validation
- HTTPS ready

## Scalability Considerations

### Horizontal Scaling
- Stateless API servers
- Shared PostgreSQL database
- Redis for distributed caching
- Telegram bot workers

### Database Optimization
- Indexed queries on frequent filters
- Normalized schema
- Partitioning for large tables (future)
- Read replicas (future)

### Caching Strategy
- User session caching in Redis
- Category and account caching
- Rate limiting with Redis
- Forecast result caching

## Performance Metrics

### Target Metrics
- API response time: <200ms (p95)
- Database query time: <50ms (p95)
- Transaction processing: <5s end-to-end
- Dashboard load: <2s

### Monitoring Points
- API endpoint response times
- Database query performance
- Error rates and types
- User transaction volume
- System resource utilization

## Deployment Architecture

### Local Development
```
Docker Compose
├── PostgreSQL Container
├── Redis Container
└── FastAPI Container (hot-reload)
```

### Production (Planned)
```
Kubernetes Cluster
├── FastAPI Pods (multiple replicas)
├── PostgreSQL (managed service)
├── Redis (managed service)
├── Ingress (API gateway)
└── Monitoring (Prometheus, Grafana)
```

## Integration Points

### External Services
1. **Gemini API** - Strategic financial reasoning
2. **Groq API** - Risk analysis and validation
3. **OpenAI API** - Reasoning layer
4. **Telegram Bot API** - Message handling
5. **Google Sheets API** - Data sync
6. **Google OAuth** - Authentication

### Webhook Handling
- Telegram message webhooks
- Bank notification processing
- Scheduled report generation

## Error Handling

### Strategy
- Graceful degradation for external API failures
- Retry logic with exponential backoff
- Comprehensive logging
- User-friendly error messages

### Error Categories
1. **Authentication Errors** - 401/403
2. **Validation Errors** - 422
3. **Not Found** - 404
4. **Server Errors** - 500
5. **Service Unavailable** - 503

## Future Enhancements

1. **GraphQL Layer** - For more flexible frontend queries
2. **Event Streaming** - Real-time transaction updates
3. **Machine Learning** - Advanced anomaly detection
4. **API Versioning** - Multiple API versions
5. **Rate Limiting** - Prevent abuse
6. **Advanced Caching** - EdgeCache for global access
