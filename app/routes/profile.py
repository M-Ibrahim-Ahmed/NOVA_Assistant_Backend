from fastapi import APIRouter
from pydantic import BaseModel

from app.models.user_profile import UserProfile
from app.services.profile_service import profile_service


router = APIRouter(prefix="/api")


class ProfileRequest(BaseModel):
    user_id: str
    profile: UserProfile


@router.get("/profile/{user_id}")
def get_profile(user_id: str):

    profile = profile_service.get_profile(
        user_id
    )

    return {
        "user_id": user_id,
        "profile": profile.model_dump(),
    }


@router.put("/profile")
def update_profile(
    request: ProfileRequest,
):

    profile = profile_service.save_profile(
        user_id=request.user_id,
        profile=request.profile,
    )

    return {
        "user_id": request.user_id,
        "profile": profile.model_dump(),
    }