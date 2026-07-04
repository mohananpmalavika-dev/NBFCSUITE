# Contributing to NBFCSUITE

Thank you for your interest in contributing! This document outlines guidelines and workflows.

## Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** for your feature: `git checkout -b feature/my-feature`
4. **Make changes** following the guidelines below
5. **Commit** with clear messages: `git commit -m "Add feature X"`
6. **Push** to your fork: `git push origin feature/my-feature`
7. **Submit a Pull Request** with a clear description

## Development Guidelines

### Backend (Python / FastAPI)

**Code Style:**
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) (use `black` for formatting)
- Type hints on all functions
- Docstrings for all public functions/classes

**Testing:**
- Write tests alongside implementation (TDD preferred)
- Minimum 80% test coverage for new code
- Use `pytest` for unit/integration tests

**Structure:**
- Keep service logic in `services/{service-name}/app/`
- Database models in `models.py`
- Pydantic schemas in `schemas.py`
- Business logic in separate modules (e.g., `services.py`, `utils.py`)

**Example service structure:**
```
services/los/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── database.py          # DB connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── security.py          # Auth utilities
│   └── routes/
│       ├── applications.py  # Application endpoints
│       ├── documents.py     # Document endpoints
│       └── scorecards.py    # Scorecard endpoints
├── tests/
│   ├── test_applications.py
│   ├── test_documents.py
│   └── test_scorecards.py
├── requirements.txt
├── Dockerfile
└── README.md
```

### Frontend (Next.js / React)

**Code Style:**
- ESLint + Prettier configuration provided
- Functional components with hooks
- TypeScript for new code

**Structure:**
- Components in `components/`
- Pages in `pages/`
- API client in `lib/api.ts`
- Styles in component folders (CSS Modules)

### Mobile (Flutter)

- Follow [Dart style guide](https://dart.dev/guides/language/effective-dart/style)
- Organize by feature (feature folder structure)
- Use BLoC pattern for state management

## Service Implementation Checklist

When implementing a new service, follow this checklist:

- [ ] Create service folder in `services/{service-name}`
- [ ] Write OpenAPI spec in `design/openapi-{service}.yaml`
- [ ] Set up `app/models.py` (SQLAlchemy)
- [ ] Set up `app/schemas.py` (Pydantic)
- [ ] Implement endpoints in `app/main.py`
- [ ] Create `requirements.txt` with dependencies
- [ ] Create `Dockerfile`
- [ ] Add integration tests
- [ ] Write `README.md` with usage examples
- [ ] Update main `README.md` with service description
- [ ] Add Kubernetes manifests to `infra/k8s/{service}/`

## API Design Standards

- RESTful principles
- Consistent error responses:
  ```json
  {
    "error": {
      "code": "INVALID_REQUEST",
      "message": "Human-readable message",
      "details": {}
    }
  }
  ```
- Pagination for list endpoints: `?skip=0&limit=20`
- Filtering, sorting on list endpoints
- Versioning via URL: `/v1/resource` (if needed)

## Database Migration Guidelines

When modifying the schema:

1. Create a new migration file: `infra/migrations/XXX_description.sql`
2. Use `IF NOT EXISTS` / `IF EXISTS` for idempotency
3. Include indexes for frequently queried columns
4. Add foreign key constraints
5. Document breaking changes in the file
6. Test migrations locally before submitting

## Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_applications.py::test_create_application
```

## Commit Message Convention

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `chore:` Build, dependencies, tooling

Example:
```
feat: Add fraud detection scoring to LOS
fix: Correct EMI calculation for 60+ month loans
docs: Update API documentation for collections service
```

## Pull Request Process

1. **Update documentation** if adding/changing features
2. **Add tests** for new functionality
3. **Pass all CI checks** (linting, tests, coverage)
4. **Request review** from relevant maintainers
5. **Address feedback** and re-request review
6. **Squash commits** if requested by maintainers
7. Maintainer will **merge** once approved

## Code Review

When reviewing PRs:
- Check code quality & style compliance
- Verify tests are adequate
- Ensure documentation is clear
- Look for security issues
- Test locally if possible

## Reporting Issues

1. Check existing issues to avoid duplicates
2. Provide clear title and description
3. Include steps to reproduce (if bug)
4. Add logs/screenshots if applicable
5. Specify environment (OS, Python version, etc.)

## Questions?

- 📧 Email: `dev@nbfcsuite.io`
- 💬 Slack: `#nbfcsuite-dev`
- 📖 Docs: See `docs/` folder

Thank you for contributing! 🙌
