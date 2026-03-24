# Pixel Art / ComfyUI Artist — Review Checklist

### Consistency
- [ ] Палитра соответствует категории
- [ ] Силуэт читаемый на игровом масштабе
- [ ] Стиль консистентен с другими спрайтами

### Technical
- [ ] Прозрачный фон (PNG)
- [ ] Правильный размер (32x32, 48x48, 96x96)
- [ ] Nearest neighbor scaling
- [ ] Power of 2 для атласов

### Animation
- [ ] Все необходимые кадры есть
- [ ] Loop бесшовный (для idle)
- [ ] Timing feels good (60ms-100ms per frame)
- [ ] Sprite sheet правильно нарезан

### Unity Integration
- [ ] Pixels Per Unit = sprite size
- [ ] Filter Mode = Point (no filter)
- [ ] Compression = None или low quality
- [ ] Sprite Atlas создан для категории
