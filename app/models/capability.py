from typing import Any

from pydantic import BaseModel


class CapabilityRequest(BaseModel):
    request_id: str
    capability: str
    reason: str


class CapabilityResult(BaseModel):
    request_id: str
    capability: str
    data: dict[str, Any]