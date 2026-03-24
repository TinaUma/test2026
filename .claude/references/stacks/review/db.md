# Database Engineer — Review Checklist

### Schema
- [ ] Primary keys (UUID или auto-increment)
- [ ] Foreign keys с proper ON DELETE
- [ ] Appropriate data types
- [ ] Constraints (CHECK, NOT NULL)

### Performance
- [ ] Indexes на filtered/joined columns
- [ ] No SELECT * в production
- [ ] EXPLAIN ANALYZE на сложных запросах
- [ ] Connection pooling настроен

### Operations
- [ ] Migrations reversible
- [ ] Redis keys имеют TTL
- [ ] Sensitive data encrypted
- [ ] Backups tested регулярно
