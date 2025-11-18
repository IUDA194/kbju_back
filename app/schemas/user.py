from datetime import date

from pydantic import BaseModel


class TelegramUser(BaseModel):
    id: int
    is_bot: bool | None = None
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    is_premium: bool | None = None


class UserProfile(BaseModel):
    id: int
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None

    class Config:
        from_attributes = True


class DailyStats(BaseModel):
    date: date
    kcal: float
    protein: float
    fat: float
    carbs: float

    class Config:
        from_attributes = True


class UserMeResponse(BaseModel):
    profile: UserProfile
    today: DailyStats | None
