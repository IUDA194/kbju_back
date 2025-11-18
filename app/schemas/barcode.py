from app.schemas.user import DailyStats, TelegramUser
from pydantic import BaseModel


class NutritionPer100g(BaseModel):
    kcal: float | None
    protein: float | None
    fat: float | None
    carbs: float | None


class NutritionPerServing(BaseModel):
    size: str | None
    kcal: float | None
    protein: float | None
    fat: float | None
    carbs: float | None


class NutritionResponse(BaseModel):
    barcode: str
    name: str
    per_100g: NutritionPer100g
    serving: NutritionPerServing


class TrackBarcodeRequest(BaseModel):
    telegram_user: TelegramUser
    grams: float | None = None
    servings: float | None = None


class TrackBarcodeResponse(BaseModel):
    barcode: str
    name: str
    amount_grams: float | None
    servings: float | None
    per_100g: NutritionPer100g
    serving: NutritionPerServing
    daily: DailyStats
