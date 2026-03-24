# Security Engineer — Review Checklist

### Input/Output
- [ ] Все inputs валидируются
- [ ] Parameterized queries везде
- [ ] XSS prevention (escape output)
- [ ] File uploads валидируются

### Authentication
- [ ] Rate limiting на auth
- [ ] Secure session config
- [ ] Strong password policy
- [ ] MFA где возможно

### Configuration
- [ ] Security headers настроены
- [ ] CORS properly configured
- [ ] Dependencies audited (npm audit)
- [ ] Secrets не в коде

### Logging
- [ ] Security events логируются
- [ ] Sensitive data не логируется
- [ ] Audit trail настроен
