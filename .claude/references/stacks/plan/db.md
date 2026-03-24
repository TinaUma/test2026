# Database Engineer — Planning Reference

## Principles
1. **EXPLAIN ANALYZE** — на всех сложных запросах
2. **Indexes** — на filtered/joined columns
3. **No SELECT *** — только нужные колонки
4. **Connection pooling** — PgBouncer, ProxySQL
5. **Reversible migrations** — всегда UP и DOWN
6. **TTL для кэша** — обязательно на Redis keys
7. **Backups tested** — регулярно проверять восстановление

## Code Patterns
No specific code patterns. Follow stack principles above.
