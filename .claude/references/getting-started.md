# Frai — Руководство по началу работы

## Требования

- Python 3.11+
- Git
- Claude Code или Cursor IDE

## Установка

### Шаг 1: Добавить Frai в проект

```bash
cd your-project
git submodule add <frai-repo-url> .frai-lib
```

### Шаг 2: Bootstrap

Bootstrap копирует скиллы, скрипты, MCP-серверы, роли и стеки в директорию вашего IDE.

```bash
# Claude Code (рекомендуется --smart для авто-детекта стека):
python .frai-lib/bootstrap/bootstrap.py --ide claude --smart

# Cursor:
python .frai-lib/bootstrap/bootstrap.py --ide cursor --smart

# Оба IDE:
python .frai-lib/bootstrap/bootstrap.py --ide all --smart
```

**Что делает `--smart`:**
- Сканирует проект для определения стека (Python, React, Go и т.д.)
- Выбирает подходящие расширенные скиллы (например, `/test` если есть тест-инфраструктура)
- Определяет наличие Ollama для семантического поиска (иначе FTS5)

**Что создаёт bootstrap:**
```
your-project/
├── .frai/
│   ├── frai                # CLI-обёртка (Unix)
│   ├── frai.cmd            # CLI-обёртка (Windows)
│   └── venv/               # Python venv (если создан)
├── .claude/                # (или .cursor/)
│   ├── skills/             # 24 SKILL.md файла
│   ├── scripts/            # Python-модули фреймворка
│   ├── mcp/                # MCP-серверы
│   ├── roles/              # 4 профиля ролей
│   ├── stacks/             # Руководства по стекам
│   └── references/         # Документация
├── .mcp.json               # Конфигурация MCP-серверов
├── CLAUDE.md               # Инструкции для агента (редактируйте!)
└── AGENTS.md               # Оглавление репозитория для агентов
```

### Шаг 3: Инициализация проекта

```bash
.frai/frai init --name my-project
```

Создаёт `.frai/frai.db` — SQLite база данных для всех данных проекта.

### Шаг 4: Начать первую сессию

В Claude Code наберите `/start`. Или через CLI:

```bash
.frai/frai session start
```

## Рабочий процесс

### Цикл работы

```
/start → /plan → /task slug → [работа] → /task done → /commit → /end
```

1. **`/start`** — Открывает сессию, загружает handoff предыдущей сессии, показывает дашборд
2. **`/plan`** — Разбивает работу на эпики, стори, задачи
3. **`/task slug`** — Активирует задачу, загружает контекст (роль + стек + память)
4. Работайте над задачей, используйте `/review`, `/test`, `/debug` по необходимости
5. **`/task done`** — Отмечает задачу выполненной (автозакрытие story/epic если все задачи готовы)
6. **`/commit`** — Создаёт conventional git commit
7. **`/end`** — Сохраняет handoff для следующей сессии, закрывает сессию

### Создание рабочих элементов

```bash
# Создание иерархии: Epic → Story → Task
.frai/frai epic add v1 "Версия 1.0"
.frai/frai story add v1 auth "Аутентификация"
.frai/frai task add auth "JWT логин" \
    --slug jwt-login \
    --role developer \
    --complexity medium \
    --goal "Пользователь может войти по email/паролю и получить JWT"

# Задать шаги плана (опционально, но рекомендуется)
.frai/frai task plan jwt-login \
    "Создать модель User с bcrypt" \
    "Реализовать /login эндпоинт" \
    "Добавить генерацию JWT" \
    "Написать тесты"
```

### Работа над задачей

```bash
# Активация задачи (ОБЯЗАТЕЛЬНО перед кодированием)
.frai/frai task start jwt-login

# Логирование прогресса (crash-safe журналирование)
.frai/frai task log jwt-login "Создана модель User с email + hashed_password"
.frai/frai task log jwt-login "Login endpoint работает, возвращает JWT"

# Отметка шагов плана
.frai/frai task step jwt-login 1    # "Создать модель User" — готово
.frai/frai task step jwt-login 2    # "Реализовать /login" — готово

# Завершение задачи (блокируется если шаги плана не завершены — --force для обхода)
.frai/frai task done jwt-login
```

### Запись знаний

```bash
# Архитектурные решения
.frai/frai decide "bcrypt вместо argon2" --rationale "Шире поддержка библиотек" --task jwt-login

# Паттерны проекта
.frai/frai memory add pattern "Формат ошибок" "Все API ошибки возвращают {error: string, code: int}"

# Готчи (на чём споткнулись)
.frai/frai memory add gotcha "JWT expiry" "Срок действия проверять на сервере, не только на клиенте"

```

### Handoff между сессиями

При завершении сессии сохраните контекст для следующего агента:

```bash
.frai/frai session handoff '{
    "completed": ["jwt-login"],
    "in_progress": ["oauth-setup"],
    "key_files": ["src/auth.py", "src/models/user.py"],
    "dead_ends": ["Пробовали passport.js — слишком сложно"],
    "next_steps": ["Добавить ротацию refresh token", "Написать интеграционные тесты"],
    "warnings": ["Rate limiter не настроен для /login"]
}'
.frai/frai session end --summary "JWT реализован, OAuth в процессе"
```

## Ключевые концепции

### Иерархия: Epic → Story → Task

- **Epic** — крупная инициатива (например, "Релиз v1.0")
- **Story** — пользовательская фича (например, "Аутентификация")
- **Task** — конкретная единица работы (например, "JWT логин")

