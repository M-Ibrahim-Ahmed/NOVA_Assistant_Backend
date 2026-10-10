
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

from app.tools.weather_tool import (
    clear_weather_result,
    get_last_weather_result,
)

from app.tools.time_tool import (
    clear_time_result,
    get_last_time_result,
)


router = APIRouter(
    prefix="/api"
)


# =========================================================
# CHAT REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):
    message: str
    user_id: str
    conversation_id: str | None = None


# =========================================================
# CHAT ENDPOINT
# =========================================================

@router.post("/chat")
async def chat(
    request: ChatRequest,
):

    # Clear previous card information for this request.
    clear_weather_result()
    clear_time_result()

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

    conversation_id = request.conversation_id

    if not conversation_id:
        conversation_id = str(
            uuid4()
        )

    history = conversation_service.get_history(
        conversation_id
    )

    # -----------------------------------------------------
    # USER PROFILE
    # -----------------------------------------------------

    profile = profile_service.get_profile(
        request.user_id
    )

    profile_data = profile.model_dump()

    print("\n")
    print("******** PROFILE DEBUG ********")
    print(profile_data)
    print("********************************")

    # -----------------------------------------------------
    # GENERATE AI RESPONSE
    # -----------------------------------------------------

    result = await generate_response(
        message=request.message,
        conversation_history=history,
        user_profile=profile_data,
    )

    # -----------------------------------------------------
    # DEVICE CAPABILITY REQUEST
    # -----------------------------------------------------

    if isinstance(
        result,
        CapabilityRequest,
    ):

        print("\n")
        print("******** CAPABILITY REQUEST ********")
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
        print("************************************")

        # Remember which conversation caused
        # this device capability request.

        capability_service.attach_conversation(
            request_id=result.request_id,
            conversation_id=conversation_id,
            user_message=request.message,
            user_id=request.user_id,
        )

        return {
            "type": "capability_request",
            "conversation_id": conversation_id,
            "request_id": result.request_id,
            "capability": result.capability,
            "reason": result.reason,
            "parameters": result.parameters,
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

    # -----------------------------------------------------
    # STRUCTURED CARD INFORMATION
    # -----------------------------------------------------

    weather_data = get_last_weather_result()
    time_data = get_last_time_result()

    print("\n")
    print("******** CONVERSATION SAVED ********")
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
        "WEATHER CARD:",
        weather_data is not None,
    )
    print(
        "TIME CARD AVAILABLE:",
        time_data is not None,
    )
    print("************************************")

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {
        "type": "response",
        "response": response_text,
        "conversation_id": conversation_id,
        "weather": weather_data,
        "time": time_data,
    }


# =========================================================
# DEVICE CAPABILITY RESULT
# =========================================================

@router.post("/chat/capability-result")
async def capability_result(
    request: CapabilityResult,
):

    # Each capability continuation is a separate
    # HTTP request, so reset its card information.

    clear_weather_result()
    clear_time_result()

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
    # GET PENDING CAPABILITY
    # -----------------------------------------------------

    # Read the conversation information before calling
    # continue_after_capability(), because that function
    # removes the pending capability request.

    pending = capability_service.get_request(
        request.request_id
    )

    if pending is None:
        raise ValueError(
            "Capability request was not found."
        )

    conversation_id = pending.conversation_id
    user_message = pending.user_message

    # -----------------------------------------------------
    # CONTINUE AI RESPONSE
    # -----------------------------------------------------

    response = await continue_after_capability(
        request_id=request.request_id,
        capability_data=request.data,
    )

    # -----------------------------------------------------
    # SAVE COMPLETED CONVERSATION
    # -----------------------------------------------------

    if conversation_id and user_message:

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
        print("*****************************************")

    # -----------------------------------------------------
    # STRUCTURED CARD INFORMATION
    # -----------------------------------------------------

    weather_data = get_last_weather_result()
    time_data = get_last_time_result()

    print(
        "WEATHER CARD AVAILABLE:",
        weather_data is not None,
    )

    print(
        "TIME CARD AVAILABLE:",
        time_data is not None,
    )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {
        "type": "response",
        "response": response,
        "conversation_id": conversation_id,
        "weather": weather_data,
        "time": time_data,
    }
