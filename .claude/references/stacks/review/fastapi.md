# FastAPI Expert — Review Checklist

### API
- [ ] Endpoints versioned (/v1/)
- [ ] Request/Response via Pydantic schemas
- [ ] HTTP status codes correct (201 create, 204 delete)
- [ ] OpenAPI documentation current

### Database
- [ ] defer() on heavy fields
- [ ] selectinload() for relationships
- [ ] Indexes on frequently filtered columns
- [ ] Alembic migrations created

### Async
- [ ] No blocking calls in async functions
- [ ] Background tasks via Celery
- [ ] Connection pooling configured
- [ ] Timeouts on external requests

### Security
- [ ] Input validated
- [ ] SQL injection impossible (ORM/params)
- [ ] Authorization on every endpoint
- [ ] Sensitive data not in logs
