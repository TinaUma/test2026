# PHP Expert — Review Checklist

### Modern PHP
- [ ] PHP 8.2+ features используются
- [ ] declare(strict_types=1) везде
- [ ] Readonly classes для value objects
- [ ] Enums вместо констант

### Security
- [ ] Prepared statements для всех запросов
- [ ] password_hash() для паролей
- [ ] htmlspecialchars() для вывода
- [ ] Input validation перед обработкой

### Code Quality
- [ ] PSR-4 autoloading
- [ ] Type declarations на всех методах
- [ ] PHPStan level 8+
- [ ] PHP CS Fixer настроен

### Architecture
- [ ] Repository pattern для данных
- [ ] Service layer для логики
- [ ] DTO для transfer objects
- [ ] Exceptions для ошибок
