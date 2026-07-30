# Changelog
License Annotation Demo filter release notes

## [Unreleased]

### Changed

- Bump the openfilter dependency to 1.2.0

## v0.1.11 - 2026-04-27

### Added
- Add Dockerfile and .dockerignore for Docker Hub publishing

## v0.1.10 - 2026-04-24

### Changed
- Fix release workflow secret names: `PYPI_API_TOKEN` → `PLAINSIGHT_PYPI_TOKEN`, `DOCKERHUB_TOKEN` → `DOCKERHUB_ACCESS_TOKEN` (org-level secret names). Without this the PyPI / Docker Hub tokens resolved to empty and no package has been published since the migration.
- Bump openfilter dependency to `>=0.1.30`.
- Remove redundant ci.yaml (shared workflow handles PR testing).
- Add push + pull_request triggers to create-release.yaml.

### Notes
- `v0.1.8` and `v0.1.9` were tagged but never published due to the secret mapping issue fixed here; `v0.1.10` is the first successful publish since the org secret migration.


## v0.1.7 - 2025-09-29

### Changed
- Updated version to v0.1.7


## v0.1.6 - 2025-09-27

### Changed
- Updated documentation

## v0.1.5 - 2025-08-07

### Changed
- Updated dependencies
- Added Python 3.13 support

## v0.1.4 - 2025-08-07

### Changed
- Updated dependencies

## v0.1.3 - 2025-08-01

### Changed
- Updated dependencies

## v0.1.2 - 2025-07-16

### Changed
- Updated dependencies

## v0.1.1 - 2025-05-22

### Changed
- Updated dependencies

## v0.1.0 - 2025-05-22

### Added
- Initial release of the Plate ID OCR Filter for visualizing OCR license plate results on video frames.
- Overlays OCR-detected license plate text onto the main frame using:
  - Automatic font scaling to fit within a padded text box.
  - Configurable font scale and thickness.
- Imposes the corresponding cropped license plate image (if available) in the top-left corner of the main frame:
  - Uses `inset_size` and `inset_margin` to control placement and size.
- OCR filtering:
  - Validates and filters OCR strings using a regex pattern for standard license plate format (`ABC1234`).
  - Caches and reuses the last seen valid plate when no new valid text is found.
- Customizable behavior via config:
  - `cropped_topic_suffix` to specify which frame topic contains cropped license plates.
  - `font_scale`, `font_thickness`, `inset_size`, `inset_margin` tunable via config or environment variables.
- Frame integrity:
  - Ensures main frame is only updated when both image and overlay bounds are valid.
  - Gracefully skips overlays when dimensions do not fit.
- Standalone CLI support via `FilterLicenseAnnotationDemo.run()`.

### Changed
- Improved config normalization with `.env` support for all key fields.
- Centralized inset and font sizing logic to reduce duplication and improve robustness.
- Enhanced debug logging to show setup state and filtered OCR text results.

### Fixed
- Fixed parsing of `inset_size` and `inset_margin` from string format (e.g., `"200x60"`) to tuple.
- Resolved potential errors from overlaying text or images outside the frame bounds.
- Ensured fallback to previous license plate text avoids unnecessary frame updates.

### Internal
- Added detailed docstrings for config class fields and core methods.
- Included validation for environment-derived config values.
- Improved log output clarity during setup and processing phases.