Авто-каскад: когда все задачи в стори завершены — стори автозакрывается. Когда все стори в эпике завершены — эпик автозакрывается.

### Жизненный цикл задачи

```
planning → active → done
              ↕
           blocked
              ↓
           review → done
```

- Задачи создаются в статусе `planning`
- `task start` переводит в `active`
- `task block` / `task unblock` для блокировок
- `task review` для этапа ревью
- `task done` завершает (проверяет шаги плана)

### Plan Completion Gate

Если у задачи есть шаги плана, `task done` блокируется пока все шаги не отмечены выполненными. Для обхода:

```bash
.frai/frai task done jwt-login --force
```

### Роли

Назначьте роль каждой задаче. Роль модифицирует поведение скиллов:

| Роль | Фокус |
|------|-------|
| `developer` | Корректность кода, паттерны, ограничения стека |
| `architect` | Дизайн системы, границы API, решения |
| `qa` | Покрытие тестами, крайние случаи, верификация |
| `tech-writer` | Качество документации, ясность |

### Стеки

Назначьте стек задаче для стек-специфичных паттернов:

```bash
.frai/frai task add auth "JWT логин" --slug jwt-login --stack fastapi --role developer
```

Агент загрузит `stacks/fastapi.md` с паттернами тестирования, конвенциями, чеклистом ревью и типичными ошибками.

### Полнотекстовый поиск

```bash
.frai/frai search "аутентификация"              # Поиск везде
.frai/frai search "JWT" --scope tasks            # Только задачи
.frai/frai search "паттерн" --scope memory       # Только память
```

### Мульти-агент

Несколько агентов могут работать над одним проектом:

```bash
.frai/frai task claim jwt-login agent-1          # Занять задачу (атомарно)
.frai/frai team                                   # Задачи по агентам
.frai/frai task unclaim jwt-login                 # Освободить
```

## MCP-интеграция

Frai предоставляет 2 MCP-сервера (автоматически настраиваются bootstrap):

1. **`frai-project`** — Полный доступ к БД: задачи, сессии, память, решения
2. **`frai-codebase-rag`** — Поиск по коду: `search_code`, `search_knowledge`, `reindex`

MCP tools имеют JSON-схемы — невозможно ошибиться в аргументах. Предпочтительнее CLI когда доступны.

## Quality Gates (v1.2.0)

Автоматические проверки качества, встроенные в workflow:

```bash
# Посмотреть активные gates
.frai/frai gates status

# Включить/выключить gate
.frai/frai gates enable mypy
.frai/frai gates disable mypy
```

**Встроенные gates:**
| Gate | По умолчанию | Severity | Триггер |
|------|-------------|----------|---------|
| `pytest` | ON | block | task-done, review |
| `ruff` | ON | block | commit |
| `filesize` | ON | warn | task-done, commit |
| `mypy` | OFF | warn | commit |
| `bandit` | OFF | warn | review |

Gates запускаются автоматически в скиллах `/task done`, `/commit`, `/review`.

## Multi-Agent Skills (v1.2.0)

### /dispatch — Оркестрация воркеров

Запускает несколько задач параллельно через Agent tool + worktrees:

```
/dispatch task-1,task-2,task-3
```

Диспетчер остаётся в основной сессии. Воркеры работают в изолированных копиях репозитория. Результаты мёрджатся после завершения.

### /loop-task — Автономный цикл

Запускает задачу в автономном режиме с перезапуском при переполнении контекста:

```
/loop-task my-complex-task
```

Каждая итерация получает свежий контекст с текущим состоянием задачи. Максимум 10 итераций, стоп после 2 зависаний подряд.

## Советы

### Для новых проектов
1. Начните с одного эпика и 2-3 стори
2. Делайте задачи маленькими (1-2 часа работы агента)
3. Всегда указывайте `--role` и `--goal` для задач
4. Используйте `task log` постоянно — это ваш crash-safe трекер прогресса

### Для агентов
1. **Всегда `/start` первым** — загружает контекст предыдущей сессии
2. **Никогда не кодить без задачи** — даже мелкие фиксы нужен `task start`
3. **`task log` после каждого шага** — если сессия упадёт, заметки сохранятся
4. **Записывайте решения** — агент следующей сессии скажет спасибо
5. **Всегда `/end`** — handoff критически важен для передачи контекста

### Обновление Frai
```bash
cd .frai-lib
git pull origin main
cd ..
python .frai-lib/bootstrap/bootstrap.py --ide claude --smart   # Перезапустить bootstrap
```

## Устранение проблем

### "No .frai/frai.db found"
Выполните `.frai/frai init --name my-project`.

### "command not found: .frai/frai"
Сделайте обёртку исполняемой: `chmod +x .frai/frai` (Unix) или используйте `.frai/frai.cmd` (Windows).

### MCP-серверы не отображаются
Проверьте наличие `.mcp.json` в корне проекта. Перезапустите bootstrap если отсутствует.

### "FOREIGN KEY constraint failed"
Вы ссылаетесь на task_slug которого нет. Используйте `--task` с существующим slug задачи, или не указывайте.

### Ошибки миграции схемы
Frai автоматически мигрирует при запуске. Если миграция провалилась — возможно, БД от несовместимой версии. Сделайте бэкап `.frai/frai.db` и переинициализируйте.
