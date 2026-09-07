import os

import httpx
from dotenv import load_dotenv


load_dotenv()


BRAVE_SEARCH_API_KEY = os.getenv(
    "BRAVE_SEARCH_API_KEY"
)

if not BRAVE_SEARCH_API_KEY:
    raise ValueError(
        "BRAVE_SEARCH_API_KEY is not configured."
    )


async def web_search(
    query: str,
    count: int = 5,
) -> str:

    print("🔎 BRAVE SEARCH:", query)
    
    url = (
        "https://api.search.brave.com"
        "/res/v1/web/search"
    )

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": BRAVE_SEARCH_API_KEY,
    }

    params = {
        "q": query,
        "count": count,
        "country": "ALL",
        "search_lang": "en",
        "safesearch": "moderate",
    }

    async with httpx.AsyncClient() as client:

        response = await client.get(
            url,
            headers=headers,
            params=params,
            timeout=10,
        )

        if response.status_code != 200:
            print("BRAVE STATUS:", response.status_code)
            print("BRAVE RESPONSE:", response.text)

        response.raise_for_status()

        data = response.json()

    results = (
        data.get("web", {})
        .get("results", [])
    )

    if not results:
        return "No useful search results were found."

    output = []

    for index, result in enumerate(
        results,
        start=1,
    ):

        title = result.get(
            "title",
            "Untitled",
        )

        description = result.get(
            "description",
            "",
        )

        result_url = result.get(
            "url",
            "",
        )

        output.append(
            f"{index}. {title}\n"
            f"Description: {description}\n"
            f"URL: {result_url}"
        )

    return "\n\n".join(output)