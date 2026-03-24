# PyQt6 Desktop GUI — Review Checklist

### Threading
- [ ] GUI updates только из main thread (через signals или invokeMethod)
- [ ] QThread для всех блокирующих операций (I/O, network, file watch)
- [ ] Worker thread правильно останавливается (quit + wait, не terminate)
- [ ] Нет race conditions при доступе к shared state

### Window Management
- [ ] Window flags корректны для платформы (win32 API для Windows overlay)
- [ ] Позиция/размер окна сохраняются между сессиями
- [ ] closeEvent обрабатывает cleanup (tray minimize vs quit)
- [ ] Frameless window имеет drag/resize handle

### Signals/Slots
- [ ] Коммуникация между компонентами через signals, не прямые вызовы
- [ ] Нет утечек — disconnect при удалении объектов или используй deleteLater
- [ ] Signal аргументы типизированы (pyqtSignal(str, int), не pyqtSignal(object))

### Resources
- [ ] QApplication — один на процесс
- [ ] QSystemTrayIcon с иконкой и контекстным меню
- [ ] Стили через QSS, не инлайн setStyleSheet на каждом виджете
- [ ] Иконки через QIcon, ресурсы через resource system или прямые пути

### Platform
- [ ] Windows-специфичный код обёрнут в if sys.platform == 'win32'
- [ ] pywin32 импорты — с try/except для кросс-платформенности
- [ ] High DPI awareness (AA_EnableHighDpiScaling)
