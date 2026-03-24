# Pixel Art / ComfyUI Artist — Planning Reference

## Principles
1. **Консистентность палитры** — единая палитра для категории (духи, враги, UI)
2. **Читаемость силуэта** — персонаж узнаваем по силуэту на 32x32
3. **Animation principles** — squash/stretch, anticipation даже в pixel art
4. **AI как инструмент** — генерация = старт, не финал
5. **Nearest neighbor scaling** — никакого bilinear для pixel art
6. **Sprite sheets** — правильная нарезка для Unity Animator
7. **Transparent backgrounds** — SAM для чистого альфа-канала

## Code Patterns
No specific code patterns. Follow stack principles above.

## Domain Knowledge

### Color Palette

| Category | Colors | Hex |
|----------|--------|-----|
| **Day (cozy)** | Warm greens, golden | #4A7023, #8FB339, #F4D03F |
| **Night (tension)** | Cool blues, purples | #1A237E, #4A148C, #7B1FA2 |
| **Spirits Cozy** | Warm orange, golden | #FF9800, #FFC107, #FFE082 |
| **Spirits Horror** | Cool blue, red | #E53935, #8E24AA, #3949AB |
| **Enemies** | Dark, rotten | #4A148C, #1B5E20, #3E2723 |
| **UI** | Wood, parchment | #8D6E63, #D7CCC8, #3E2723 |

### ComfyUI Settings
```
Model: SDXL 1.0
LoRA: Pixel Art XL (strength 0.8-1.2)
CFG Scale: 7-8 (without LCM) or 1.5 (with LCM)
Steps: 20-30 (without LCM) or 8 (with LCM)
Resolution: 512x512 → downscale 8x (nearest neighbor)

IMPORTANT: Do NOT write "pixel art" in prompt when using Pixel Art XL
```

### Sprite Requirements

| Category | Size | Animations |
|----------|------|------------|
| Player | 32x32 | idle, walk (4-8 frames), hurt |
| Spirits | 32x32 | idle, attack, ability |
| Enemies (regular) | 32x32 | idle, walk, attack |
| Enemies (elite) | 48x48 | idle, walk, attack, special |
| Boss | 96x96 | idle, attack1, attack2, phase_transition, death |
| Effects | 32x32 | 4-8 frames loop |

### Pipeline
1. **Prompt** — compose from template
2. **Generate** — ComfyUI, 512x512
3. **Segmentation** — SAM2/SAM3, remove background
4. **Palette** — ComfyUI-PixelArt-Detector, apply project palette
5. **Downscale** — nearest neighbor to target size
6. **Polish** — Aseprite, manual artifact cleanup
7. **Animation** — img2img for frames or manual
8. **Sprite sheet** — SpriteSheetMaker or Aseprite export
9. **Unity** — import, Sprite Editor slice, Animator
