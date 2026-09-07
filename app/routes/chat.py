from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_service import generate_response
from app.services.conversation_service import conversation_service


router = APIRouter(prefix="/api")


# =========================================================
# REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):
    message: str
    user_id: str
    latitude: float | None = None
    longitude: float | None = None

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
    # GET PREVIOUS CONVERSATION
    # -----------------------------------------------------

    history = conversation_service.get_history(
        conversation_id
    )

    # -----------------------------------------------------
    # GENERATE NOVA RESPONSE
    # -----------------------------------------------------

    response = await generate_response(
        message=request.message,
        latitude=request.latitude,
        longitude=request.longitude,
        conversation_history=history,
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