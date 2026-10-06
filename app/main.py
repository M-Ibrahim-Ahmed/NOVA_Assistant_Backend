from fastapi import FastAPI

from app.routes.health import router as health_router
from app.routes.chat import router as chat_router
from app.routes.profile import router as profile_router

app = FastAPI(
    title="NOVA Backend",
    description="Backend API for the NOVA AI Assistant",
    version="1.0.0",
)


app.include_router(health_router)
app.include_router(chat_router)
app.include_router(profile_router)


@app.get("/")
def root():
    return {
        "message": "NOVA backend is running"
    }