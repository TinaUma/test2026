# Frai — Быстрый старт для AI-агентов

Эта инструкция для AI-агента (Claude Code, Cursor и т.д.), который впервые подключается к проекту с Frai.

## 1. Установка (новый проект)

### 1.1. Клонировать фреймворк как сабмодуль

```bash
git submodule add <frai-repo-url> .frai-lib
```

### 1.2. Запустить bootstrap

```bash
python .frai-lib/bootstrap/bootstrap.py --smart --init my-project
```

Что произойдёт:
- Создастся `.frai/` — данные (БД, конфиг, venv)
- Создастся `.claude/` (или `.cursor/`) — skills, scripts, MCP
- Создадутся `CLAUDE.md`, `AGENTS.md`, `.mcp.json`
- Стеки определятся автоматически (Python, React, Go, и т.д.)
- CLI-обёртка: `.frai/frai` (Unix) / `.frai/frai.cmd` (Windows)

### 1.3. Добавить в .gitignore

```
.frai/
```

`.claude/` и `CLAUDE.md` — коммитить (это инструкции для агентов).

### 1.4. Проверить

```bash
.frai/frai status
```

Должно показать: `Tasks: 0/0 done`, `Session: none active`.

---

## 2. Обновление с предыдущей версии

```bash
cd .frai-lib && git pull origin main && cd ..
python .frai-lib/bootstrap/bootstrap.py --update-deps
```

Миграции БД применяются автоматически. Перед миграцией создаётся бэкап: `.frai/frai.db.bak.vN`.

**Проверить после обновления:**
```bash
.frai/frai status
.frai/frai metrics
```

---

## 3. Первая сессия — полный цикл

### 3.1. Начать сессию

```bash
.frai/frai session start
```

### 3.2. Создать задачу

```bash
.frai/frai task quick "Добавить авторизацию" --role developer --stack python --goal "Пользователь может войти по email/паролю"
```

### 3.3. Установить acceptance criteria (ОБЯЗАТЕЛЬНО)

```bash
.frai/frai task update <slug> --acceptance-criteria "1. POST /login возвращает JWT. 2. Невалидные данные — 401. 3. Пустой email — 422."
```

**Без goal + AC задачу нельзя начать (QG-0 Context Gate).**

### 3.4. Начать работу

```bash
.frai/frai task start <slug>
```

### 3.5. Работать по плану

После каждого шага:
```bash
.frai/frai task log <slug> "Реализовал endpoint POST /login"
.frai/frai task step <slug> 1
```

Если подход не сработал — задокументировать:
```bash
.frai/frai dead-end "Пробовал bcrypt" "Не работает на Python 3.14" --task <slug>
```

### 3.6. Завершить задачу

1. Проверить каждый AC:
```bash
.frai/frai task log <slug> "AC verified: 1. POST /login 200 ✓ 2. Невалидные 401 ✓ 3. Пустой 422 ✓"
```

2. Закрыть:
```bash
.frai/frai task done <slug> --ac-verified
```

**Без evidence в notes и --ac-verified закрыть нельзя (QG-2 Implementation Gate).**

### 3.7. Завершить сессию

```bash
.frai/frai session handoff '{"completed":["<slug>"],"next_steps":["Написать тесты"],"dead_ends":[],"warnings":[]}'
.frai/frai session end --summary "Реализована авторизация"
```

---

## 4. Рабочий цикл (ежедневный)

```
/start                          → загрузить контекст, посмотреть метрики
/plan "описание задачи"         → создать задачу с goal + AC
/task <slug>                    → начать работу (QG-0 проверит goal+AC)
  работа → task log → task step → dead-end при неудачах
/task done                      → проверить AC, залогировать evidence, закрыть (QG-2)
/review                         → code review (проверит scope creep, dead ends, AC)
/test                           → запустить тесты
/commit                         → закоммитить (проверит active task, scope)
/checkpoint                     → сохранить контекст (каждые 30-50 tool calls)
/end                            → завершить сессию (метрики, handoff, решения)
```

---

## 5. SENAR Quality Gates

| Gate | Когда | Что проверяет | Обход |
|------|-------|---------------|-------|
| **QG-0** | `task start` | goal + acceptance_criteria заполнены | Нет обхода через CLI |
| **QG-2** | `task done` | AC verified в notes + `--ac-verified` + quality gates (pytest, ruff) | Нет обхода через CLI |

---

## 6. Ключевые команды

```bash
.frai/frai status                    # Обзор + предупреждение о сессии
.frai/frai metrics                   # SENAR метрики
.frai/frai task list                 # Все задачи
.frai/frai task show <slug>          # Детали задачи
.frai/frai dead-end "что" "почему"   # Задокументировать dead end
.frai/frai explore start "тема"      # Начать исследование (без задачи)
.frai/frai explore end --summary "..." # Завершить исследование
.frai/frai memory search "запрос"    # Поиск по памяти
.frai/frai audit check               # Проверить нужен ли аудит
.frai/frai audit mark                # Отметить аудит проведённым
```

---

## 7. Что нельзя делать

- Писать код без `task start` — создай задачу через `/plan`
- Закрывать задачу без проверки AC — залогируй evidence через `task log`
- Игнорировать dead ends — документируй сразу через `dead-end`
- Работать дольше 120 минут без `/checkpoint`
- Коммитить без подтверждения пользователя
- Обращаться к БД напрямую — только через `.frai/frai` CLI

---

## 8. Структура файлов

```
.frai/                  # Данные (НЕ коммитить)
  frai.db               # SQLite БД (задачи, сессии, память)
  config.json           # Конфигурация
  frai / frai.cmd       # CLI-обёртка
  vendor/               # Внешние skills
.claude/                # Инструкции для Claude Code (коммитить)
  skills/               # 10 core skills (/start, /plan, /task, ...)
  scripts/              # Бизнес-логика (копия из .frai-lib)
  CLAUDE.md             # Главные инструкции
CLAUDE.md               # Корневой — генерируется bootstrap
```
