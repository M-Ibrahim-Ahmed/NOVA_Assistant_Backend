from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_service import generate_response
from app.services.conversation_service import conversation_service
from app.services.memory_extractor import memory_extractor
from app.services.memory_service import memory_service
from app.services.memory_retriever import memory_retriever


router = APIRouter(prefix="/api")


# =========================================================
# REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):

    message: str

    # Long-term user identity
    user_id: str

    # Device location
    latitude: float | None = None
    longitude: float | None = None

    # Short-term conversation identity
    conversation_id: str | None = None


# =========================================================
# CHAT ENDPOINT
# =========================================================

@router.post("/chat")
async def chat(request: ChatRequest):

    # -----------------------------------------------------
    # CREATE CONVERSATION ID IF NEEDED
    # -----------------------------------------------------

    conversation_id = request.conversation_id

    if not conversation_id:
        conversation_id = str(uuid4())

    # -----------------------------------------------------
    # GET SHORT-TERM CONVERSATION HISTORY
    # -----------------------------------------------------

    history = conversation_service.get_history(
        conversation_id
    )

    # -----------------------------------------------------
    # GET EXISTING LONG-TERM MEMORIES
    # -----------------------------------------------------

    memories = memory_service.get_memories(
        request.user_id
    )

    # -----------------------------------------------------
    # EXTRACT NEW MEMORIES FROM USER MESSAGE
    # -----------------------------------------------------

    new_memories = memory_extractor.extract(
        request.message
    )

    # -----------------------------------------------------
    # SAVE NEW MEMORIES
    # -----------------------------------------------------

    for memory in new_memories:

        memory_service.add_memory(
            user_id=request.user_id,
            memory=memory,
        )

    # -----------------------------------------------------
    # REFRESH MEMORIES
    #
    # This allows NOVA to use a newly learned memory
    # during the same request.
    # -----------------------------------------------------

    if new_memories:

        memories = memory_service.get_memories(
            request.user_id
        )

    # -----------------------------------------------------
    # RETRIEVE ONLY RELEVANT LONG-TERM MEMORIES
    #
    # Instead of sending every stored memory to the AI,
    # the local retriever selects only memories relevant
    # to the current user message.
    # -----------------------------------------------------

    relevant_memories = memory_retriever.retrieve(
        message=request.message,
        memories=memories,
        max_results=5,
    )

    # -----------------------------------------------------
    # GENERATE NOVA RESPONSE
    # -----------------------------------------------------

    response = await generate_response(
        message=request.message,
        latitude=request.latitude,
        longitude=request.longitude,
        conversation_history=history,
        user_memories=relevant_memories,
    )

    # -----------------------------------------------------
    # STORE USER MESSAGE
    # -----------------------------------------------------

    conversation_service.add_message(
        session_id=conversation_id,
        role="user",
        content=request.message,
    )

    # -----------------------------------------------------
    # STORE NOVA RESPONSE
    # -----------------------------------------------------

    conversation_service.add_message(
        session_id=conversation_id,
        role="assistant",
        content=response,
    )

    # -----------------------------------------------------
    # RETURN RESPONSE
    # -----------------------------------------------------

    return {
        "response": response,
        "conversation_id": conversation_id,
    }
