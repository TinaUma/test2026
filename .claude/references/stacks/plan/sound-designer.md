# Sound Designer — Planning Reference

## Principles
1. **Feedback is king** — каждое действие = звуковой отклик
2. **Less is more** — не перегружать soundscape
3. **Layering** — базовый звук + sweetener + low-end
4. **Dynamic range** — тихие моменты делают громкие значимыми
5. **Consistency** — одинаковая "семья" звуков для категории
6. **Adaptive audio** — музыка реагирует на gameplay
7. **Accessibility** — важная информация не только через звук

## Code Patterns
No specific code patterns. Follow stack principles above.

## Domain Knowledge

### Sound Categories

#### Whisper System (USP!)
```
CRITICAL: Whisper is the main mechanic, sound must be perfect

Charge sounds (0 → 1.5s):
- 0.0s: soft inhale + ambient shimmer
- 0.5s: first "threshold" — subtle chime (1 spirit)
- 1.0s: second "threshold" — deeper resonance (2 spirits)
- 1.5s: burst — full ethereal choir swell (3 spirits)

Release:
- 1 spirit: short whisper-incantation
- 2 spirits: two-voice whisper
- 3 spirits: choral burst + reverb tail

Style: Old Slavic intonations, not words — phonemes
Reference: Dead Cells ability sounds + Slavic folk vocals
```

#### Spirit Sounds (by type)
```
Domovoy (cozy): warm, wooden, bells
Kikimora (creepy): wet, hissing, swampy
Ognevik (fire): crackling, whoosh, sparks
Horror evolutions: distorted versions of base sounds
```

#### Day/Night Ambience
```
DAY:
- Birds (Slavic: nightingale, cuckoo)
- Light wind in leaves
- Distant water stream
- Warm, safe feeling

NIGHT:
- Owls, wolf howl (distant)
- Creaking trees
- Supernatural whispers (quiet, at the edge of hearing)
- Tension, unease
```

#### Combat
```
Hits: punch + impact layer
Enemy deaths: soul release (important for feedback!)
Synergies: special combo sound (rewarding!)
Damage taken: pain + low-end thud
Near-death: heartbeat + muffled audio
```

#### Music

| Track | Style | Instruments |
|-------|-------|-------------|
| Day (cozy) | Calm, folk | Balalaika, gusli, flute |
| Night (tension) | Tense | Drums, low strings, choir |
| Boss | Epic | Full orchestra + Slavic choir |
| Hut (hub) | Cozy | Acoustic, intimate |

### Technical Specs

#### Formats
```
Source: WAV 48kHz / 24bit
Game export: OGG Vorbis (quality 6-8)
Music loops: seamless, 2-3 min
SFX: normalized to -3dB peak
```

#### Unity Audio Settings
```
- 2D sounds for UI, ambient
- 3D sounds for spirits, enemies (small radius)
- Audio Mixer: Master, Music, SFX, Ambient, UI
- Compression: Vorbis for long, ADPCM for short
```

### Sound Design Templates

#### Ability Sound (3 layers)
```
1. Attack layer — main sound of the action
2. Sweetener — high-end detail, "magic sparkle"
3. Low-end — bass impact, weight
```

#### Death Sound (enemy)
```
1. Impact — physical "hit"
2. Soul release — magical/ethereal (important for theme!)
3. Body fall — closure
```
