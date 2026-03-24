# Lua WoW Addon — Review Checklist

### Sandbox
- [ ] Нет вызовов os.execute(), io.open(), require() на внешние модули
- [ ] Нет попыток HTTP-запросов или socket-соединений
- [ ] Все данные хранятся только через SavedVariables

### Performance
- [ ] Нет тяжёлой логики в OnUpdate (вызывается каждый кадр)
- [ ] Events предпочтительнее polling
- [ ] Строки не конкатенируются в циклах (используй table.concat)
- [ ] Локальные переменные вместо глобальных (local = быстрее)

### TOC
- [ ] Interface version соответствует текущему патчу WoW
- [ ] SavedVariables объявлены в TOC (не хардкод)
- [ ] Зависимости указаны через ## Dependencies или ## OptionalDeps

### API Usage
- [ ] ADDON_LOADED проверяет имя аддона (... == "AddonName")
- [ ] Chat events регистрируются только нужные (не все CHAT_MSG_*)
- [ ] ChatFrame_AddMessageEventFilter не имеет side effects
- [ ] LoggingChat() вызывается после полной загрузки UI

### Secret Values (Midnight 12.0)
- [ ] Аддон корректно обрабатывает Secret Values (msg может быть непрочитаемым)
- [ ] Нет зависимости от чтения чата в бою — companion app работает через WoWChatLog.txt

### Compatibility
- [ ] Нет deprecated API (GetPlayerInfoByGUID → C_PlayerInfo.GetPlayerInfoByGUID)
- [ ] Используется C_* namespace где доступен (C_ChatInfo, C_AddOns)
- [ ] Тестировано с /reload без ошибок
