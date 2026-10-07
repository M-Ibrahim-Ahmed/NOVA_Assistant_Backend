from typing import Any

from pydantic import BaseModel, Field


class CapabilityRequest(BaseModel):
    request_id: str
    capability: str
    reason: str

    parameters: dict[str, Any] = Field(
        default_factory=dict
    )


class CapabilityResult(BaseModel):
    request_id: str
    capability: str
    data: dict[str, Any]