# Advanced Shelly

Automatic backup of scripts and device configuration from Shelly Gen2+ devices for Home Assistant.

## Features

- ✅ Scheduled backups of scripts and configuration
- ✅ Configurable backup interval and backup path
- ✅ Manual backup trigger
- ✅ Restore scripts from backup
- ✅ Restore device configuration from backup
- ✅ Support for multiple Shelly devices
- ✅ Optional Digest Auth (username `admin`)
- ✅ Sensors for last backup, script count, and connectivity

## Supported devices

All Shelly Gen2+ devices that support scripts:
- Shelly Plus 1/1PM
- Shelly Plus 2PM
- Shelly Plus I4
- Shelly Plus Plug S
- Shelly Pro series
- And other Gen2+ devices

**Important:** Gen1 devices are not supported because they do not provide script functionality.

## Quick start

### 1. Install via HACS

1. In HACS, go to "Integrations"
2. Click the three dots in the top-right corner → "Custom repositories"
3. Add the URL: `https://github.com/artemkaxboy/advanced-shelly`
4. Select the category "Integration"
5. Find "Advanced Shelly" in the integrations list
6. Click "Download"
7. Restart Home Assistant

### 2. Set up the integration

1. Go to Settings → Devices & Services
2. Click "+ Add Integration"
3. Find "Advanced Shelly"
4. Enter:
   - Device URL (e.g., `http://192.168.1.100`)
   - Device name (optional)
   - Password (optional; Digest Auth for `admin`)
   - Backup path (default: /config/shelly_backups)
   - Backup interval in seconds (default: 86400 = 24 hours)
5. Click "Submit"

The first backup will be created automatically during setup.

## Usage

### Backup structure

```
/config/shelly_backups/
└── shellyplus1pm-a8032ab12345/
    ├── device_config.json
    ├── 1_my_script.js       # Script code
    ├── 1_my_script.json     # Metadata
    ├── 2_automation.js
    └── 2_automation.json
```

### Available services

#### Create a manual backup
```yaml
service: advanced_shelly.backup_now
data:
  device_id: shellyplus1pm-a8032ab12345  # optional
```

#### Restore a script
```yaml
service: advanced_shelly.restore_script
data:
  device_id: shellyplus1pm-a8032ab12345
  script_id: 1
  backup_path: /config/shelly_backups/.../1_script.js  # optional
```

#### Restore device configuration
```yaml
service: advanced_shelly.restore_config
data:
  device_id: shellyplus1pm-a8032ab12345
  backup_path: /config/shelly_backups/.../device_config.json  # optional
```

## Documentation

- [Full documentation on GitHub](https://github.com/artemkaxboy/advanced-shelly)
- [Automation examples](https://github.com/artemkaxboy/advanced-shelly/blob/main/examples/automations.yaml)
- [Lovelace card examples](https://github.com/artemkaxboy/advanced-shelly/blob/main/examples/lovelace.yaml)
- [Shelly API documentation](https://github.com/artemkaxboy/advanced-shelly/blob/main/docs/API.md)

## Help and support

- 🐛 [Report an issue](https://github.com/artemkaxboy/advanced-shelly/issues)
- 💬 [Discussions](https://github.com/artemkaxboy/advanced-shelly/discussions)
- ⭐ [Star on GitHub](https://github.com/artemkaxboy/advanced-shelly)

## Security

- The integration works fully locally
- Scripts and configuration are stored as plain text files
- No data is transmitted outside your network
- Regular backups of the backup folder are recommended

---

**Enjoy! 🎉**
