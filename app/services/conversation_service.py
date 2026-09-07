from typing import Dict, List


class ConversationService:

    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages

        # Stores conversations separately by session ID.
        self._conversations: Dict[
            str,
            List[dict]
        ] = {}

    # =====================================================
    # GET CONVERSATION
    # =====================================================

    def get_history(
        self,
        session_id: str,
    ) -> List[dict]:

        return self._conversations.get(
            session_id,
            []
        )

    # =====================================================
    # ADD MESSAGE
    # =====================================================

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:

        if session_id not in self._conversations:
            self._conversations[session_id] = []

        self._conversations[session_id].append(
            {
                "role": role,
                "content": content,
            }
        )

        # Keep only the most recent messages.
        self._conversations[session_id] = (
            self._conversations[session_id][
                -self.max_messages:
            ]
        )

    # =====================================================
    # CLEAR CONVERSATION
    # =====================================================

    def clear(
        self,
        session_id: str,
    ) -> None:

        self._conversations.pop(
            session_id,
            None,
        )

    # =====================================================
    # REMOVE EMPTY CONVERSATIONS
    # =====================================================

    def exists(
        self,
        session_id: str,
    ) -> bool:

        return session_id in self._conversations


# =========================================================
# SINGLE SERVICE INSTANCE
# =========================================================

conversation_service = ConversationService(
    max_messages=10
)