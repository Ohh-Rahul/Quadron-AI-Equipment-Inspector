"""Basic image validation tests."""

from io import BytesIO

from PIL import Image

from src.image_validator import MAX_IMAGE_SIZE_BYTES, validate_image_file


def _small_png() -> bytes:
    image = Image.new("RGB", (10, 10), color="white")
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def test_valid_png_is_accepted() -> None:
    valid, message = validate_image_file(_small_png(), "image/png")

    assert valid is True
    assert message == "Image is valid."


def test_wrong_type_is_rejected() -> None:
    valid, _ = validate_image_file(_small_png(), "application/pdf")

    assert valid is False


def test_oversized_image_is_rejected() -> None:
    oversized = b"0" * (MAX_IMAGE_SIZE_BYTES + 1)

    valid, _ = validate_image_file(oversized, "image/png")

    assert valid is False
