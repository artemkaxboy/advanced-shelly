# Advanced Shelly for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![HACS][hacs-shield]][hacs]

![Project Maintenance][maintenance-shield]
[![Community Forum][forum-shield]][forum]

A custom Home Assistant integration that automatically backs up scripts and device configuration from Shelly Gen2+ devices.

## Features

- ✅ Automatic scheduled backups of scripts and device configuration
- ✅ Configurable backup interval and backup path
- ✅ Manual backup trigger via service
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
- Shelly Pro 1/1PM/2/2PM
- Shelly Pro 3
- Shelly Pro 4PM
- And other Gen2+ devices

**Important:** Gen1 devices are not supported because they do not provide script functionality.

## Installation

### Option 1: HACS (recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed in your Home Assistant
2. In HACS, go to "Integrations"
3. Click the three dots in the top-right corner and select "Custom repositories"
4. Add the URL of this repository: `https://github.com/artemkaxboy/advanced-shelly`
5. Select the category "Integration"
6. Click "Add"
7. Find "Advanced Shelly" in the list and click "Download"
8. Restart Home Assistant

### Option 2: Manual installation

1. Copy the `custom_components/advanced_shelly` folder into `config/custom_components/`
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services → Add Integration
2. Find "Advanced Shelly"
3. Enter:
   - Device URL (e.g., `http://192.168.1.100`)
   - Device name (optional)
   - Password (optional; Digest Auth for `admin`)
   - Backup path (default: `/config/shelly_backups`)
   - Backup interval in seconds (default: 86400 = 24 hours, min 3600, max 604800)
4. Click "Submit"

The integration creates an initial backup automatically during setup.

## Usage

### Backup structure

Backups are stored with the following structure:

```
/config/shelly_backups/
└── shellyplus1pm-a8032ab12345/
    ├── device_config.json
    ├── 1_my_script.js
    ├── 1_my_script.json
    ├── 2_automation.js
    └── 2_automation.json
```

Each script creates two files:
- A `.js` file with the script code
- A `.json` file with metadata (ID, name, enable, device ID, device name)

### Services

#### advanced_shelly.backup_now

Starts a manual backup. If `device_id` is omitted, all configured devices are backed up.

```yaml
service: advanced_shelly.backup_now
data:
  device_id: shellyplus1pm-a8032ab12345  # optional
```

#### advanced_shelly.restore_script

Restores a script from backup.

```yaml
service: advanced_shelly.restore_script
data:
  device_id: shellyplus1pm-a8032ab12345
  script_id: 1
  backup_path: /config/shelly_backups/shellyplus1pm-a8032ab12345/1_my_script.js  # optional
```

#### advanced_shelly.restore_config

Restores device configuration from backup.

```yaml
service: advanced_shelly.restore_config
data:
  device_id: shellyplus1pm-a8032ab12345
  backup_path: /config/shelly_backups/shellyplus1pm-a8032ab12345/device_config.json  # optional
```

### Entities

- Sensor: `Last backup` (timestamp)
- Sensor: `Script count` (number of scripts on the device)
- Binary sensor: `Connectivity` (device online/offline)

The last backup sensor exposes extra attributes:
- `device_id`
- `backup_count`
- `last_error`

The connectivity sensor exposes extra attributes:
- `last_seen`
- `device_id`

### Automations

#### Backup when a script changes

```yaml
automation:
  - alias: "Backup Shelly scripts on change"
    trigger:
      - platform: state
        entity_id: input_boolean.script_modified  # your trigger
    action:
      - service: advanced_shelly.backup_now
```

#### Notification after backup

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

## Logging

To enable verbose logging, add this to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.advanced_shelly: debug
```

## Troubleshooting

### Device not supported

Make sure you have a Shelly Gen2+ device. Gen1 devices do not support scripts.

### Unable to connect

1. Check that the device is reachable on the network
2. Make sure the URL is correct
3. Ensure the device is not blocked by a firewall

### Scripts are not saved

1. Check permissions on the backup folder
2. Ensure there is enough disk space
3. Check Home Assistant logs for error details

## Security

- The integration stores scripts as plain text files
- The device configuration is stored in `device_config.json`
- Regularly back up the `/config/shelly_backups` folder
- No data is transmitted outside your local network

## License

MIT License

## Support

If you found a bug or want to suggest a new feature, create an issue in the GitHub repository.

## Acknowledgments

Thanks to the Home Assistant community and the Shelly developers for great products!

---

## Badges and links

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
