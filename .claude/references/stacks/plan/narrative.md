# Narrative Designer — Planning Reference

## Principles
1. **Show, don't tell** — environmental storytelling > текстовые дампы
2. **Механика = история** — эволюция Cozy/Horror отражает выбор игрока
3. **Краткость** — игрок в action-игре не читает стены текста
4. **Аутентичность** — настоящий фольклор, не generic fantasy
5. **Игрок — агент** — его выборы определяют историю
6. **Emergent narrative** — синергии духов = их отношения
7. **Локализуемость** — тексты готовы к переводу

## Code Patterns
No specific code patterns. Follow stack principles above.

## Domain Knowledge

### Central Narrative
```
SETUP:
Wanderer (player) strayed into deep taiga and awakened the Master of the Taiga —
an ancient forest spirit. Now the forest won't release them until they reach
the Heart of the Taiga deep in the thicket.

CONFLICT:
The Master is not an enemy — he tests. He taught the wanderer to whisper
incantations, summoning spirit helpers. But the more souls the spirits consume,
the further they drift from the light...

FORK:
Cozy path → spirits remain kind protectors
Horror path → spirits become powerful monsters
Player choice determines the ending.
```

### Spirits — Characters and Lore

#### Domovoy
```
Lore: House spirit, hearth protector. Lives behind the stove, loves milk.
Character: Grumpy but caring. Like an old grandfather.

Cozy evolution → Domovoy-Grandfather
"Protects not only the house, but all who dwell within."

Horror evolution → Domovoy-Nightmare
"He who protects can also destroy."
```

#### Kikimora
```
Lore: Swamp spirit, wife of domovoy (in some versions).
Character: Cunning, snarky, but not evil. Loves mischief.

Cozy evolution → Kikimora-Weaver
"Weaves fates, not just threads."

Horror evolution → Kikimora-Plague
"Her venom became deadly, like her grudge."
```

#### Ognevik (Fire-chick)
```
Lore: Small fire spirit, relative of the Firebird.
Character: Curious, restless, slightly chaotic.

Cozy evolution → Firebird
"His light warms without burning."

Horror evolution → Arsonist
"Fire that devours everything."
```

### Enemies — Lore

| Enemy | Origin | Description |
|-------|--------|-------------|
| Upyr | Restless dead | One who died wrongly. Forever hungry. |
| Wolf | Cursed beast | Not a normal wolf — a shadow wolf, echo of the forest. |
| Will-o'-wisp | Lost soul | Lures travelers into the swamp. Explodes from despair. |
| Volkolak | Werewolf | A human who lost their humanity. |
| Bolotnitsa | Swamp spirit | Mistress of the bogs, catches the careless. |

### Endings (5)
```
1. FOREST GUARDIAN (80%+ Cozy)
2. LORD OF DARKNESS (80%+ Horror)
3. EQUILIBRIUM (~50/50)
4. EXILE (refuse final battle)
5. TRUE PATH (all spirits max + secrets)
```

### Writing Style Guide

#### Text Lengths
```
UI labels: 1-3 words
Tooltips: 1 sentence
Lore entries: 2-4 sentences
Spirit descriptions: 1 sentence + quote
Endings: 2-3 sentences
```

#### Tone
```
Day: Cozy, fairy-tale, like grandmother's stories
Night: Anxious, but not horror — more "creepy interesting"
Cozy spirits: Warm, homey
Horror spirits: Ominous, but with a note of tragedy
```

#### Forbidden
```
- Modern slang
- Generic fantasy tropes (mana, spell, magic)
- Walls of text
- Explaining the obvious
- Direct moralizing
```
