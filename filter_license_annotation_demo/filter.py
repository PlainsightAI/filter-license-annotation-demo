import logging
import os
import re
import cv2
import numpy as np
from openfilter.filter_runtime.filter import FilterConfig, Filter, Frame

__all__ = ['FilterLicenseAnnotationDemoConfig', 'FilterLicenseAnnotationDemo']

logger = logging.getLogger(__name__)

class FilterLicenseAnnotationDemoConfig(FilterConfig):
    cropped_topic_suffix: str = "cropped_main"  # Default cropped topic to expect
    font_scale: float = 1.0  # Font scale for overlayed OCR text
    font_thickness: int = 2  # Font thickness for text
    inset_size: tuple = (200, 60)  # (width, height) of inset image
    inset_margin: tuple = (10, 10)  # (x, y) margin from top-left corner
    debug: bool = False  # Enable debug logging

class FilterLicenseAnnotationDemo(Filter):
    """Annotates frames with OCR texts and imposes cropped license plate images."""

    @classmethod
    def normalize_config(cls, config: FilterLicenseAnnotationDemoConfig):
        config = FilterLicenseAnnotationDemoConfig(super().normalize_config(config))

        env_mapping = {
            "cropped_topic_suffix": str,
            "font_scale": float,
            "font_thickness": int,
            "inset_size": str,    # To parse manually
            "inset_margin": str,  # To parse manually
            "debug": bool,
        }

        for key, expected_type in env_mapping.items():
            env_key = f"FILTER_{key.upper()}"
            env_val = os.getenv(env_key)
            if env_val is not None:
                if expected_type is bool:
                    setattr(config, key, env_val.strip().lower() == "true")
                elif expected_type is float:
                    setattr(config, key, float(env_val.strip()))
                elif expected_type is int:
                    setattr(config, key, int(env_val.strip()))
                else:
                    setattr(config, key, env_val.strip())

        # Parse inset_size if needed
        if isinstance(config.inset_size, str):
            try:
                width, height = map(int, config.inset_size.lower().split('x'))
                config.inset_size = (width, height)
            except Exception as e:
                raise ValueError(f"Invalid inset_size format '{config.inset_size}'. Expected 'WIDTHxHEIGHT'. Error: {e}")

        # Parse inset_margin if needed
        if isinstance(config.inset_margin, str):
            try:
                x_margin, y_margin = map(int, config.inset_margin.lower().split('x'))
                config.inset_margin = (x_margin, y_margin)
            except Exception as e:
                raise ValueError(f"Invalid inset_margin format '{config.inset_margin}'. Expected 'XMARGINxYMARGIN'. Error: {e}")

        return config

    def setup(self, config: FilterLicenseAnnotationDemoConfig):
        self.cropped_topic_suffix = config.cropped_topic_suffix
        self.font_scale = config.font_scale
        self.font_thickness = config.font_thickness
        self.inset_size = config.inset_size
        self.inset_margin = config.inset_margin
        self.debug = config.debug
        self.last_seen_license = None  # Track last detected license plate

        if self.debug:
            logger.setLevel(logging.DEBUG)

        logger.info(f"FilterLicenseAnnotationDemo setup complete with config: {config}")

    def shutdown(self):
        logger.info("FilterLicenseAnnotationDemo shutdown complete.")

    def process(self, frames: dict[str, Frame]):
        main_frame = frames.get("main")
        cropped_frame = frames.get(self.cropped_topic_suffix)

        if main_frame is None:
            logger.warning("Main frame missing — skipping processing.")
            return frames

        image = main_frame.rw_bgr.image
        meta = main_frame.data.get("meta", {})

        # 1. Overlay OCR texts
        texts = []
        if cropped_frame:
            texts = cropped_frame.data.get("meta", {}).get("ocr_texts", [])

        # License plate extraction with fallback
        license_plate_pattern = re.compile(r'^[A-Z]{3}[0-9]{4}$', re.IGNORECASE)

        filtered_texts = []
        for text in texts:
            text = text.strip().replace(' ', '').upper()
            if license_plate_pattern.match(text):
                filtered_texts.append(text)

        if filtered_texts:
            self.last_seen_license = filtered_texts[0]  # Use first match
            texts = [self.last_seen_license]
        elif self.last_seen_license:
            texts = [self.last_seen_license]  # fallback to last seen
        else:
            texts = []

        logger.debug(f"Texts: {texts}")
        if texts and cropped_frame:
            text = texts[0].strip()
            if text:
                x_margin, y_margin = self.inset_margin
                inset_width, inset_height = self.inset_size
                padding = 6

                # Estimate a font scale (text width = ~90% of inset width)
                desired_text_width = inset_width * 0.9
                test_font_scale = 1.0
                (test_width, _), _ = cv2.getTextSize(
                    text,
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=test_font_scale,
                    thickness=self.font_thickness
                )
                font_scale = test_font_scale * (desired_text_width / test_width)

                # Get text size with adjusted scale
                (text_width, text_height), baseline = cv2.getTextSize(
                    text,
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=font_scale,
                    thickness=self.font_thickness
                )

                x1 = x_margin
                y1 = y_margin + inset_height + padding
                x2 = x1 + text_width + 2 * padding
                y2 = y1 + text_height + 2 * padding

                if y2 <= image.shape[0] and x2 <= image.shape[1]:
                    cv2.rectangle(image, (x1, y1), (x2, y2), (50, 50, 50), thickness=-1)
                    cv2.putText(
                        image,
                        text,
                        (x1 + padding, y1 + text_height + padding // 2),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=font_scale,
                        color=(255, 255, 255),
                        thickness=self.font_thickness,
                        lineType=cv2.LINE_AA
                    )
                else:
                    logger.warning("OCR label doesn't fit below the inset image — skipping text drawing.")

        # 2. Overlay cropped image
        if cropped_frame:
            cropped = cropped_frame.rw_bgr.image
            try:
                resized = cv2.resize(cropped, self.inset_size)
                x_margin, y_margin = self.inset_margin
                h, w = resized.shape[:2]

                # Check if the cropped inset fits inside the main image
                if (y_margin + h <= image.shape[0]) and (x_margin + w <= image.shape[1]):
                    image[y_margin:y_margin+h, x_margin:x_margin+w] = resized
                else:
                    logger.warning("Inset image does not fit inside the main frame — skipping inset.")

            except Exception as e:
                logger.warning(f"Failed to overlay cropped image: {e}")

        frames["main"] = Frame(
            image,
            {**main_frame.data},
            format="BGR"
        )

        return frames

if __name__ == '__main__':
    FilterLicenseAnnotationDemo.run()
