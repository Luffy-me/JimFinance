# JimFinance Development Guide

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Git

### Initial Setup

1. **Clone repository:**
```bash
git clone https://github.com/Luffy-me/JimFinance.git
cd JimFinance
```

2. **Create virtual environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp ../.env.example ../.env
# Edit .env with your settings
```

5. **Setup database:**
```bash
# Create PostgreSQL database
createdb jimfinance

# Update DATABASE_URL in .env
DATABASE_URL=******localhost/jimfinance
```

6. **Run the application:**
```bash
uvicorn main:app --reload
```

Access the API at `http://localhost:8000`

## Development with Docker

### Quick Start
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f backend
```

### Access Services
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Rebuild Services
```bash
docker-compose up --build
```

### Stop Services
```bash
docker-compose down
```

### Reset Database
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d    # Recreate
```

## Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          # Settings and environment
│   │   ├── logging.py         # Logging setup
│   │   └── security.py        # Auth and encryption
│   ├── db/
│   │   └── base.py            # Database setup
│   ├── models/
│   │   └── database.py        # SQLAlchemy models
│   ├── schemas/
│   │   └── __init__.py        # Pydantic schemas
│   ├── api/v1/
│   │   ├── router.py          # Main API router
│   │   └── endpoints/
│   │       ├── auth.py        # Auth endpoints
│   │       ├── users.py       # User endpoints
│   │       ├── accounts.py    # Account endpoints
│   │       ├── transactions.py # Transaction endpoints
│   │       ├── categories.py  # Category endpoints
│   │       ├── subscriptions.py # Subscription endpoints
│   │       └── dashboard.py   # Dashboard endpoints
│   ├── services/              # Business logic
│   ├── utils/
│   │   └── health.py          # Health checks
│   └── ml/                    # AI/ML services
├── main.py                    # FastAPI app entry
├── requirements.txt           # Dependencies
└── migrations/                # Alembic migrations
```

## Database Migrations

### Create Migration

```bash
cd backend
alembic revision --autogenerate -m "Add new column"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback

```bash
alembic downgrade -1
```

## Running Tests

### Run All Tests
```bash
cd backend
pytest
```

### Run Specific Test
```bash
pytest tests/test_auth.py
```

### Run with Coverage
```bash
pytest --cov=app tests/
```

### Run in Watch Mode
```bash
pytest-watch
```

## Code Style

### Format Code
```bash
black app/
isort app/
```

### Lint Code
```bash
flake8 app/
```

### Type Check
```bash
mypy app/
```

### Pre-commit Hook
```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
EOF

# Install hooks
pre-commit install
```

## Environment Variables

### Required
```
DATABASE_URL=******localhost:5432/jimfinance
SECRET_KEY=your-super-secret-key
TELEGRAM_BOT_TOKEN=your-token
```

### Optional
```
GEMINI_API_KEY=your-key
GROQ_API_KEY=your-key
OPENAI_API_KEY=your-key
GOOGLE_OAUTH_CLIENT_ID=your-id
```

## Common Commands

### Backend Development
```bash
# Terminal 1: Run server
cd backend
uvicorn main:app --reload

# Terminal 2: Run Celery (future)
celery -A app.tasks worker --loglevel=info
```

### Database
```bash
# Connect to database
psql jimfinance

# Backup database
pg_dump jimfinance > backup.sql

# Restore database
psql jimfinance < backup.sql
```

### Redis
```bash
# Connect to Redis
redis-cli

# Monitor Redis
redis-cli monitor

# Flush all data
redis-cli FLUSHALL
```

## Debugging

### FastAPI Debug Mode
```bash
DEBUG=true uvicorn main:app --reload
```

### PDB Debugging
```python
import pdb; pdb.set_trace()
```

### Logging
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Message")
logger.error("Error message")
```

### Database Queries
```python
# In SQLAlchemy, enable SQL logging
from sqlalchemy.pool import StaticPool
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log all queries
)
```

## API Testing

### Using curl
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email":"user@example.com",
    "username":"user",
    "password":"password"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email":"user@example.com",
    "password":"password"
  }'

# Get user (with token)
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: ******"
```

### Using Swagger UI
Navigate to http://localhost:8000/docs and use the interactive UI

### Using Thunder Client / Postman
Import the Swagger spec: http://localhost:8000/openapi.json

## Deployment

### Build Docker Image
```bash
docker build -f infra/docker/Dockerfile.backend -t jimfinance:latest .
```

### Push to Registry
```bash
docker tag jimfinance:latest registry.example.com/jimfinance:latest
docker push registry.example.com/jimfinance:latest
```

### Deploy to Production
(Documentation coming in Phase 7)

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
psql -h localhost -U jimfinance -d jimfinance
```

### Redis Connection Issues
```bash
# Check Redis is running
redis-cli ping  # Should return PONG

# Check Redis info
redis-cli info
```

### Import Errors
```bash
# Verify all modules are installed
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

## Contributing

### Code Standards
- Follow PEP 8 style guide
- Use type hints for functions
- Write docstrings for modules, classes, functions
- Add tests for new features
- Use descriptive commit messages

### Pull Request Process
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests and linting
5. Commit: `git commit -am 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Create Pull Request

### Commit Message Format
```
<type>: <subject>

<body>

<footer>
```

**Types:** feat, fix, docs, style, refactor, test, chore

**Example:**
```
feat: Add transaction categorization

- Implement AI-based transaction categorization
- Add confidence scoring
- Integrate with Gemini API

Closes #42
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Python Best Practices](https://pep8.org/)

## Support

For questions or issues:
- Check the [README.md](../README.md)
- Review the [ARCHITECTURE.md](./ARCHITECTURE.md)
- Check [DATABASE.md](./DATABASE.md)
- Open a GitHub issue
