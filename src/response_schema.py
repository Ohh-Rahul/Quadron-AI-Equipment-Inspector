
"""Pydantic schema for a structured equipment inspection response."""

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field, field_validator


AssessmentStatus = Literal[
    "Good",
    "Needs repair",
    "Unsafe",
    "cannot_assess"
]


class InspectionResponse(BaseModel):
    """Structured result returned by the equipment inspection workflow."""

    assessment_status: AssessmentStatus
    category: str
    equipment_name: str
    verdict: AssessmentStatus

    checklist_results: List[Dict[str, Any]] = Field(
        default_factory=list
    )

    visible_issues: List[str] = Field(
        default_factory=list
    )

    confidence: float = Field(ge=0.0, le=1.0)
    reason: str

    @field_validator("visible_issues", mode="before")
    @classmethod
    def normalize_visible_issues(cls, value):
        """Convert AI-generated issue objects into readable strings."""

        if value is None:
            return []

        if not isinstance(value, list):
            raise ValueError("visible_issues must be a list.")

        normalized_issues = []

        for issue in value:
            if isinstance(issue, str):
                normalized_issues.append(issue)

            elif isinstance(issue, dict):
                description = (
                    issue.get("issue")
                    or issue.get("description")
                    or issue.get("name")
                )

                if description:
                    normalized_issues.append(str(description))
                else:
                    normalized_issues.append(str(issue))

            else:
                normalized_issues.append(str(issue))

        return normalized_issues
