# Changelog
License Plate Annotation Filter release notes

## [Unreleased]

## v0.1.5 - 2025-08-07

# Changed
- Updated dependencies
- Added Python 3.13 support

## v0.1.4 - 2025-08-07

# Changed
- Updated dependencies

## v0.1.3 - 2025-08-01

# Changed
- Updated dependencies

## v0.1.2 - 2025-07-16

# Changed
- Updated dependencies

## v0.1.1 - 2025-05-22

# Changed
- Updated dependencies

## v0.1.0 - 2025-05-22

### Added
- Initial release of the License Plate Annotation Demo filter for visualizing OCR license plate results on video frames.
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
