import json
from pathlib import Path

from app.models.user_profile import UserProfile


BASE_DIR = Path(__file__).resolve().parents[2]

USERS_DIR = BASE_DIR / "data" / "users"


class ProfileService:

    def __init__(self):
        USERS_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _get_profile_file(
        self,
        user_id: str,
    ) -> Path:

        return USERS_DIR / f"{user_id}.json"

    def get_profile(
        self,
        user_id: str,
    ) -> UserProfile:

        profile_file = self._get_profile_file(
            user_id
        )

        if not profile_file.exists():
            return UserProfile()

        try:
            with open(
                profile_file,
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            return UserProfile.model_validate(data)

        except (
            json.JSONDecodeError,
            ValueError,
        ):
            return UserProfile()

    def save_profile(
        self,
        user_id: str,
        profile: UserProfile,
    ) -> UserProfile:

        profile_file = self._get_profile_file(
            user_id
        )

        with open(
            profile_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                profile.model_dump(),
                file,
                indent=2,
                ensure_ascii=False,
            )

        return profile


profile_service = ProfileService()