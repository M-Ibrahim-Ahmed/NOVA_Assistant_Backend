from pydantic import BaseModel


class HomeLocation(BaseModel):
    city: str | None = None
    country: str | None = None
    address: str | None = None


class UserPreferences(BaseModel):
    favorite_sport: str | None = None
    favorite_programming_language: str | None = None


class UserProfile(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None

    home_location: HomeLocation = HomeLocation()

    occupation: str | None = None

    preferences: UserPreferences = UserPreferences()