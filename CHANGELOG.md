# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security


## [0.3.0] - 2026-08-29

### Added 
- Added the `misbot-app-migrate.container` Quadlet unit so the deployment can run database migrations.
- Added an internal PUT `/players/update-from-json` endpoint for bulk updates of player records. Added a nickname column to the players table. Refactored the move queries function from the exec module into the queries package.
- Added GET `/player/monthly-stat` endpoint and the `get_monthly_player_stat` db query accordingly.
- Added `type` to the `channels` table. Types now are `logger` and the `regular`. Integrate monthly stat with Telegram Bot that could post it to the regular channel type.
- Added POST `/player/send-stat-from-json` to send stored chat statistics that are missing from the database.

### Changed
- Refactored `src/misbot/config.py` to use Pydantic Settings. All configuration is now defined in the `Settings` class.
- Refactored FastAPI routes by adding `players` and `telegram` routers, and added `services` module.

### Security
- Secured the `/player/*` endpoints by validating access tokens against the configured JWKS and enforcing the required scopes.


### Fixed
- `send_monthly_stat_message` now returns the list of messages split by the 4096-character message limit.


## [0.2.0] - 2026-03-07

### Changed

- Replaced `last_seen` player tracking with session-based approach to correctly handle out-of-order requests when calculating player time spent.


## [0.1.0] - 2026-01-29

### Added

- Initial raw implementation of the `misbot` web application, integrating a web server and a Telegram bot, with support for an SQLite database and Alembic migrations.


[unreleased]: https://github.com/stratila/HookEmitter/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/stratila/HookEmitter/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/stratila/HookEmitter/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/stratila/HookEmitter/compare/e639ed9...v0.1.0