import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from app.tools.time_tool import get_current_time
from app.tools.weather_tool import get_weather
from app.tools.location_tool import find_location
from app.tools.search_tool import search_web


load_dotenv()


# =========================================================
# OPENAI CLIENT
# =========================================================

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY is not configured."
    )

client = OpenAI(api_key=api_key)


# =========================================================
# TIME TOOL
# =========================================================

time_tool = {
    "type": "function",
    "name": "get_current_time",
    "description": (
        "Get the current date and time in Pakistan. "
        "Use this when the user asks about the current date, "
        "current time, today, tomorrow, yesterday, "
        "or the day of the week."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
}


# =========================================================
# WEATHER TOOL
# =========================================================

weather_tool = {
    "type": "function",
    "name": "get_weather",
    "description": (
        "Get current weather and up to 7 days of weather forecast "
        "using geographic latitude and longitude coordinates. "
        "This includes temperature, humidity, wind, weather "
        "conditions, precipitation probability, and precipitation "
        "amounts."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {
                "type": "number",
                "description": "Latitude of the location.",
            },
            "longitude": {
                "type": "number",
                "description": "Longitude of the location.",
            },
        },
        "required": [
            "latitude",
            "longitude",
        ],
        "additionalProperties": False,
    },
}


# =========================================================
# LOCATION / GEOCODING TOOL
# =========================================================

location_tool = {
    "type": "function",
    "name": "find_location",
    "description": (
        "Find geographic coordinates for a named location "
        "such as a city, country, region, or place."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": (
                    "The explicitly named city, country, "
                    "region, or place."
                ),
            },
        },
        "required": [
            "location",
        ],
        "additionalProperties": False,
    },
}


# =========================================================
# WEB SEARCH TOOL
# =========================================================

search_tool = {
    "type": "function",
    "name": "search_web",
    "description": (
        "Search the internet for current, recent, "
        "or specific information. "
        "Use this when the user asks for news, "
        "latest information, recent events, current "
        "information, current prices, or explicitly "
        "asks to search the web."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "The search query to send to the web."
                ),
            },
        },
        "required": [
            "query",
        ],
        "additionalProperties": False,
    },
}


# =========================================================
# AVAILABLE TOOLS
# =========================================================

tools = [
    time_tool,
    weather_tool,
    location_tool,
    search_tool,
]


# =========================================================
# GENERATE RESPONSE
# =========================================================

