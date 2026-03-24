# Lua WoW Addon — Planning Reference

## Principles
1. **Sandbox** — нет HTTP, нет filesystem, нет os.execute(). Только WoW API, SavedVariables, Chat API
2. **Events, не polling** — frame:RegisterEvent + OnEvent handler, не OnUpdate тики
3. **SavedVariables** — единственный способ хранения данных между сессиями. Загружаются при login/reload
4. **Minimal footprint** — аддон должен быть лёгким (<200 строк). Тяжёлая логика — в companion app
5. **TOC metadata** — Interface version строго соответствует патчу (12.0.x для Midnight)
6. **Slash commands** — /commandname для пользовательского взаимодействия. Регистрация через SlashCmdList
7. **Secret Values (Midnight)** — чат в Lua API заблокирован во время M+/PvP/boss encounter. WoWChatLog.txt не затронут

## Code Patterns

### Event Registration
```lua
local frame = CreateFrame("Frame")
frame:RegisterEvent("ADDON_LOADED")
frame:RegisterEvent("CHAT_MSG_PARTY")
frame:SetScript("OnEvent", function(self, event, ...)
    if event == "ADDON_LOADED" and ... == "AddonName" then
        -- init
    end
end)
```

### SavedVariables (TOC)
```
## SavedVariables: AddonNameDB
## SavedVariablesPerCharacter: AddonNameCharDB
```

### Slash Command
```lua
SLASH_ADDONNAME1 = "/cmd"
SlashCmdList["ADDONNAME"] = function(msg)
    -- handle msg
end
```

### Chat Log Toggle
```lua
-- Включить запись чата в файл
LoggingChat(true)
-- Проверить статус
local isLogging = IsLoggingChat()
```
