# 🚘 License Plate Annotation Demo Filter

**License Plate Annotation Demo Filter** is a lightweight [OpenFilter](https://github.com/PlainsightAI/openfilter)-based demo filter that overlays OCR-processed license plate text and cropped plate images onto video frames.

It integrates seamlessly with:
- [`filter-license-plate-detection`](https://github.com/PlainsightAI/filter-license-plate-detection)
- [`filter-crop`](https://github.com/PlainsightAI/filter-crop)
- [`filter-optical-character-recognition`](https://github.com/PlainsightAI/filter-optical-character-recognition)

[![PyPI version](https://img.shields.io/pypi/v/filter-license-annotation-demo.svg?style=flat-square)](https://pypi.org/project/filter-license-annotation-demo/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/PlainsightAI/filter-license-annotation-demo/blob/main/LICENSE)
![Build Status](https://github.com/PlainsightAI/filter-license-annotation-demo/actions/workflows/ci.yaml/badge.svg)

---

## ✨ Features

- 🖍️ Overlays OCR license plate text on the main frame
- 🖼️ Displays cropped license plate image as a top-left inset
- 🧠 Filters OCR output using a regex pattern for valid plates (e.g., `ABC1234`)
- 🧩 Designed to run after detection, cropping, and OCR filters in OpenFilter pipelines
- ⚙️ Fully configurable via CLI, code, or environment variables

---

## 📦 Installation

Install the latest version from PyPI:

```bash
pip install filter-license-annotation-demo
````

Or install from source:

```bash
# Clone the repo
git clone https://github.com/PlainsightAI/filter-license-annotation-demo.git
cd filter-license-annotation-demo

# (Optional but recommended) create a virtual environemnt:
python -m venv venv && source venv/bin/activate

# Install the filter
make install
```

---

## 🚀 Quick Start (CLI)

Run a full license plate pipeline using the CLI:

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
```

Or:

```bash
make run
```

Then open [http://localhost:8000](http://localhost:8000) to view annotated results.

---

## 🧰 Using from PyPI

After installing with:

```bash
pip install filter-license-annotation-demo
```

You can run the filter directly in code:

### Standalone

```python
from filter_license_annotation_demo.filter import FilterLicenseAnnotationDemo

if __name__ == "__main__":
    FilterLicenseAnnotationDemo.run()
```

### Multi-filter Pipeline

```python
from openfilter.filter_runtime.filter import Filter
from filter_license_plate_detection.filter import FilterLicensePlateDetection
from filter_crop.filter import FilterCrop
from filter_optical_character_recognition.filter import FilterOpticalCharacterRecognition
from filter_license_annotation_demo.filter import FilterLicenseAnnotationDemo
from openfilter.filter_runtime.filters.video_in import VideoIn
from openfilter.filter_runtime.filters.webvis import Webvis

if __name__ == '__main__':
    Filter.run_multi([
        (VideoIn, dict(
            sources='file://example_video.mp4!loop',
            outputs='tcp://*:5550',
        )),
        (FilterLicensePlateDetection, dict(
            sources='tcp://localhost:5550',
            outputs='tcp://*:5552',
        )),
        (FilterCrop, dict(
            sources='tcp://localhost:5552',
            outputs='tcp://*:5554',
            detection_key='license_plate_detection',
            detection_class_field='label',
            detection_roi_field='box',
            output_prefix='cropped_',
            mutate_original_frames=False,
            topic_mode='main_only',
        )),
        (FilterOpticalCharacterRecognition, dict(
            sources='tcp://localhost:5554',
            outputs='tcp://*:5556',
            topic_pattern='license_plate',
            ocr_engine='easyocr',
            forward_ocr_texts=True,
        )),
        (FilterLicenseAnnotationDemo, dict(
            sources='tcp://localhost:5556',
            outputs='tcp://*:5558',
            cropped_topic_suffix='license_plate',
        )),
        (Webvis, dict(
            sources='tcp://localhost:5558',
        )),
    ])
```

---

## 🔧 Configuration

| Field                  | Type    | Description                           | Example          |
| ---------------------- | ------- | ------------------------------------- | ---------------- |
| `cropped_topic_suffix` | `str`   | Topic with cropped plate images       | `"cropped_main"` |
| `font_scale`           | `float` | Font size multiplier for overlay text | `1.0`            |
| `font_thickness`       | `int`   | Thickness of text stroke              | `2`              |
| `inset_size`           | `tuple` | Width and height of the inset image   | `(200, 60)`      |
| `inset_margin`         | `tuple` | Offset from top-left corner           | `(10, 10)`       |
| `debug`                | `bool`  | Enable verbose debug logging          | `true`           |

All fields are also supported as environment variables using the `FILTER_` prefix (e.g., `FILTER_FONT_SCALE=1.2`).

---

## 🧪 Testing

Run all tests:

```bash
make test
```

Run individual test files:

```bash
pytest -v tests/test_filter_license_annotation_demo.py
```

---

## 🧩 How It Works

| Filter                                 | Role                                                    |
| -------------------------------------- | ------------------------------------------------------- |
| `filter-license-plate-detection`       | Detects license plates in frames                        |
| `filter-crop`                          | Crops detected license plates                           |
| `filter-optical-character-recognition` | Applies OCR to cropped license plate images             |
| `**This Filter**`                      | Overlays cropped plate image and OCR text on main frame |

OCR text is filtered using a regex (`^[A-Z]{3}[0-9]{4}$`). If no valid OCR is detected in the current frame, the last valid plate is reused for continuity.

---

## 🤝 Contributing

We welcome contributions! See our [CONTRIBUTING.md](https://github.com/PlainsightAI/filter-license-annotation-demo/blob/main/CONTRIBUTING.md).

**Tips**:

* Format with `black`
* Lint with `ruff`
* Add type hints and docstrings
* Write tests for all features
* Sign commits using DCO (`git commit -s`)

---

## 📄 License

Licensed under the [Apache 2.0 License](https://github.com/PlainsightAI/filter-license-annotation-demo/blob/main/LICENSE).

---

## 🙏 Acknowledgements

Thank you for using the License Plate Annotation Filter!

Questions or feedback? [Open an issue](https://github.com/PlainsightAI/filter-license-annotation-demo/issues/new/choose).