async def generate_response(
    message: str,
    latitude: float | None = None,
    longitude: float | None = None,
    conversation_history: list[dict] | None = None,
    user_memories: list[str] | None = None,
) -> str:

    # -----------------------------------------------------
    # INITIALIZE MEMORY / HISTORY
    # -----------------------------------------------------

    if conversation_history is None:
        conversation_history = []

    if user_memories is None:
        user_memories = []

    # Keep short-term conversation bounded.
    # This prevents the context from growing indefinitely.
    conversation_history = conversation_history[-10:]

    # -----------------------------------------------------
    # DEVICE LOCATION
    # -----------------------------------------------------

    has_device_location = (
        latitude is not None
        and longitude is not None
    )

    if has_device_location:

        location_context = (
            "\n\nDEVICE LOCATION AVAILABLE:\n"
            f"Latitude: {latitude}\n"
            f"Longitude: {longitude}\n\n"
            "These coordinates represent the user's current "
            "device location."
        )

    else:

        location_context = (
            "\n\nDEVICE LOCATION:\n"
            "No device location is currently available."
        )

    # -----------------------------------------------------
    # AI INSTRUCTIONS
    # -----------------------------------------------------

    instructions = (
        "You are NOVA, a mobile voice assistant that gives "
        "short, natural and conversational answers.\n\n"

        "RESPONSE STYLE:\n"
        "Keep responses brief and easy to speak aloud.\n"
        "Usually answer in 1-3 sentences.\n"
        "Prefer one short sentence when that fully answers "
        "the question.\n"
        "Do not give long explanations unless the user "
        "explicitly asks for a detailed explanation.\n"
        "Do not use unnecessary introductions, conclusions, "
        "or filler.\n"
        "Do not repeat the user's question.\n"
        "Avoid long lists unless the user specifically asks "
        "for a list.\n"
        "For simple questions, give a simple answer.\n"
        "Use natural spoken language rather than formal writing.\n\n"

        "GENERAL RULE:\n"
        "Use tools whenever current or real-world information "
        "is required.\n\n"

        "TIME RULE:\n"
        "For current date, current time, today, tomorrow, "
        "yesterday, or day-of-week questions, use "
        "get_current_time.\n"
        "Never guess the current time or date.\n\n"

        "WEATHER LOCATION RULES:\n\n"

        "RULE 1 — EXPLICIT LOCATION:\n"
        "If the user explicitly names a location, such as "
        "Islamabad, Lahore, Karachi, Dubai, London, Pakistan, "
        "Australia, etc., use that location.\n"
        "Do NOT use the device location in this case.\n"
        "First call find_location with the named location.\n"
        "Then use the returned latitude and longitude with "
        "get_weather.\n\n"

        "RULE 2 — NO EXPLICIT LOCATION:\n"
        "If the user asks about weather without naming a "
        "location, for example:\n"
        "'What's the weather?'\n"
        "'What's the weather here?'\n"
        "'How's the weather?'\n"
        "'Is it hot outside?'\n"
        "and device coordinates are available, immediately "
        "use the device latitude and longitude with "
        "get_weather.\n"
        "Do NOT call find_location.\n"
        "Do NOT ask the user for a city.\n\n"

        "RULE 3 — NO LOCATION AVAILABLE:\n"
        "If the user asks about weather without naming a "
        "location and device coordinates are NOT available, "
        "ask the user which location they want.\n\n"

        "LOCATION PRIORITY:\n"
        "Explicitly named location > device location.\n\n"

        "After receiving weather information, answer naturally "
        "and briefly. Give only the most useful weather details.\n\n"

        "WEB SEARCH RULES:\n"
        "Use search_web when the user asks for current, "
        "recent, or time-sensitive information.\n"
        "Use it for current news, recent events, latest "
        "technology releases, current cybersecurity threats, "
        "current sports results, current prices, or when the "
        "user explicitly asks you to search the web.\n\n"

        "Do not use search_web for simple general knowledge "
        "questions that do not require current information.\n\n"

        "When search results are returned, summarize only "
        "the most important information.\n"
        "Normally give the answer in 1-3 sentences.\n"
        "Do not read out URLs unless the user asks for them.\n"
        "Do not mention the search tool, Brave, APIs, or "
        "internal implementation details."

        + location_context
    )

    # -----------------------------------------------------
    # BUILD CONVERSATION CONTEXT
    # -----------------------------------------------------

    conversation_context = ""

    if conversation_history:

        conversation_context = (
            "\n\nRECENT CONVERSATION:\n"
        )

        for item in conversation_history:

            role = item["role"]
            content = item["content"]

            if role == "user":

                conversation_context += (
                    f"User: {content}\n"
                )

            elif role == "assistant":

                conversation_context += (
                    f"NOVA: {content}\n"
                )

    # -----------------------------------------------------
    # BUILD LONG-TERM MEMORY CONTEXT
    # -----------------------------------------------------

    memory_context = ""

    if user_memories:

        memory_context = (
            "\n\nLONG-TERM USER MEMORY:\n"
        )

        for memory in user_memories:

            memory_context += (
                f"- {memory}\n"
            )

        memory_context += (
            "\nUse these memories only when they are "
            "relevant to the user's current request. "
            "Do not mention the memory system. "
            "Do not unnecessarily reveal or repeat "
            "stored personal information.\n"
        )

    # -----------------------------------------------------
    # INITIAL REQUEST
    # -----------------------------------------------------

    response = client.responses.create(
        model="gpt-5.6-luna",

        instructions=(
            instructions
            + conversation_context
            + memory_context
        ),

        input=message,

        tools=tools,
    )

    # -----------------------------------------------------
    # TOOL LOOP
    # -----------------------------------------------------

    while True:

        tool_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        # -------------------------------------------------
        # NO TOOL CALLS
        # -------------------------------------------------

        if not tool_calls:
            return response.output_text

        tool_outputs = []

        # -------------------------------------------------
        # PROCESS TOOL CALLS
        # -------------------------------------------------

        for tool_call in tool_calls:

            # =============================================
            # TIME
            # =============================================

            if tool_call.name == "get_current_time":

                result = get_current_time()

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": result,
                    }
                )

            # =============================================
            # FIND LOCATION
            # =============================================

            elif tool_call.name == "find_location":

                arguments = json.loads(
                    tool_call.arguments
                )

                location = arguments["location"]

                try:

                    result = await find_location(
                        location
                    )

                    tool_outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": tool_call.call_id,
                            "output": json.dumps(result),
                        }
                    )

                except Exception as e:

                    tool_outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": tool_call.call_id,
                            "output": json.dumps(
                                {
                                    "error": str(e)
                                }
                            ),
                        }
                    )

            # =============================================
            # WEATHER
            # =============================================

            elif tool_call.name == "get_weather":

                arguments = json.loads(
                    tool_call.arguments
                )

                weather_latitude = arguments["latitude"]
                weather_longitude = arguments["longitude"]

                try:

                    result = await get_weather(
                        latitude=weather_latitude,
                        longitude=weather_longitude,
                    )

                    tool_outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": tool_call.call_id,
                            "output": result,
                        }
                    )

                except Exception as e:

                    tool_outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": tool_call.call_id,
                            "output": json.dumps(
                                {
                                    "error": str(e)
                                }
                            ),
                        }
                    )

            # =============================================
            # WEB SEARCH
            # =============================================

            elif tool_call.name == "search_web":

                arguments = json.loads(
                    tool_call.arguments
                )

                query = arguments["query"]

                try:

                    result = await search_web(
                        query
                    )

                    tool_outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": tool_call.call_id,
                            "output": result,
                        }
                    )

                except Exception as e:

                    tool_outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": tool_call.call_id,
                            "output": json.dumps(
                                {
                                    "error": str(e)
                                }
                            ),
                        }
                    )

        # -------------------------------------------------
        # SEND TOOL RESULTS BACK TO AI
        # -------------------------------------------------

        response = client.responses.create(
            model="gpt-5.6-luna",

            instructions=(
                "You are NOVA, a mobile voice assistant.\n\n"

                "Use the returned tool information to answer "
                "the user's original question naturally.\n\n"

                "You may also use the recent conversation and "
                "long-term user memory provided in the original "
                "request when relevant.\n\n"

                "RESPONSE LENGTH:\n"
                "Keep the answer very short because NOVA "
                "speaks the response aloud.\n"
                "Normally use 1-2 sentences.\n"
                "For simple questions, use one sentence.\n"
                "Only provide a detailed answer when the user "
                "explicitly asks for more detail.\n\n"

                "If find_location returned coordinates and "
                "weather information has not yet been retrieved, "
                "call get_weather using those coordinates.\n\n"

                "If get_weather returned weather information, "
                "answer the user directly using only the most "
                "relevant details.\n\n"

                "If search_web returned search results, use "
                "those results to answer the user's question. "
                "Prioritize relevant and recent information. "
                "Summarize instead of listing every result.\n"
                "Do not read URLs unless explicitly asked.\n\n"

                "If the weather request used device coordinates, "
                "do not mention the coordinates unless explicitly "
                "asked.\n\n"

                "Never mention internal tools, APIs, Brave, "
                "function calls, or implementation details.\n\n"

                "Keep the response natural, concise, and "
                "conversational."
            ),

            previous_response_id=response.id,

            input=tool_outputs,

            tools=tools,
        )

