# Go Backend Expert — Review Checklist

### Code Style
- [ ] Идиоматичный Go код
- [ ] Ошибки обёрнуты с контекстом (fmt.Errorf)
- [ ] Context передаётся везде
- [ ] Structured logging (slog)

### Architecture
- [ ] Handler → Service → Repository
- [ ] Интерфейсы для зависимостей
- [ ] Graceful shutdown реализован
- [ ] Connection pooling настроен

### Concurrency
- [ ] errgroup для параллельных операций
- [ ] Каналы закрываются правильно
- [ ] Нет goroutine leaks
- [ ] sync.Mutex где нужен

### Performance
- [ ] Profiling проведён
- [ ] Аллокации минимизированы
- [ ] Буферизация где уместна
