# Django Expert — Review Checklist

### Models
- [ ] Custom User model настроен
- [ ] Индексы на часто фильтруемых полях
- [ ] related_name на ForeignKey
- [ ] Миграции созданы и проверены

### API
- [ ] ViewSets с правильными permissions
- [ ] Serializers валидируют данные
- [ ] Пагинация настроена
- [ ] Фильтрация через django-filter

### Performance
- [ ] select_related для ForeignKey
- [ ] prefetch_related для M2M/reverse FK
- [ ] only()/defer() для тяжёлых полей
- [ ] Кэширование настроено

### Security
- [ ] Permissions на каждом endpoint
- [ ] CORS настроен правильно
- [ ] Sensitive данные не в логах
- [ ] Rate limiting на публичных endpoints
