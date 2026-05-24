# JimFinance - AI-Native Personal Financial Operating System

A production-grade personal finance platform combining spreadsheet-native architecture, Telegram-first transaction capture, and multi-agent quantitative reasoning.

## 🎯 Vision

**"AI that deeply understands a person financially over years."**

JimFinance is an intelligent financial operating system designed for:
- International students
- Freelancers and remote workers
- Emerging market users
- Multi-currency individuals
- Financially conscious people seeking behavioral intelligence

## 🏗️ Architecture Overview

### Technology Stack

**Backend:**
- FastAPI (Python)
- PostgreSQL (primary database)
- Redis (caching)
- SQLAlchemy ORM

**AI/ML:**
- Google Gemini Pro (strategist agent)
- Groq (critic/risk agent)
- OpenAI (reasoning layer)
- Tesseract/PaddleOCR (document processing)

**Frontend (Planned):**
- Next.js 14 with TypeScript
- TailwindCSS + shadcn/ui
- Framer Motion
- Recharts

**Messaging:**
- Telegram Bot API
- Google Sheets Integration

**Infrastructure:**
- Docker & Docker Compose
- PostgreSQL + Redis
- Modular microservice architecture

## 📁 Project Structure

```
JimFinance/
├── backend/
│   ├── app/
│   │   ├── core/              # Configuration, security, logging
│   │   ├── db/                # Database setup and ORM
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── endpoints/  # API endpoints (auth, users, transactions, etc.)
│   │   ├── services/          # Business logic layer
│   │   ├── utils/             # Utilities (health checks, etc.)
│   │   └── ml/
│   │       ├── ocr/           # Document OCR pipeline
│   │       ├── transaction_intelligence/  # Transaction AI processing
│   │       └── agents/        # Multi-agent reasoning engine
│   ├── main.py                # FastAPI app entry point
│   ├── requirements.txt        # Python dependencies
│   └── migrations/             # Alembic database migrations
├── frontend/                  # (Planned) Next.js application
├── infra/                     # Infrastructure configuration
│   ├── docker/                # Dockerfile(s)
│   ├── kubernetes/            # K8s manifests (planned)
│   └── terraform/             # IaC (planned)
├── docs/                      # Documentation
├── docker-compose.yml         # Local development setup
├── .env.example               # Environment variables template
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 14+ (if running without Docker)

### Local Development with Docker

1. **Clone and setup:**
```bash
git clone https://github.com/Luffy-me/JimFinance.git
cd JimFinance
cp .env.example .env
```

2. **Start services:**
```bash
docker-compose up -d
```

3. **Access the application:**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Local Development without Docker

1. **Setup Python environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure database:**
```bash
# Create PostgreSQL database
createdb jimfinance

