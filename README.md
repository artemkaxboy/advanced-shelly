# Advanced Shelly для Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![HACS][hacs-shield]][hacs]

![Project Maintenance][maintenance-shield]
[![Community Forum][forum-shield]][forum]

Кастомная интеграция для Home Assistant, которая автоматически создает резервные копии скриптов с устройств Shelly Gen2+.

## Возможности

- ✅ Автоматическое резервное копирование скриптов с устройств Shelly Gen2+
- ✅ Настраиваемый интервал резервного копирования
- ✅ Сохранение метаданных скриптов (имя, ID, статус включения)
- ✅ Ручной запуск резервного копирования через сервис
- ✅ Восстановление скриптов из резервной копии
- ✅ Поддержка нескольких устройств Shelly
- ✅ Простая настройка через UI

## Поддерживаемые устройства

Все устройства Shelly Gen2+, которые поддерживают скрипты:
- Shelly Plus 1/1PM
- Shelly Plus 2PM
- Shelly Plus I4
- Shelly Plus Plug S
- Shelly Pro 1/1PM/2/2PM
- Shelly Pro 3
- Shelly Pro 4PM
- И другие Gen2+ устройства

**Важно:** Устройства Gen1 не поддерживаются, так как они не имеют функционала скриптов.

## Установка

### Вариант 1: HACS (рекомендуется)

1. Убедитесь, что [HACS](https://hacs.xyz/) установлен в вашем Home Assistant
2. В HACS перейдите в "Integrations"
3. Нажмите на три точки в правом верхнем углу и выберите "Custom repositories"
4. Добавьте URL этого репозитория: `https://github.com/artemkaxboy/advanced-shelly`
5. Выберите категорию "Integration"
6. Нажмите "Add"
7. Найдите "Advanced Shelly" в списке и нажмите "Download"
8. Перезапустите Home Assistant

### Вариант 2: Ручная установка

1. Скопируйте папку `custom_components/advanced_shelly` в `config/custom_components/`
2. Перезапустите Home Assistant

## Настройка

1. Перейдите в Settings → Devices & Services → Add Integration
2. Найдите "Advanced Shelly"
3. Введите:
   - IP-адрес устройства Shelly
   - Название устройства (необязательно)
   - Путь для сохранения бэкапов (по умолчанию: `/config/shelly_backups`)
   - Интервал резервного копирования в секундах (по умолчанию: 86400 = 24 часа)
4. Нажмите "Submit"

Интеграция автоматически создаст начальный бэкап при настройке.

## Использование

### Структура бэкапов

Бэкапы сохраняются в следующей структуре:

```
/config/shelly_backups/
└── shellyplus1pm-a8032ab12345/
    ├── 1_my_script.js
    ├── 1_my_script.json
    ├── 2_automation.js
    └── 2_automation.json
```

Для каждого скрипта создается два файла:
- `.js` файл с кодом скрипта
- `.json` файл с метаданными (ID, имя, статус, информация об устройстве)

### Сервисы

#### advanced_shelly.backup_now

Запускает резервное копирование вручную.

```yaml
service: advanced_shelly.backup_now
data:
  device_id: shellyplus1pm-a8032ab12345  # необязательно, если не указано - бэкап всех устройств
```

#### advanced_shelly.restore_script

Восстанавливает скрипт из резервной копии.

```yaml
service: advanced_shelly.restore_script
data:
  device_id: shellyplus1pm-a8032ab12345
  script_id: 1
  backup_path: /config/shelly_backups/shellyplus1pm-a8032ab12345/1_my_script.js  # необязательно
```

### Автоматизации

#### Бэкап при изменении скрипта

Вы можете создать автоматизацию для бэкапа при внесении изменений:

```yaml
automation:
  - alias: "Backup Shelly scripts on change"
    trigger:
      - platform: state
        entity_id: input_boolean.script_modified  # ваш триггер
    action:
      - service: advanced_shelly.backup_now
```

#### Уведомление после бэкапа

```yaml
automation:
  - alias: "Notify after Shelly backup"
    trigger:
      - platform: time
        at: "02:00:00"
    action:
      - service: advanced_shelly.backup_now
      - service: notify.mobile_app
        data:
          message: "Shelly scripts backup completed"
```

## Логирование

Для включения подробного логирования добавьте в `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.advanced_shelly: debug
```

## Устранение неполадок

### Устройство не поддерживается

Убедитесь, что у вас устройство Shelly Gen2+. Устройства Gen1 не поддерживают скрипты.

### Не удается подключиться

1. Проверьте, что устройство доступно по сети
2. Убедитесь, что IP-адрес указан правильно
3. Проверьте, что устройство не заблокировано firewall

### Скрипты не сохраняются

1. Проверьте права доступа к папке бэкапов
2. Убедитесь, что на диске достаточно места
3. Проверьте логи Home Assistant для деталей ошибок

## Безопасность

- Интеграция хранит скрипты в виде обычных текстовых файлов
- Рекомендуется регулярно создавать резервные копии папки `/config/shelly_backups`
- Никакие данные не передаются за пределы вашей локальной сети

## Лицензия

MIT License

## Поддержка

Если вы нашли баг или хотите предложить новую функцию, создайте issue в GitHub репозитории.

## Благодарности

Спасибо сообществу Home Assistant и разработчикам Shelly за отличные продукты!

---

## Бейджи и ссылки

[releases-shield]: https://img.shields.io/github/release/artemkaxboy/advanced-shelly.svg?style=for-the-badge
[releases]: https://github.com/artemkaxboy/advanced-shelly/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/artemkaxboy/advanced-shelly.svg?style=for-the-badge
[commits]: https://github.com/artemkaxboy/advanced-shelly/commits/main
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[hacs]: https://github.com/hacs/integration
[license-shield]: https://img.shields.io/github/license/artemkaxboy/advanced-shelly.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40artemkaxboy-blue.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
