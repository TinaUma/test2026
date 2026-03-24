# Django Expert — Planning Reference

## Principles
1. **Custom User Model** — всегда определять в начале проекта
2. **Thin Views** — логика в сервисах, не в views
3. **Serializers для валидации** — DRF serializers на вход/выход
4. **select_related/prefetch_related** — предотвращение N+1
5. **Транзакции явные** — @transaction.atomic для критичных операций
6. **Signals осторожно** — предпочитать явные вызовы
7. **API only** — JSON responses, никаких Django templates

## Code Patterns
No specific code patterns. Follow stack principles above.
