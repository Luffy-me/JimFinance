# Contributing to JimFinance

Thank you for your interest in contributing to JimFinance! We welcome contributions of all kinds.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

### 1. Fork the Repository

```bash
git clone https://github.com/Luffy-me/JimFinance.git
cd JimFinance
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Set Up Development Environment

Follow [QUICKSTART.md](./QUICKSTART.md)

## Development Guidelines

### Code Style

#### Python
- Use Black for formatting
- Follow PEP 8
- Type hints for all functions
- Docstrings for all modules/functions

```python
def calculate_savings_rate(income: float, expenses: float) -> float:
    """
    Calculate savings rate as a percentage.
    
    Args:
        income: Monthly income
        expenses: Monthly expenses
        
    Returns:
        Savings rate as percentage (0-100)
    """
    if income == 0:
        return 0.0
    return ((income - expenses) / income) * 100
```

#### TypeScript
- Use ESLint and Prettier
- Strict type checking
- Meaningful variable names

```typescript
interface Transaction {
  id: number
  amount: number
  merchant: string
  category: TransactionCategory
  date: Date
}

function calculateTotalByCategory(
  transactions: Transaction[],
  category: TransactionCategory
): number {
  return transactions
    .filter((t) => t.category === category)
    .reduce((sum, t) => sum + t.amount, 0)
}
```

### Commit Messages

Follow conventional commits:

```
type(scope): subject

- type: feat, fix, docs, style, refactor, perf, test
- scope: feature area (auth, transactions, dashboard, etc.)
- subject: lowercase, present tense, no period
```

Examples:
- `feat(auth): add JWT token refresh endpoint`
- `fix(transactions): prevent duplicate detection false positives`
- `docs(readme): update installation instructions`

### Testing

Write tests for all new features:

```python
def test_calculate_savings_rate():
    """Test savings rate calculation."""
    assert calculate_savings_rate(5000, 2000) == 60.0
    assert calculate_savings_rate(5000, 0) == 100.0
    assert calculate_savings_rate(0, 2000) == 0.0
```

Run tests before submitting:

```bash
pytest backend/tests
npm run test
```

### Pull Request Process

1. Update documentation
2. Add tests for new features
3. Run linting and type checking
4. Create descriptive PR title and description
5. Link related issues
6. Wait for code review

#### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Related Issues
Closes #123

## Testing
Describe how to test changes

## Checklist
- [ ] Tests pass
- [ ] Code is formatted
- [ ] Documentation updated
- [ ] No breaking changes
```

## Architecture Guidelines

### Backend

- **Services**: Business logic layer
- **Routes**: API endpoints
- **Models**: Database ORM models
- **Schemas**: Request/response validation
- **Core**: Configuration, security, database

Structure:
```
backend/app/
├── api/v1/endpoints/  # Route handlers
├── models.py          # SQLAlchemy models
├── schemas.py         # Pydantic schemas
├── services/          # Business logic
├── agents/            # AI agents
├── workers/           # Background jobs
└── core/              # Config, security
```

### Frontend

- **Minimal component hierarchy**
- **Reusable UI components**
- **Zustand for state management**
- **Hooks for custom logic**

Structure:
```
frontend/
├── app/               # Next.js routes
├── components/        # React components
├── lib/              # Utilities, stores
├── types/            # TypeScript types
└── styles/           # Global styles
```

## Performance Considerations

- **Pagination**: Default 50, max 100 items
- **Caching**: Use Redis for expensive queries
- **Indexing**: Add DB indexes for frequently queried fields
- **Lazy Loading**: Load related data on demand
- **Client-side**: Code split, image optimization

## Security

- Validate all inputs
- Use parameterized queries
- Hash passwords with bcrypt
- Rotate secrets regularly
- Audit sensitive operations
- Never commit secrets

## Documentation

Write documentation for:
- New endpoints
- Complex algorithms
- Configuration options
- User-facing features

Update:
- README.md
- API_REFERENCE.md
- ARCHITECTURE.md
- Code comments

## Release Process

1. Update version number
2. Update CHANGELOG
3. Create git tag
4. Push to main branch
5. Create GitHub release

Versions follow Semantic Versioning (MAJOR.MINOR.PATCH)

## Questions?

- Check existing documentation
- Review similar implementations
- Open a discussion issue
- Ask in pull request comments

---

**Thank you for contributing!**
