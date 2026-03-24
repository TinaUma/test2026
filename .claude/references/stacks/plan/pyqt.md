# PyQt6 Desktop GUI — Planning Reference

## Principles
1. **Signals/Slots** — вся межкомпонентная коммуникация через Qt signals, не callbacks
2. **QThread для фоновых задач** — никогда не блокировать GUI thread (I/O, API вызовы, file watching)
3. **Model/View** — данные отделены от представления (QAbstractListModel, не прямая запись в QListWidget)
4. **Window flags** — WS_EX_TRANSPARENT + WS_EX_TOPMOST для overlay, Qt.FramelessWindowHint для кастомных окон
5. **Resource management** — QApplication singleton, правильный shutdown (deleteLater, closeEvent)
6. **Settings persistence** — QSettings или JSON для сохранения позиции окна, размера, настроек
7. **Platform-aware** — проверять ОС для window flags (win32 API на Windows, X11 на Linux)

## Code Patterns

### Signal/Slot
```python
class Worker(QThread):
    result_ready = pyqtSignal(str, str)  # original, translation
    error = pyqtSignal(str)

    def run(self):
        # heavy work here, emit signals
        self.result_ready.emit(text, translation)
```

### Overlay Window (click-through)
```python
# Windows: click-through + always-on-top
hwnd = int(self.winId())
win32gui.SetWindowLong(hwnd, GWL_EXSTYLE,
    WS_EX_TRANSPARENT | WS_EX_LAYERED | WS_EX_TOPMOST)
```

### Thread-safe GUI updates
```python
# NEVER update GUI from worker thread
# Use signals or QMetaObject.invokeMethod
self.worker.result_ready.connect(self.on_translation)  # runs on GUI thread
```
