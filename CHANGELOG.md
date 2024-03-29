# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2024-02-05

### Added

- Add support for processing the new offspot file-manager (#104)

### Changed

- Colors assigned to package names are not random anymore (#109)
- Many small UI adjustments (#106)

### Fixed

- Top toolbar is not working properly when there is no yearly aggregation (#101)

## [0.2.1] - 2024-01-26

### Added

- Backend: add support for file-manager in addition to EduPi (#104)

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
