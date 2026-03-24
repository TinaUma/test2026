# FastAPI Expert — Planning Reference

## Principles
1. **Async everywhere** — await for I/O, sync only for CPU-bound
2. **Pydantic schemas** — validate input and output
3. **Dependency Injection** — use Depends() for dependencies
4. **Repository pattern** — separate business logic from data access
5. **defer() for heavy fields** — embeddings, large JSON
6. **selectinload()** — prevent N+1 queries
7. **Explicit transactions** — async with session.begin()

## Code Patterns

### Router Definition
```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, UserResponse
from app.services.user import UserService

router = APIRouter(prefix="/v1/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    service: UserService = Depends()
) -> UserResponse:
    return await service.create(data)
```

### Service with Repository
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, defer

class UserService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def get_with_relations(self, user_id: int):
        stmt = (
            select(User)
            .options(
                selectinload(User.posts),
                defer(User.large_json_field)
            )
            .where(User.id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
```
