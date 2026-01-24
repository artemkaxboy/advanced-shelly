# ⚡ Быстрое исправление ошибки 404

## Проблема
HACS не может скачать интеграцию - ошибка 404.

## Решение за 3 шага

### 1️⃣ Создайте релиз на GitHub

**Перейдите в ваш репозиторий:**
```
https://github.com/artemkaxboy/advanced-shelly
```

**Нажмите:**
1. Вкладка **"Releases"** (справа от Code)
2. **"Create a new release"** (зеленая кнопка)

**Заполните:**
- **Choose a tag**: введите `v1.0.0` и нажмите "Create new tag"
- **Target**: выберите `main`
- **Release title**: `v1.0.0`
- **Description**: `Initial release - автоматическое резервное копирование скриптов Shelly`

**Нажмите "Publish release"**

### 2️⃣ Удалите из HACS и переустановите

В Home Assistant:
1. **HACS** → **Integrations**
2. Найдите **Advanced Shelly**
3. Нажмите **⋮** (три точки)
4. **Remove**
5. Подтвердите удаление

Подождите 10 секунд.

6. Снова **⋮** → **Custom repositories**
7. Добавьте репозиторий заново:
   - Repository: `https://github.com/artemkaxboy/advanced-shelly`
   - Category: `Integration`
8. **Add**
9. Найдите интеграцию и нажмите **Download**

### 3️⃣ Перезапустите Home Assistant

**Settings** → **System** → **Restart**

## Готово! ✅

Интеграция должна установиться.

---

## Если всё ещё не работает

### Проверьте структуру репозитория

Зайдите на GitHub в ваш репозиторий и убедитесь что файлы лежат так:

```
artemkaxboy/advanced-shelly/           ← корень репозитория
├── custom_components/                 ← эта папка ОБЯЗАТЕЛЬНА
│   └── advanced_shelly/              ← и эта тоже
│       ├── __init__.py
│       ├── manifest.json
│       ├── config_flow.py
│       └── ...
├── hacs.json                         ← в корне
├── README.md
└── ...
```

**Если папки `custom_components` нет в корне** - это проблема!

### Правильный hacs.json

Файл `hacs.json` должен быть в корне репозитория:

```json
{
  "name": "Advanced Shelly",
  "content_in_root": false,
  "filename": "advanced_shelly",
  "render_readme": true,
  "homeassistant": "2024.1.0",
  "zip_release": true,
  "hide_default_branch": false
}
```

### Проверьте основную ветку

Основная ветка должна называться **`main`**, а не `master`.

**Как проверить:**
На главной странице репозитория GitHub смотрите слева вверху - должно быть написано `main`.

**Если написано `master`:**
```bash
git branch -m master main
git push -u origin main
```

Затем в GitHub:
1. **Settings** → **Branches**
2. **Default branch** → выберите `main`
3. **Update**

## Альтернатива: Ручная установка

Если HACS совсем не работает:

1. Скачайте ZIP с GitHub:
   ```
   https://github.com/artemkaxboy/advanced-shelly/archive/refs/heads/main.zip
   ```

2. Распакуйте архив

3. Скопируйте папку `custom_components/advanced_shelly` 
   в `/config/custom_components/` в вашем Home Assistant

4. Перезапустите Home Assistant

5. Добавьте интеграцию через UI:
   **Settings** → **Devices & Services** → **Add Integration** → **Advanced Shelly**

---

## После установки

### Добавление устройства

1. **Settings** → **Devices & Services** → **Add Integration**
2. Найдите **Advanced Shelly**
3. Введите:
   - IP-адрес вашего Shelly (например: 192.168.1.100)
   - Интервал бэкапа в секундах (по умолчанию 86400 = 24 часа)
4. Нажмите Submit

### Проверка работы

Бэкапы будут сохраняться в `/config/shelly_backups/{device_id}/`

Проверить логи:
```bash
tail -f /config/home-assistant.log | grep advanced_shelly
```

### Использование сервисов

Создать бэкап вручную:
```yaml
service: advanced_shelly.backup_now
```

Восстановить скрипт:
```yaml
service: advanced_shelly.restore_script
data:
  device_id: shellyplus1pm-xxx
  script_id: 1
```
