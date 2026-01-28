# Development and testing guide

## Project structure

```
custom_components/advanced_shelly/
├── __init__.py              # Integration core logic
├── config_flow.py           # UI setup
├── const.py                 # Constants
├── manifest.json            # Integration metadata
├── services.yaml            # Service descriptions
├── strings.json             # Base strings
├── translations/            # Translations
│   ├── en.json
│   └── ru.json
```

## Development requirements

- Python 3.11+
- Home Assistant Core 2024.1.0+
- Shelly Gen2+ device for testing

## Local development

### 1. Clone and install

```bash
# Clone the repo and link the integration folder into Home Assistant
cd /path/to/homeassistant/config
mkdir -p custom_components
cd custom_components
git clone https://github.com/artemkaxboy/advanced-shelly.git

# The integration is in custom_components/advanced_shelly
```

### 2. Install development dependencies

```bash
pip install -r requirements_dev.txt
```

Create `requirements_dev.txt`:
```
homeassistant>=2024.1.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-homeassistant-custom-component
aiohttp>=3.8.0
```

### 3. Configure the development environment

VS Code with these extensions is recommended:
- Python
- Home Assistant Config Helper
- YAML

`.vscode/settings.json` example:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

## Testing

### Unit tests

Create `tests/test_coordinator.py`:

```python
"""Tests for Advanced Shelly coordinator."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from homeassistant.core import HomeAssistant

from custom_components.advanced_shelly import ShellyBackupCoordinator


@pytest.mark.asyncio
async def test_update_device_status_success():
    """Test updating device status when the device is reachable."""
    hass = MagicMock(spec=HomeAssistant)
    coordinator = ShellyBackupCoordinator(hass, "http://192.168.1.100", None, "/tmp/backups")

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get_device_info.return_value = {"id": "test-device", "name": "Test Shelly"}

    with patch("custom_components.advanced_shelly.ShellyClient", return_value=mock_client):
        result = await coordinator.update_device_status()

    assert result is True
    assert coordinator.device_id == "test-device"
    assert coordinator.device_name == "Test Shelly"


@pytest.mark.asyncio
async def test_backup_scripts_no_scripts():
    """Test backup when the device has no scripts."""
    hass = MagicMock(spec=HomeAssistant)
    coordinator = ShellyBackupCoordinator(hass, "http://192.168.1.100", None, "/tmp/backups")

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get_device_info.return_value = {"id": "test-device", "name": "Test Shelly"}
    mock_client.get_script_list.return_value = {"scripts": []}
    mock_client.get_config.return_value = {"sys": {}}

    with patch("custom_components.advanced_shelly.ShellyClient", return_value=mock_client):
        await coordinator.backup_scripts()

    assert coordinator.script_count == 0
```

Run tests:
```bash
pytest tests/
```

### Integration testing

Use a real Shelly device for testing:

```bash
# Set environment variables
export SHELLY_TEST_URL="http://192.168.1.100"
export SHELLY_TEST_PASSWORD=""
export SHELLY_TEST_BACKUP_PATH="/tmp/shelly_test_backups"

# Run integration tests
pytest tests/integration/
```

### Manual testing

1. Restart Home Assistant
2. Check logs:
```bash
tail -f /config/home-assistant.log | grep advanced_shelly
```

3. Add the integration via the UI
4. Verify backup creation
5. Test services via Developer Tools → Services

## Debugging

### Enable debug logs

In `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.advanced_shelly: debug
    aiohttp: debug
```

### Use pdb

Add to code:
```python
import pdb; pdb.set_trace()
```

## Code checks

### Formatting

```bash
# Black formatter
black custom_components/advanced_shelly/

# isort for imports
isort custom_components/advanced_shelly/
```

### Linting

```bash
# pylint
pylint custom_components/advanced_shelly/

# flake8
flake8 custom_components/advanced_shelly/
```

### Type checking

```bash
# mypy
mypy custom_components/advanced_shelly/
```

## CI/CD

Example `.github/workflows/test.yml`:

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
          pylint custom_components/advanced_shelly/

      - name: Test with pytest
        run: |
          pytest tests/
```

## Publish to HACS

1. Create a release on GitHub:
```bash
git tag -a v1.0.15 -m "Release v1.0.15"
git push origin v1.0.15
```

2. Ensure `hacs.json` is filled out correctly

3. Submit a PR to the [HACS default repository](https://github.com/hacs/default)

## Documentation updates

When adding new features, update:
- README.md
- docs/API.md (if the API usage changes)
- examples/ (add usage examples)
- translations/ (add translations)

## Useful commands

```bash
# Validate JSON files
python -m json.tool custom_components/advanced_shelly/manifest.json

# Validate YAML files
yamllint custom_components/advanced_shelly/services.yaml

# Create archive for manual installation
tar -czf advanced_shelly.tar.gz custom_components/advanced_shelly/

# Clear __pycache__
find . -type d -name __pycache__ -exec rm -rf {} +
```

## Tips

1. **Versioning**: Follow [Semantic Versioning](https://semver.org/)
2. **Commits**: Use [Conventional Commits](https://www.conventionalcommits.org/)
3. **Changelog**: Maintain CHANGELOG.md to track changes
4. **Security**: Never commit passwords or device URLs
5. **Compatibility**: Test with the latest Home Assistant version

## Known issues

- Gen1 devices are not supported
- Digest Auth authentication can be unstable
- Large scripts (>10KB) may upload slowly

## Roadmap

Planned improvements:
- [ ] Incremental backups
- [ ] Backup encryption
- [ ] Git integration for versioning
- [ ] Dashboard for change history
- [ ] Automatic recovery on errors
- [ ] Webhook support for notifications
