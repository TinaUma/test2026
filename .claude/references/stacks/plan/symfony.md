# Symfony Expert — Planning Reference

## Principles
1. **DTO для данных** — не entities в controllers
2. **Services для логики** — thin controllers
3. **Voters для авторизации** — fine-grained access
4. **Serialization groups** — контроль вывода
5. **Validation constraints** — на DTO и entities
6. **Messenger для async** — очереди задач
7. **API only** — никаких Twig templates

## Code Patterns
No specific code patterns. Follow stack principles above.
