# Node.js Backend Expert — Planning Reference

## Principles
1. **Async/await везде** — никаких callback hell
2. **Zod валидация** — схемы на входе
3. **Service layer** — бизнес-логика отдельно от handlers
4. **Централизованные ошибки** — AppError класс + global handler
5. **Structured logging** — pino с контекстом
6. **Graceful shutdown** — правильное завершение
7. **Environment validation** — проверка env на старте

## Code Patterns
No specific code patterns. Follow stack principles above.
