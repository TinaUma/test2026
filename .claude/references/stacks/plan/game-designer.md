# Game Designer — Planning Reference

## Principles
1. **Core loop первичен** — если микро-цикл не fun, игра не спасётся
2. **Meaningful choices** — каждый выбор должен иметь trade-off
3. **Risk/reward баланс** — Horror = сильнее но рискованнее
4. **Emergent gameplay** — синергии > скриптованный контент
5. **Iteration over perfection** — тестировать рано и часто
6. **Data-driven** — числа в ScriptableObjects, не в коде
7. **Player fantasy** — механика должна поддерживать фантазию

## Code Patterns
No specific code patterns. Follow stack principles above.

## Domain Knowledge

### Key Balance Systems

#### Whisper System (Charge + Release)
```
Hold 0.5s  → 1 spirit (fast, safe)
Hold 1.0s  → 2 spirits + combo
Hold 1.5s  → 3 spirits + burst + synergy

Trade-off: Longer hold = more powerful, but more vulnerable
Cooldown: 5-8s (frequent enough for agency)
```

#### Dual Evolution (Cozy/Horror)
```
COZY path:
- Defense, healing, control
- More stable, easier
- Light resources (honey, flowers)

HORROR path:
- Damage, berserk, drain HP
- More powerful, but riskier
- Dark resources (bones, ash)

Goal: 3+ different playthroughs
```

#### Spirit Synergies
```
On burst (3 spirits) → check combos:
- Rusalka + Bannik = Steam Explosion
- Ognevik + Kikimora = Poisonous Fire
- Domovoy + Young Drevyen = Fortress

100+ combinations = emergent builds
```

#### Wave Progression
```
Wave 1-3:   Regular enemies, learning
Wave 4-7:   Elite enemies, combinations
Wave 8-10:  Peak difficulty
Final:      Boss with phases

Emotional rhythm: tension → release → choice
```

### Base Numbers

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Player HP | 100 | Round number, easy to calculate % |
| Spirits in deck | 8-12 | Enough for combos, but memorable |
| Whisper cooldown | 5-8s | Agency without spam |
| Enemies on screen | max 25 | Readability + performance |
| Wave length | 2-3 min | Attention doesn't fatigue |
| Run length | 30-40 min | One session = one run |

### ScriptableObject Templates

#### SpiritData
```
- ID, Name, Description
- Base HP, Damage, Speed
- Role (Tank/DPS/Support/Control)
- Ability (cooldown, effect)
- Evolution paths (Cozy/Horror)
- Synergy tags
```

#### EnemyData
```
- ID, Name
- HP, Damage, Speed
- Behavior type (Melee/Ranged/Kamikaze/Summoner)
- Spawn weight per wave
- Loot table
```

#### WaveData
```
- Wave number
- Enemy composition (type, count)
- Spawn timing
- Elite chance
- Reward options
```
