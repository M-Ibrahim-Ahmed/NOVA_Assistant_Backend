from app.services.search_service import web_search


async def search_web(query: str) -> str:
    return await web_search(query)