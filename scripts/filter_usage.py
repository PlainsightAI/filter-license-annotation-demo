#!/usr/bin/env python3
"""
License Annotation Demo usage script

End-to-end pipeline:
VideoIn → LicensePlateDetection → Crop (topic license_plate) → OCR → LicenseAnnotationDemo → Webvis

Environment variables:
- VIDEO_INPUT: Path to input video (default: ./example_video.mp4)
- WEBVIS_PORT: Web UI port (default: 8000)
- FILTER_CROPPED_TOPIC_SUFFIX: Cropped topic name (default: license_plate)
- FILTER_FORWARD_UPSTREAM_DATA: Forward upstream non-image frames (default: true)
"""

import os
from openfilter.filter_runtime import Filter
from openfilter.filter_runtime.filters.video_in import VideoIn
from openfilter.filter_runtime.filters.webvis import Webvis
from filter_license_annotation_demo.filter import (
    FilterLicenseAnnotationDemo,
    FilterLicenseAnnotationDemoConfig,
)
# Upstream filters referenced in the Makefile pipeline
from filter_license_plate_detection.filter import FilterLicensePlateDetection
from filter_crop.filter import FilterCrop
from filter_optical_character_recognition.filter import (
    FilterOpticalCharacterRecognition,
    FilterOpticalCharacterRecognitionConfig,
)


def main():
    video_input = os.getenv("VIDEO_INPUT", "./example_video.mp4")
    cropped_suffix = os.getenv("FILTER_CROPPED_TOPIC_SUFFIX", "license_plate")
    forward_upstream = os.getenv("FILTER_FORWARD_UPSTREAM_DATA", "true").lower() == "true"
    webvis_port = int(os.getenv("WEBVIS_PORT", "8000"))

    # Derive a collision-free port chain: each node uses (out, out+1). Step by 2.
    base = int(os.getenv("PORT_BASE", "5550"))
    v_out = base           # VideoIn publishes here; listens on base+1
    det_out = base + 2     # Detector publishes here; listens on det_out+1
    crop_out = base + 4    # Crop publishes here; listens on crop_out+1
    ocr_out = base + 6     # OCR publishes here; listens on ocr_out+1
    annot_out = base + 8   # Annotation publishes here; listens on annot_out+1

    Filter.run_multi(
        [
            # 1) Video source
            (
                VideoIn,
                dict(
                    id="vidin",
                    sources=f"file://{video_input}!loop",
                    outputs=f"tcp://*:{v_out}",
                ),
            ),
            # 2) License plate detection
            (
                FilterLicensePlateDetection,
                dict(
                    id="detector",
                    sources=f"tcp://127.0.0.1:{v_out}",
                    outputs=f"tcp://*:{det_out}",
                    mq_log="pretty",
                ),
            ),
            # 3) Crop detected license plates into a side topic
            (
                FilterCrop,
                dict(
                    id="crop",
                    sources=f"tcp://127.0.0.1:{det_out}",
                    outputs=f"tcp://*:{crop_out}",
                    mq_log="pretty",
                    detection_key="license_plate_detection",
                    detection_class_field="label",
                    detection_roi_field="box",
                    output_prefix=f"{cropped_suffix}",
                    mutate_original_frames=False,
                    topic_mode="main_only",
                ),
            ),
            # 4) OCR over the cropped plate topic
            (
                FilterOpticalCharacterRecognition,
                FilterOpticalCharacterRecognitionConfig(
                    id="ocr",
                    sources=f"tcp://127.0.0.1:{crop_out}",
                    outputs=f"tcp://*:{ocr_out}",
                    mq_log="pretty",
                    topic_pattern=f"{cropped_suffix}",
                    ocr_engine="easyocr",
                    forward_ocr_texts=True,
                    write_output_file=False,
                    forward_upstream_data=True,
                ),
            ),
            # 5) Annotate main with cropped plate + text
            (
                FilterLicenseAnnotationDemo,
                FilterLicenseAnnotationDemoConfig(
                    id="license_annot",
                    sources=f"tcp://127.0.0.1:{ocr_out}",
                    outputs=f"tcp://*:{annot_out}",
                    mq_log="pretty",
                    cropped_topic_suffix=cropped_suffix,
                    forward_upstream_data=forward_upstream,
                ),
            ),
            # 6) Web visualization
            (
                Webvis,
                dict(id="webvis", sources=f"tcp://127.0.0.1:{annot_out}", port=webvis_port),
            ),
        ]
    )


if __name__ == "__main__":
    main()


