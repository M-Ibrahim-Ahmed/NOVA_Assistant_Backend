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

        # Conversation context is attached by the chat route
        # after the AI requests a device capability.
        self.conversation_id: str | None = None
        self.user_message: str | None = None
        self.user_id: str | None = None


class CapabilityService:

    def __init__(self):
        self._pending: dict[
            str,
            PendingCapability,
        ] = {}

    # =====================================================
    # CREATE REQUEST
    # =====================================================

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

    # =====================================================
    # ATTACH CONVERSATION CONTEXT
    # =====================================================

    def attach_conversation(
        self,
        request_id: str,
        conversation_id: str,
        user_message: str,
        user_id: str,
    ) -> None:

        pending = self._pending.get(
            request_id
        )

        if pending is None:
            raise ValueError(
                "Capability request was not found."
            )

        pending.conversation_id = (
            conversation_id
        )

        pending.user_message = (
            user_message
        )

        pending.user_id = (
            user_id
        )

    # =====================================================
    # GET REQUEST
    # =====================================================

    def get_request(
        self,
        request_id: str,
    ) -> PendingCapability | None:

        return self._pending.get(
            request_id
        )

    # =====================================================
    # REMOVE REQUEST
    # =====================================================

    def remove_request(
        self,
        request_id: str,
    ) -> None:

        self._pending.pop(
            request_id,
            None,
        )


capability_service = CapabilityService()