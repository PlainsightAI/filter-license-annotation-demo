"""
Integration tests for License Annotation Demo config normalization.
"""

import os
import pytest

from filter_license_annotation_demo.filter import (
    FilterLicenseAnnotationDemo,
    FilterLicenseAnnotationDemoConfig,
)


class TestIntegrationConfigNormalization:
    def test_string_to_type_conversions(self):
        cfg = {
            "cropped_topic_suffix": "license_plate",
            "font_scale": "1.25",
            "font_thickness": "3",
            "inset_size": "220x80",
            "inset_margin": "12x14",
            "debug": "true",
            "forward_upstream_data": "false",
        }

        normalized = FilterLicenseAnnotationDemo.normalize_config(cfg)

        assert normalized.cropped_topic_suffix == "license_plate"
        assert isinstance(normalized.font_scale, float) and normalized.font_scale == 1.25
        assert isinstance(normalized.font_thickness, int) and normalized.font_thickness == 3
        assert normalized.inset_size == (220, 80)
        assert normalized.inset_margin == (12, 14)
        assert normalized.debug is True
        assert normalized.forward_upstream_data is False

    def test_env_loading(self, monkeypatch):
        monkeypatch.setenv("FILTER_CROPPED_TOPIC_SUFFIX", "lp")
        monkeypatch.setenv("FILTER_FONT_SCALE", "1.1")
        monkeypatch.setenv("FILTER_FONT_THICKNESS", "4")
        monkeypatch.setenv("FILTER_INSET_SIZE", "210x70")
        monkeypatch.setenv("FILTER_INSET_MARGIN", "8x9")
        monkeypatch.setenv("FILTER_DEBUG", "true")
        monkeypatch.setenv("FILTER_FORWARD_UPSTREAM_DATA", "true")

        try:
            normalized = FilterLicenseAnnotationDemo.normalize_config({})
            assert normalized.cropped_topic_suffix == "lp"
            assert normalized.font_scale == 1.1
            assert normalized.font_thickness == 4
            assert normalized.inset_size == (210, 70)
            assert normalized.inset_margin == (8, 9)
            assert normalized.debug is True
            assert normalized.forward_upstream_data is True
        finally:
            for key in [
                "FILTER_CROPPED_TOPIC_SUFFIX",
                "FILTER_FONT_SCALE",
                "FILTER_FONT_THICKNESS",
                "FILTER_INSET_SIZE",
                "FILTER_INSET_MARGIN",
                "FILTER_DEBUG",
                "FILTER_FORWARD_UPSTREAM_DATA",
            ]:
                if key in os.environ:
                    del os.environ[key]


