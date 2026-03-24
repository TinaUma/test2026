# Laravel Expert — Review Checklist

### Controllers
- [ ] Thin controllers, логика в services
- [ ] Form Requests для валидации
- [ ] API Resources для responses
- [ ] Правильные HTTP статусы

### Eloquent
- [ ] Relationships определены
- [ ] Eager loading где нужно
- [ ] Scopes для частых фильтров
- [ ] $fillable/$guarded настроены

### Architecture
- [ ] Service layer для бизнес-логики
- [ ] Repository pattern (опционально)
- [ ] Events для side effects
- [ ] Jobs для тяжёлых операций

### Security
- [ ] Policies для авторизации
- [ ] Sanctum для API auth
- [ ] Rate limiting настроен
- [ ] Mass assignment защищён
