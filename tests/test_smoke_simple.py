"""
Smoke tests for License Annotation Demo filter.
"""

import numpy as np
from openfilter.filter_runtime.filter import Frame
from filter_license_annotation_demo.filter import (
    FilterLicenseAnnotationDemo,
    FilterLicenseAnnotationDemoConfig,
)


class TestSmokeSimple:
    def create_frame(self, w=320, h=240):
        img = np.zeros((h, w, 3), dtype=np.uint8)
        return Frame(img, {"meta": {}}, "BGR")

    def test_initialization_and_process_all_topics(self):
        cfg = FilterLicenseAnnotationDemoConfig(
            cropped_topic_suffix="license_plate",
            forward_upstream_data=True,
        )
        f = FilterLicenseAnnotationDemo(cfg)
        f.setup(cfg)

        main = self.create_frame()
        cropped = Frame(self.create_frame(64, 32).rw_bgr.image, {"meta": {"ocr_texts": ["ABC1234"]}}, "BGR")

        frames = {
            "stream2": self.create_frame(),
            "main": main,
            "license_plate": cropped,
            "telemetry": Frame({"only": "data"}),
        }

        out = f.process(frames)
        # main must be first
        assert list(out.keys())[0] == "main"
        # all topics present (including forwarded non-image)
        assert set(out.keys()) >= {"main", "stream2", "license_plate", "telemetry"}

    def test_forwarding_disabled(self):
        cfg = FilterLicenseAnnotationDemoConfig(
            cropped_topic_suffix="license_plate",
            forward_upstream_data=False,
        )
        f = FilterLicenseAnnotationDemo(cfg)
        f.setup(cfg)

        frames = {
            "main": self.create_frame(),
            "telemetry": Frame({"only": "data"}),
        }

        out = f.process(frames)
        assert "main" in out and "telemetry" not in out


