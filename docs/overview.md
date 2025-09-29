---
title: License Plate Annotation Demo
sidebar_label: Overview
sidebar_position: 1
---

The **License Plate Annotation Demo Filter** is a lightweight [OpenFilter](https://github.com/PlainsightAI/openfilter)-based filter that overlays OCR-processed license plate text and cropped plate images onto video frames.  
It is designed to work **in combination with detection, cropping, and OCR filters**, and provides an intuitive way to visualize the results of a full license plate recognition pipeline.

This document is automatically published to production documentation on every production release.

---

## ✨ Key Features

- 🖍️ Draws OCR license plate text directly onto video frames
- 🖼️ Displays cropped plate image as a corner inset
- 🧠 Filters OCR output using a regex (e.g., `ABC1234`)
- 🔁 Maintains the last known valid plate if current OCR fails
- 🔧 Fully configurable via CLI flags or `FILTER_` environment variables
- 🔀 Optional pass-through of upstream non-image frames via `forward_upstream_data`
- 🔄 Processes all received topics and returns `main` first
 - 📦 Compatible with OpenFilter CLI and multi-stage pipelines

---

## 🚀 Full Pipeline Example

This filter is not standalone. It expects metadata and frame input from earlier filters in a pipeline:

```bash
openfilter run \
  - VideoIn \
      --sources 'file://example_video.mp4!loop' \
  - filter_license_plate_detection.filter.FilterLicensePlateDetection \
  - filter_crop.filter.FilterCrop \
      --detection_key license_plate_detection \
      --detection_class_field label \
      --detection_roi_field box \
      --output_prefix cropped_ \
      --mutate_original_frames false \
      --topic_mode main_only \
  - filter_optical_character_recognition.filter.FilterOpticalCharacterRecognition \
      --topic_pattern 'license_plate' \
      --ocr_engine easyocr \
      --forward_ocr_texts true \
  - filter_license_annotation_demo.filter.FilterLicenseAnnotationDemo \
      --cropped_topic_suffix license_plate \
  - Webvis
````

You can also run the pipeline using the single-process usage script:

```bash
WEBVIS_PORT=8002 \\
VIDEO_INPUT=./example_video.mp4 \\
FILTER_CROPPED_TOPIC_SUFFIX=license_plate \\
FILTER_FORWARD_UPSTREAM_DATA=true \\
python scripts/filter_usage.py
```

This pipeline:

1. Reads the input video
2. Detects license plates
3. Crops detected plates
4. Runs OCR on cropped regions
5. Draws the results on the original video stream
6. Displays output in `Webvis`

---

## ⚙️ Configuration Options

| Field                  | Type    | Description                                      | Example           |
| ---------------------- | ------- | ------------------------------------------------ | ----------------- |
| `cropped_topic_suffix` | `str`   | Topic containing the cropped license plate image | `"license_plate"` |
| `font_scale`           | `float` | Font size multiplier for overlay text            | `1.0`             |
| `font_thickness`       | `int`   | Stroke thickness of the text                     | `2`               |
| `inset_size`           | `tuple` | Dimensions `(width, height)` of the inset image  | `(200, 60)`       |
| `inset_margin`         | `tuple` | Margin from the top-left corner                  | `(10, 10)`        |
| `debug`                | `bool`  | Enable debug logging                             | `true`            |

These can also be configured using environment variables:

```bash
export FILTER_FONT_SCALE=1.2
export FILTER_INSET_MARGIN=20x10
```

---

## 🧠 Behavior and Logic

* **Text Overlay**: OCR results from the cropped frame’s `meta.ocr_texts` field are filtered using a regex and drawn onto the main frame.
* **Fallback**: If no valid OCR text is found, the last valid plate is reused.
* **Inset Image**: The cropped license plate image is drawn in the top-left corner using the configured `inset_size` and `inset_margin`.
* **Safety Checks**: The filter skips overlays if dimensions would exceed the frame or required input is missing.
* **Output**: Overlays are rendered in-place; output is returned on the `"main"` topic.

---

## 🧩 Integration with Other Filters

| Filter                                 | Role                                            |
| -------------------------------------- | ----------------------------------------------- |
| `filter-license-plate-detection`       | Detects license plates in incoming frames       |
| `filter-crop`                          | Crops ROIs from detected plates                 |
| `filter-optical-character-recognition` | Applies OCR to cropped images                   |
| `**This Filter**`                      | Overlays text and cropped image onto main frame |

This filter **requires upstream OCR** and **cropped frames** with attached metadata.

---

## 🧪 Testing

You can run the test suite using:

```bash
make test
```

Or individually:

```bash
pytest -v tests/test_filter_license_annotation_demo.py
```

Make sure to test both visual overlays and environment-driven configuration paths.

---

## 🧼 Notes

* The expected format for `inset_size` and `inset_margin` via environment variables is `"WIDTHxHEIGHT"` (e.g., `200x60`)
* Regex filtering uses the pattern: `^[A-Z]{3}[0-9]{4}$`
* Debug mode logs OCR input, fallback states, and drawing decisions

---

For development instructions and contribution guidelines, see the [CONTRIBUTING guide](https://github.com/PlainsightAI/filter-license-annotation-demo/blob/main/CONTRIBUTING.md).