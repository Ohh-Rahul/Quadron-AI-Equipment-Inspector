"""Validation helpers for uploaded inspection images."""

from io import BytesIO
from typing import Union

from PIL import Image, UnidentifiedImageError


MAX_IMAGE_SIZE_BYTES = 2 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg"}


def validate_image_file(
    image_data: Union[bytes, bytearray],
    content_type: str,
) -> tuple[bool, str]:
    """Validate type, size, and readability of an uploaded image."""
    if content_type not in ALLOWED_IMAGE_TYPES:
        return False, "Unsupported image type. Use PNG or JPEG."

    if len(image_data) > MAX_IMAGE_SIZE_BYTES:
        return False, "Image is larger than the 2 MB limit."

    try:
        with Image.open(BytesIO(image_data)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError):
        return False, "The image is invalid or unreadable."

    return True, "Image is valid."
