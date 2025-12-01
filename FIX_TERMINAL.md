# Исправление терминалов Local и Local (2) в PyCharm

## Проблема
Терминалы "Local" и "Local (2)" не запускаются с ошибкой PowerShell.

## Решение

### Вариант 1: Исправить настройки терминала в PyCharm

1. **File → Settings** (или `Ctrl+Alt+S`)
2. **Tools → Terminal**
3. В поле **"Shell path"** укажите один из вариантов:
   ```
   C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
   ```
   ИЛИ
   ```
   C:\Program Files\PowerShell\7\pwsh.exe
   ```
4. Снимите галочку **"Activate virtualenv"** (если стоит)
5. Нажмите **OK**
6. Закройте и откройте терминалы "Local" и "Local (2)" заново

### Вариант 2: Использовать готовые скрипты

В терминале "Windows PowerShell" (который работает):
- Для backend: `.\run_backend.ps1`
- Для frontend: `.\run_frontend.ps1`

### Вариант 3: Пересоздать терминалы

1. Закройте терминалы "Local" и "Local (2)" (крестик на вкладке)
2. Создайте новые через кнопку "+"
3. Они должны работать с исправленными настройками




