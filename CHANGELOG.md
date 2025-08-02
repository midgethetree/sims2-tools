# Changelog

## Unreleased - yyyy-mm-dd

### Changed

- error logs are now generated in simidge/simtracker folders in the following locations instead of the same folder as simidge/simtracker itself and will rotate when they get too big:
  - AppData\Roaming (Windows)
  - $XDG_STATE_HOME (Linux/MacOS)
  - ~/.local/state (Linux/MacOS if $XDG_STATE_HOME is not set)
- simidge: added settings dialog to allow changing the paths to Downloads and objects.package

### Added

-

### Removed

-

### Fixed

-

## [0.2.0] - 2025-07-12

### Changed

- **Breaking:** replace locations.txt with ini config files in the user's config directory for both simtracker and simidge (read the docs for [simidge](/docs/simidge/config.md) and [simtracker](/docs/simtracker/config.md) for more information)
- reorganized/refactored codebase for greater readability and maintainability

### Added

- simtracker: added support for configuration for numerous sims data in the config file to support custom genetics, careers, turn-on replacement mods, and more ([read the docs](/docs/simtracker/config.md) for more information)
- simidge: Find Translated / Empty Strings: strings eligible to be "cleaned up" in simpe appear in search results
- simidge: Find Translates / Empty Strings: skip lua string when looking for strings with comments
