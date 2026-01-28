# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.15] - 2025-01-28

### Added
- Device configuration backup (`device_config.json`) using Shelly GetConfig
- `restore_config` service to restore device configuration
- Connectivity binary sensor for device online/offline status
- Last backup timestamp sensor and script count sensor
- Options flow to change backup interval and backup path

### Changed
- Backup process now updates entity state and backup metrics after each run
- Script metadata includes device ID and device name

## [1.0.1] - 2025-01-24

### Fixed
- Fixed `KeyError: 'title'` when adding a device via the UI
- Improved error handling in the config flow
- Added detailed logging to simplify debugging
- Improved connection error messages
- Added handling for different device response parsing errors

## [1.0.0] - 2025-01-24

### Added
- Initial release of the Advanced Shelly integration
- Automatic backup of scripts from Shelly Gen2+ devices
- Configurable backup interval
- Script metadata storage (name, ID, status)
- `backup_now` service for manual backup
- `restore_script` service to restore scripts from backup
- Support for multiple Shelly devices
- UI setup (config flow)
- Russian and English localization
- Detailed documentation and usage examples
- Automation examples
- Lovelace card examples
- Shelly API documentation
- Development guide

### Features
- Compatible with Home Assistant 2024.1.0+
- Supports all Shelly Gen2+ devices with scripts
- Automatic creation of backup directory structure
- Stores scripts in text format for easy viewing
- Stores metadata in JSON format
- Periodic automatic backups
- Connection check during setup
- Connection error handling

[Unreleased]: https://github.com/artemkaxboy/advanced-shelly/compare/v1.0.15...HEAD
[1.0.15]: https://github.com/artemkaxboy/advanced-shelly/releases/tag/v1.0.15
[1.0.1]: https://github.com/artemkaxboy/advanced-shelly/releases/tag/v1.0.1
[1.0.0]: https://github.com/artemkaxboy/advanced-shelly/releases/tag/v1.0.0
