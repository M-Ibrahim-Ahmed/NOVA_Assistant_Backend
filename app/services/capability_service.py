from typing import Any


class PendingCapability:
    def __init__(
        self,
        request_id: str,
        capability: str,
        response_id: str,
        call_id: str,
    ):
        self.request_id = request_id
        self.capability = capability
        self.response_id = response_id
        self.call_id = call_id


class CapabilityService:

    def __init__(self):
        self._pending: dict[
            str,
            PendingCapability,
        ] = {}

    def create_request(
        self,
        request_id: str,
        capability: str,
        response_id: str,
        call_id: str,
    ) -> PendingCapability:

        pending = PendingCapability(
            request_id=request_id,
            capability=capability,
            response_id=response_id,
            call_id=call_id,
        )

        self._pending[request_id] = pending

        return pending

    def get_request(
        self,
        request_id: str,
    ) -> PendingCapability | None:

        return self._pending.get(request_id)

    def remove_request(
        self,
        request_id: str,
    ) -> None:

        self._pending.pop(
            request_id,
            None,
        )


capability_service = CapabilityService()