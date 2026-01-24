# Руководство по разработке и тестированию

## Структура проекта

```
shelly_scripts_backup/
├── __init__.py              # Основная логика интеграции
├── config_flow.py           # Настройка через UI
├── const.py                 # Константы
├── manifest.json            # Метаданные интеграции
├── services.yaml            # Описание сервисов
├── strings.json             # Базовые строки
├── translations/            # Переводы
│   ├── en.json
│   └── ru.json
├── examples/                # Примеры использования
│   ├── automations.yaml
│   └── lovelace.yaml
└── docs/                    # Документация
    └── API.md
```

## Требования для разработки

- Python 3.11+
- Home Assistant Core 2024.1.0+
- Shelly Gen2+ устройство для тестирования

## Локальная разработка

### 1. Клонирование и установка

```bash
# Клонировать в custom_components Home Assistant
cd /path/to/homeassistant/config
mkdir -p custom_components
cd custom_components
git clone <your-repo> shelly_scripts_backup
```

### 2. Установка зависимостей для разработки

```bash
pip install -r requirements_dev.txt
```

Создайте `requirements_dev.txt`:
```
homeassistant>=2024.1.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-homeassistant-custom-component
aiohttp>=3.8.0
```

### 3. Настройка среды разработки

Рекомендуется использовать VS Code с расширениями:
- Python
- Home Assistant Config Helper
- YAML

Настройки `.vscode/settings.json`:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

## Тестирование

### Юнит-тесты

Создайте `tests/test_init.py`:

```python
"""Tests for Shelly Scripts Backup integration."""
import pytest
from unittest.mock import patch, MagicMock
from homeassistant.core import HomeAssistant

from custom_components.shelly_scripts_backup import (
    ShellyBackupCoordinator,
)


@pytest.mark.asyncio
async def test_get_device_info():
    """Test getting device info."""
    hass = MagicMock(spec=HomeAssistant)
    coordinator = ShellyBackupCoordinator(hass, "192.168.1.100", "/tmp/backups")
    
    with patch.object(coordinator, '_make_request') as mock_request:
        mock_request.return_value = {
            "id": "test-device",
            "name": "Test Shelly",
            "gen": 2
        }
        
        result = await coordinator.get_device_info()
        assert result["id"] == "test-device"
        assert result["gen"] == 2


@pytest.mark.asyncio
async def test_backup_scripts():
    """Test backing up scripts."""
    hass = MagicMock(spec=HomeAssistant)
    coordinator = ShellyBackupCoordinator(hass, "192.168.1.100", "/tmp/backups")
    
    with patch.object(coordinator, 'get_device_info') as mock_info, \
         patch.object(coordinator, 'get_scripts_list') as mock_list, \
         patch.object(coordinator, 'get_script_code') as mock_code:
        
        mock_info.return_value = {"id": "test-device", "name": "Test"}
        mock_list.return_value = [{"id": 1, "name": "test_script"}]
        mock_code.return_value = "let x = 1;"
        
        await coordinator.backup_scripts()
        
        mock_info.assert_called_once()
        mock_list.assert_called_once()
        mock_code.assert_called_once_with(1)
```

Запуск тестов:
```bash
pytest tests/
```

### Интеграционное тестирование

Используйте реальное устройство Shelly для тестирования:

```bash
# Установите переменные окружения
export SHELLY_TEST_IP="192.168.1.100"
export SHELLY_TEST_BACKUP_PATH="/tmp/shelly_test_backups"

# Запустите интеграционные тесты
pytest tests/integration/
```

### Ручное тестирование

1. Перезапустите Home Assistant
2. Проверьте логи:
```bash
tail -f /config/home-assistant.log | grep shelly_scripts_backup
```

3. Добавьте интеграцию через UI
4. Проверьте создание бэкапов
5. Протестируйте сервисы через Developer Tools → Services

## Отладка

### Включение debug логов

В `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.shelly_scripts_backup: debug
    aiohttp: debug
```

### Использование pdb

Добавьте в код:
```python
import pdb; pdb.set_trace()
```

### Просмотр HTTP запросов

```python
import logging

_LOGGER = logging.getLogger(__name__)

async def _make_request(self, endpoint: str, params: dict | None = None) -> dict:
    url = f"http://{self.host}{endpoint}"
    _LOGGER.debug("Making request to %s with params %s", url, params)
    # ... rest of code
```

## Проверка кода

### Форматирование

```bash
# Black formatter
black custom_components/shelly_scripts_backup/

# isort для импортов
isort custom_components/shelly_scripts_backup/
```

### Линтинг

```bash
# pylint
pylint custom_components/shelly_scripts_backup/

# flake8
flake8 custom_components/shelly_scripts_backup/
```

### Проверка типов

```bash
# mypy
mypy custom_components/shelly_scripts_backup/
```

## CI/CD

Пример `.github/workflows/test.yml`:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements_dev.txt
      
      - name: Lint with pylint
        run: |
          pylint custom_components/shelly_scripts_backup/
      
      - name: Test with pytest
        run: |
          pytest tests/
```

## Публикация в HACS

1. Создайте релиз в GitHub:
```bash
git tag -a v1.0.0 -m "First release"
git push origin v1.0.0
```

2. Убедитесь, что `hacs.json` заполнен правильно

3. Отправьте PR в [HACS default repository](https://github.com/hacs/default)

## Обновление документации

При добавлении новых фич обновите:
- README.md
- API.md (если меняется API)
- examples/ (добавьте примеры использования)
- translations/ (добавьте переводы)

## Полезные команды

```bash
# Проверить JSON файлы
python -m json.tool manifest.json

# Проверить YAML файлы
yamllint services.yaml

# Создать архив для ручной установки
tar -czf shelly_scripts_backup.tar.gz shelly_scripts_backup/

# Очистить __pycache__
find . -type d -name __pycache__ -exec rm -rf {} +
```

## Советы

1. **Версионирование**: Следуйте [Semantic Versioning](https://semver.org/)
2. **Коммиты**: Используйте [Conventional Commits](https://www.conventionalcommits.org/)
3. **Changelog**: Ведите CHANGELOG.md для отслеживания изменений
4. **Безопасность**: Никогда не коммитьте пароли или IP-адреса
5. **Совместимость**: Тестируйте с последней версией Home Assistant

## Известные проблемы

- Устройства Gen1 не поддерживаются
- Аутентификация Digest Auth может работать нестабильно
- Большие скрипты (>10KB) могут загружаться медленно

## Дорожная карта

Планируемые улучшения:
- [ ] Поддержка инкрементных бэкапов
- [ ] Шифрование бэкапов
- [ ] Интеграция с Git для версионирования
- [ ] Dashboard для просмотра истории изменений
- [ ] Автоматическое восстановление при ошибках
- [ ] Поддержка webhook для уведомлений