# Update .env with your database URL
DATABASE_URL=******localhost/jimfinance
```

3. **Run the application:**
```bash
cd backend
uvicorn main:app --reload
```

## 📚 Core Features (Phase 1)

### Authentication & Users
- User registration and login with JWT tokens
- Secure password hashing with bcrypt
- OAuth 2.0 ready (Google OAuth)
- User profile management

### Financial Accounts
- Multi-account support
- Multiple currencies (RUB, USD, EUR, INR, GBP)
- Different account types (checking, savings, credit card, investment, cash)
- Real-time balance tracking

### Transactions
- Transaction creation and categorization
- Merchant recognition
- Recurring transaction detection
- Confidence scoring for AI categorization
- Anomaly detection ready
- Multi-currency support

### Categories
- Customizable transaction categories
- Category type classification
- Color and icon support
- Default category templates

### Subscriptions
- Recurring subscription tracking
- Billing cycle management
- Automatic renewal configuration
- Subscription analytics

### Dashboard
- Financial overview
- Total balance aggregation
- Monthly income/expense calculation
- Savings rate calculation
- Financial runway estimation
- Recent transaction history
- Subscription overview
- Financial goals tracking

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - Logout user

### Users
- `GET /api/v1/users/me` - Current user info
- `PUT /api/v1/users/me` - Update user profile
- `GET /api/v1/users/{user_id}` - Get user by ID

### Accounts
- `POST /api/v1/accounts` - Create account
- `GET /api/v1/accounts` - List accounts
- `GET /api/v1/accounts/{account_id}` - Get account
- `PUT /api/v1/accounts/{account_id}` - Update account
- `DELETE /api/v1/accounts/{account_id}` - Delete account

### Transactions
- `POST /api/v1/transactions` - Create transaction
- `GET /api/v1/transactions` - List transactions
- `GET /api/v1/transactions/{transaction_id}` - Get transaction
- `PUT /api/v1/transactions/{transaction_id}` - Update transaction
- `DELETE /api/v1/transactions/{transaction_id}` - Delete transaction

### Categories
- `POST /api/v1/categories` - Create category
- `GET /api/v1/categories` - List categories
- `GET /api/v1/categories/{category_id}` - Get category
- `DELETE /api/v1/categories/{category_id}` - Delete category

### Subscriptions
- `POST /api/v1/subscriptions` - Create subscription
- `GET /api/v1/subscriptions` - List subscriptions
- `GET /api/v1/subscriptions/{subscription_id}` - Get subscription
- `PUT /api/v1/subscriptions/{subscription_id}` - Update subscription
- `DELETE /api/v1/subscriptions/{subscription_id}` - Delete subscription

### Dashboard
- `GET /api/v1/dashboard` - Get dashboard data and stats

### Health
- `GET /health` - Health check

## 🔐 Security Features

- JWT token-based authentication
- Password hashing with bcrypt
- CORS middleware
- Trusted host middleware
- SQL injection prevention via ORM
- Environment variable management
- Secure secret key handling
- OAuth 2.0 ready

## 📊 Database Schema

### Core Tables
- `users` - User accounts and profiles
- `accounts` - Financial accounts
- `transactions` - Individual transactions
- `categories` - Transaction categories
- `subscriptions` - Recurring subscriptions
- `financial_memory` - Behavioral insights
- `forecasts` - Financial projections
- `financial_goals` - User financial goals

## 🛣️ Roadmap

### Phase 2: Transaction Intelligence Engine
- OCR pipeline setup
- Transaction extraction and normalization
- Financial memory system
- Transaction categorization engine

### Phase 3: Telegram Bot
- Telegram bot setup
- Message handlers
- Expense capture
- Real-time feedback

### Phase 4: Multi-Agent Reasoning
- Gemini Pro Strategist
- Groq Critic/Risk Agent
- Synthesis Engine
- Financial calculations

### Phase 5: Dashboard Frontend
- Next.js application
- Dashboard UI
- Real-time updates
- Data visualization

### Phase 6: Advanced Features
- Google Sheets integration
- Purchase decision engine
- Weekly reporting
- Advanced analytics

### Phase 7: Production
- Docker containerization
- Security hardening
- Performance optimization
- Deployment setup

## 🧪 Testing

Run tests with pytest:
```bash
cd backend
pytest tests/
```

## 📝 Documentation

- [API Documentation](docs/API.md) - Detailed API reference
- [Architecture Design](docs/ARCHITECTURE.md) - System architecture
- [Database Schema](docs/DATABASE.md) - Database design
- [Development Guide](docs/DEVELOPMENT.md) - Contributing guide
- [Phase 2: Transaction Intelligence](docs/PHASE2_TRANSACTION_INTELLIGENCE.md) - Transaction engine documentation
- [Phase 3: Telegram Bot](docs/PHASE3_TELEGRAM_BOT.md) - Telegram bot features and API
- [Telegram Bot Setup](docs/TELEGRAM_BOT_SETUP.md) - Setup and deployment guide
- [Phase 3 Roadmap](docs/PHASE3_ROADMAP.md) - Remaining work for Phase 3
- [Phase 4: Multi-Agent Reasoning](docs/PHASE4_MULTI_AGENT_REASONING.md) - Multi-agent system documentation
- [Phase 4 Quick Reference](docs/PHASE4_QUICK_REFERENCE.md) - Quick reference guide

## 🤝 Contributing

This is a personal project built with production-grade standards. Contributions welcome!

## 📄 License

MIT License - see LICENSE file for details

## 👤 Author

Built with ❤️ by [Luffy-me](https://github.com/Luffy-me)

## 📞 Support

For issues and questions:
- GitHub Issues: [Report a Bug](https://github.com/Luffy-me/JimFinance/issues)
- Documentation: Check the [docs/](docs/) folder

---

**Status:** 🚀 Phase 3 - Telegram Bot (In Progress)
