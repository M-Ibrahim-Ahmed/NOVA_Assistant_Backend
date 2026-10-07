from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

from app.models.capability import (
    CapabilityRequest,
    CapabilityResult,
)

from app.services.ai_service import (
    continue_after_capability,
    generate_response,
)

from app.services.capability_service import (
    capability_service,
)

from app.services.conversation_service import (
    conversation_service,
)

from app.services.profile_service import (
    profile_service,
)


router = APIRouter(
    prefix="/api"
)


# =========================================================
# CHAT REQUEST
# =========================================================

class ChatRequest(BaseModel):

    message: str

    user_id: str

    conversation_id: str | None = None


# =========================================================
# CHAT
# =========================================================

@router.post("/chat")
async def chat(
    request: ChatRequest,
):

    print("\n")
    print("========================================")
    print("CHAT REQUEST RECEIVED")
    print("========================================")
    print(
        "USER ID:",
        request.user_id,
    )
    print(
        "MESSAGE:",
        request.message,
    )
    print(
        "CONVERSATION ID:",
        request.conversation_id,
    )
    print("========================================")

    # -----------------------------------------------------
    # CONVERSATION
    # -----------------------------------------------------

    conversation_id = (
        request.conversation_id
    )

    if not conversation_id:

        conversation_id = str(
            uuid4()
        )

    history = (
        conversation_service.get_history(
            conversation_id
        )
    )

    # -----------------------------------------------------
    # PROFILE
    # -----------------------------------------------------

    profile = (
        profile_service.get_profile(
            request.user_id
        )
    )

    print("\n")
    print(
        "******** PROFILE DEBUG ********"
    )
    print(
        profile.model_dump()
    )
    print(
        "********************************"
    )

    # -----------------------------------------------------
    # AI
    # -----------------------------------------------------

    result = await generate_response(

        message=request.message,

        conversation_history=history,

        user_profile=profile.model_dump(),
    )

    # -----------------------------------------------------
    # CAPABILITY REQUEST
    # -----------------------------------------------------

    if isinstance(
        result,
        CapabilityRequest,
    ):

        print("\n")
        print(
            "******** CAPABILITY REQUEST ********"
        )
        print(
            "REQUEST ID:",
            result.request_id,
        )
        print(
            "CAPABILITY:",
            result.capability,
        )
        print(
            "REASON:",
            result.reason,
        )
        print(
            "PARAMETERS:",
            result.parameters,
        )
        print(
            "************************************"
        )

        # -------------------------------------------------
        # IMPORTANT
        #
        # Remember which conversation caused this
        # capability request.
        # -------------------------------------------------

        capability_service.attach_conversation(

            request_id=result.request_id,

            conversation_id=conversation_id,

            user_message=request.message,

            user_id=request.user_id,
        )

    return {

        "type":
            "capability_request",

        "conversation_id":
            conversation_id,

        "request_id":
            result.request_id,

        "capability":
            result.capability,

        "reason":
            result.reason,

        "parameters":
            result.parameters,
    }

    # -----------------------------------------------------
    # NORMAL RESPONSE
    # -----------------------------------------------------

    response_text = result

    # -----------------------------------------------------
    # SAVE CONVERSATION
    # -----------------------------------------------------

    conversation_service.add_message(

        session_id=conversation_id,

        role="user",

        content=request.message,
    )

    conversation_service.add_message(

        session_id=conversation_id,

        role="assistant",

        content=response_text,
    )

    print("\n")
    print(
        "******** CONVERSATION SAVED ********"
    )
    print(
        "CONVERSATION ID:",
        conversation_id,
    )
    print(
        "USER:",
        request.message,
    )
    print(
        "NOVA:",
        response_text,
    )
    print(
        "************************************"
    )

    return {

        "type":
            "response",

        "response":
            response_text,

        "conversation_id":
            conversation_id,
    }


# =========================================================
# CAPABILITY RESULT
# =========================================================

@router.post("/chat/capability-result")
async def capability_result(
    request: CapabilityResult,
):

    print("\n")
    print("========================================")
    print("CAPABILITY RESULT RECEIVED")
    print("========================================")
    print(
        "REQUEST ID:",
        request.request_id,
    )
    print(
        "CAPABILITY:",
        request.capability,
    )
    print(
        "DATA:",
        request.data,
    )
    print("========================================")

    # -----------------------------------------------------
    # GET PENDING REQUEST BEFORE CONTINUATION
    #
    # continue_after_capability removes the pending
    # request after completion, so we need the conversation
    # information first.
    # -----------------------------------------------------

    pending = (
        capability_service.get_request(
            request.request_id
        )
    )

    if pending is None:

        raise ValueError(
            "Capability request was not found."
        )

    conversation_id = (
        pending.conversation_id
    )

    user_message = (
        pending.user_message
    )

    # -----------------------------------------------------
    # CONTINUE AI
    # -----------------------------------------------------

    response = (
        await continue_after_capability(

            request_id=request.request_id,

            capability_data=request.data,
        )
    )

    # -----------------------------------------------------
    # SAVE COMPLETED CAPABILITY CONVERSATION
    # -----------------------------------------------------

    if (
        conversation_id
        and user_message
    ):

        conversation_service.add_message(

            session_id=conversation_id,

            role="user",

            content=user_message,
        )

        conversation_service.add_message(

            session_id=conversation_id,

            role="assistant",

            content=response,
        )

        print("\n")
        print(
            "***** CAPABILITY CONVERSATION SAVED *****"
        )
        print(
            "CONVERSATION ID:",
            conversation_id,
        )
        print(
            "USER:",
            user_message,
        )
        print(
            "NOVA:",
            response,
        )
        print(
            "*****************************************"
        )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {

        "type":
            "response",

        "response":
            response,

        "conversation_id":
            conversation_id,
    }