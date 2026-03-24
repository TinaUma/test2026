# Rust System Developer — Review Checklist

### Ownership
- [ ] Proper borrowing vs cloning
- [ ] Lifetimes explicit где нужно
- [ ] Arc для shared ownership
- [ ] Cow для flexibility

### Error Handling
- [ ] Custom error types с thiserror
- [ ] ? operator для propagation
- [ ] Result везде, не panic
- [ ] Error context с anyhow

### Async
- [ ] tokio::spawn для background tasks
- [ ] Graceful shutdown реализован
- [ ] Нет blocking в async контексте
- [ ] Connection pooling настроен

### Performance
- [ ] Pre-allocated collections
- [ ] Iterators вместо loops
- [ ] Benchmarks с criterion
- [ ] Профилирование проведено
