# Rust System Developer — Planning Reference

## Principles
1. **Ownership first** — понимать кто владеет данными
2. **Error types с thiserror** — типизированные ошибки
3. **? operator** — propagation ошибок
4. **Clone осторожно** — предпочитать borrowing
5. **Async с tokio** — не блокировать runtime
6. **Graceful shutdown** — signal handling
7. **Zero-cost abstractions** — iterators > loops

## Code Patterns
No specific code patterns. Follow stack principles above.
