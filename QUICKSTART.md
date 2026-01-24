# 🚀 Быстрый старт

## Установка за 3 минуты

### Шаг 1: Установка
Скопируйте папку `shelly_scripts_backup` в `/config/custom_components/`:

```bash
cd /config/custom_components
git clone https://github.com/yourusername/shelly_scripts_backup.git
```

Или через HACS:
1. HACS → Integrations → ⋮ → Custom repositories
2. Добавьте URL репозитория
3. Найдите "Shelly Scripts Backup" → Download

### Шаг 2: Перезапуск
Перезапустите Home Assistant

### Шаг 3: Настройка
1. Settings → Devices & Services → Add Integration
2. Найдите "Shelly Scripts Backup"
3. Введите IP-адрес вашего Shelly устройства (например: `192.168.1.100`)
4. Нажмите Submit

**Готово!** Первый бэкап будет создан автоматически.

## Где найти бэкапы?

Бэкапы сохраняются в `/config/shelly_backups/{device_id}/`:

```
/config/shelly_backups/
└── shellyplus1pm-a8032ab12345/
    ├── 1_my_script.js       # Код скрипта
    ├── 1_my_script.json     # Метаданные
    ├── 2_automation.js
    └── 2_automation.json
```

## Основные команды

### Создать бэкап вручную
```yaml
service: shelly_scripts_backup.backup_now
```

### Создать бэкап конкретного устройства
```yaml
service: shelly_scripts_backup.backup_now
data:
  device_id: shellyplus1pm-a8032ab12345
```

### Восстановить скрипт
```yaml
service: shelly_scripts_backup.restore_script
data:
  device_id: shellyplus1pm-a8032ab12345
  script_id: 1
```

## Добавить кнопку на дашборд

```yaml
type: button
name: Backup Shelly Scripts
icon: mdi:backup-restore
tap_action:
  action: call-service
  service: shelly_scripts_backup.backup_now
```

## Автоматизация ежедневного бэкапа

```yaml
automation:
  - alias: "Daily Shelly Backup"
    trigger:
      - platform: time
        at: "02:00:00"
    action:
      - service: shelly_scripts_backup.backup_now
```

## Проверка работы

### Через логи
```bash
tail -f /config/home-assistant.log | grep shelly_scripts_backup
```

Вы должны увидеть:
```
INFO: Starting backup for device My Shelly (shellyplus1pm-xxx)
INFO: Backed up script my_automation (ID: 1) to /config/shelly_backups/...
INFO: Backup completed for device shellyplus1pm-xxx
```

### Через файловую систему
```bash
ls -la /config/shelly_backups/
```

## Часто задаваемые вопросы

**Q: Как часто создаются бэкапы?**  
A: По умолчанию каждые 24 часа. Настраивается при добавлении интеграции.

**Q: Сколько места занимают бэкапы?**  
A: Обычно 1-5 KB на скрипт. Для 10 скриптов ~ 50 KB.

**Q: Можно ли изменить путь сохранения?**  
A: Да, при настройке интеграции укажите свой путь.

**Q: Поддерживается ли мое устройство?**  
A: Все Shelly Gen2+ устройства со скриптами (Plus, Pro серии).

**Q: Как восстановить все скрипты сразу?**  
A: Используйте цикл в автоматизации или Node-RED для восстановления нескольких скриптов.

## Следующие шаги

- 📖 Изучите [полную документацию](README.md)
- 🤖 Посмотрите [примеры автоматизаций](examples/automations.yaml)
- 🎨 Добавьте [карточки на дашборд](examples/lovelace.yaml)
- 🔧 Узнайте о [Shelly API](docs/API.md)

## Нужна помощь?

- 🐛 [Сообщить о проблеме](https://github.com/yourusername/shelly_scripts_backup/issues)
- 💬 [Обсуждения](https://github.com/yourusername/shelly_scripts_backup/discussions)
- 📧 [Email автору](mailto:your@email.com)

---

**Приятного использования! 🎉**
