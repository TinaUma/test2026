# Node.js Backend Expert — Review Checklist

### Architecture
- [ ] Controllers thin, логика в services
- [ ] Все inputs валидируются через Zod
- [ ] Централизованный error handler
- [ ] Structured logging с контекстом

### Async
- [ ] Все async errors обработаны
- [ ] Promise.all для параллельных операций
- [ ] Cleanup в finally блоках
- [ ] Таймауты на внешние запросы

### Security
- [ ] Rate limiting на публичных endpoints
- [ ] Helmet middleware включён
- [ ] CORS настроен правильно
- [ ] Sensitive данные не в responses

### Performance
- [ ] Connection pooling настроен
- [ ] Кэширование где уместно
- [ ] Нет блокирующих операций в event loop
