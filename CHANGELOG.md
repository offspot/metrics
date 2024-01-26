# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2024-01-26

### Fixed

- Backend: Indicator processor sometimes re-process an already recorded period after an application restarts (#97)

## [0.2.0] - 2024-01-23

### Added

- Implement the total usage details page (#55)
- Implement the package popularity details page (#53)
- Implement a simplified version of top toolbar mobile version (#89)

### Changed

- Remove the footer (#63)
- Revisit backend logic to fix concurrency issue and cope with high log volume (#41 and #42)
- Make backend log level customizable (#40)
- Use colors from an accessible color scheme (#86)
- Upgrade Python (3.12) + Python and Node.JS dependencies (#73)
- Migrate Docker image to alpine instead of slim-bookworm (#72)

### Fixed

- Include a better system description in README.md (#12)
- Fallback logo image should be a PNG (#93)
- Fix responsivness of top toolbar on medium screens (#77)
- Do not consider there are only Caddy files in the log folder (#81)

## [0.1.0] - 2023-12-21

### Added

- Initial release
