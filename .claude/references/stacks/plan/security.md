# Security Engineer — Planning Reference

## Principles
1. **Input validation** — на всех входах
2. **Parameterized queries** — никакой конкатенации SQL
3. **Rate limiting** — на authentication endpoints
4. **Secure sessions** — httpOnly, secure, sameSite
5. **bcrypt/argon2** — для паролей (не MD5/SHA1)
6. **HTTPS everywhere** — в production
7. **Security headers** — helmet.js или аналог

## Code Patterns
No specific code patterns. Follow stack principles above.
