"""Basic response schema validation tests."""

import pytest
from pydantic import ValidationError

from src.response_schema import InspectionResponse


def test_valid_response_is_accepted() -> None:
    response = InspectionResponse(
        assessment_status="Good",
        category="IT equipment",
        equipment_name="Desktop computer",
        verdict="Good",
        confidence=0.95,
        reason="No visible defects were identified.",
    )

    assert response.verdict == "Good"


def test_cannot_assess_is_supported() -> None:
    response = InspectionResponse(
        assessment_status="cannot_assess",
        category="Unknown",
        equipment_name="Unknown",
        verdict="cannot_assess",
        confidence=0.1,
        reason="The image is too blurry.",
    )

    assert response.assessment_status == "cannot_assess"


def test_invalid_status_is_rejected() -> None:
    with pytest.raises(ValidationError):
        InspectionResponse(
            assessment_status="Unknown status",
            category="IT equipment",
            equipment_name="Projector",
            verdict="Good",
            confidence=0.9,
            reason="Invalid status should fail validation.",
        )
