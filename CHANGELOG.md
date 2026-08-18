# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Refactored `src/misbot/config.py` to use Pydantic Settings. All configuration is now defined in the `Settings` class.
- Secured the `/player/*` endpoints by validating access tokens against the configured JWKS and enforcing the required scopes.
- Added the `misbot-app-migrate.container` Quadlet unit so the deployment can run database migrations.

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [0.2.0] - 2026-03-07

### Changed

- Replaced `last_seen` player tracking with session-based approach to correctly handle out-of-order requests when calculating player time spent.


## [0.1.0] - 2026-01-29

### Added

- Initial raw implementation of the `misbot` web application, integrating a web server and a Telegram bot, with support for an SQLite database and Alembic migrations.


[unreleased]: https://github.com/stratila/HookEmitter/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/stratila/HookEmitter/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/stratila/HookEmitter/compare/e639ed9...v0.1.0

