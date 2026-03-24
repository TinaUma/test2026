# Nuxt3 Fullstack Expert — Planning Reference

## Principles
1. **Composition API** — только `<script setup>`
2. **useFetch в компонентах** — не $fetch (hydration issues)
3. **Pinia для state** — defineStore с setup syntax
4. **Zod валидация** — на server routes
5. **~/ alias** — для всех импортов
6. **Auto-imports** — не импортировать ref, computed
7. **External CSS** — без scoped styles

## Code Patterns
No specific code patterns. Follow stack principles above.
