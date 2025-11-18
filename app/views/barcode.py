import httpx
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.service.barcode import (
        fetch_product_data, extract_bju, ProductNotFoundError
)
from app.service.user import (
        get_or_create_user_from_telegram, add_to_daily_nutrition
)
from app.schemas.barcode import (
    NutritionResponse,
    TrackBarcodeRequest,
    TrackBarcodeResponse,
    NutritionPer100g,
    NutritionPerServing,
)
from app.schemas.user import DailyStats


async def get_bju_by_barcode(barcode: str) -> NutritionResponse:
    """
    Простой просмотр продукта по штрихкоду — без пользователя.
    """
    try:
        product = await fetch_product_data(barcode)
        data = extract_bju(product)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Ошибка внешнего сервиса OpenFoodFacts",
        )

    return NutritionResponse(
        barcode=barcode,
        name=data["name"],
        per_100g=NutritionPer100g(**data["per_100g"]),
        serving=NutritionPerServing(**data["serving"]),
    )


async def track_bju_by_barcode(
    barcode: str,
    payload: TrackBarcodeRequest,
    db: Session = Depends(get_db),
) -> TrackBarcodeResponse:
    """
    Берём телеграм-пользователя, делаем get_or_create,
    считаем БЖУ/ккал за эту еду, обновляем дневную статистику.
    """
    if not payload.grams and not payload.servings:
        raise HTTPException(
            status_code=400,
            detail="Нужно указать либо grams, либо servings",
        )

    try:
        product = await fetch_product_data(barcode)
        data = extract_bju(product)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Ошибка внешнего сервиса OpenFoodFacts",
        )

    user = get_or_create_user_from_telegram(db, payload.telegram_user)

    per_100g = data["per_100g"]
    per_serv = data["serving"]

    kcal_add = protein_add = fat_add = carbs_add = 0.0

    if payload.grams and per_100g["kcal"] is not None:
        factor = payload.grams / 100.0
        kcal_add += (per_100g["kcal"] or 0.0) * factor
        protein_add += (per_100g["protein"] or 0.0) * factor
        fat_add += (per_100g["fat"] or 0.0) * factor
        carbs_add += (per_100g["carbs"] or 0.0) * factor
    elif payload.servings and per_serv["kcal"] is not None:
        factor = payload.servings
        kcal_add += (per_serv["kcal"] or 0.0) * factor
        protein_add += (per_serv["protein"] or 0.0) * factor
        fat_add += (per_serv["fat"] or 0.0) * factor
        carbs_add += (per_serv["carbs"] or 0.0) * factor
    else:
        pass

    daily_record = add_to_daily_nutrition(
        db,
        user=user,
        kcal=kcal_add,
        protein=protein_add,
        fat=fat_add,
        carbs=carbs_add,
    )

    daily_stats = DailyStats(
        date=daily_record.date,
        kcal=daily_record.kcal_total,
        protein=daily_record.protein_total,
        fat=daily_record.fat_total,
        carbs=daily_record.carbs_total,
    )

    return TrackBarcodeResponse(
        barcode=barcode,
        name=data["name"],
        amount_grams=payload.grams,
        servings=payload.servings,
        per_100g=NutritionPer100g(**per_100g),
        serving=NutritionPerServing(**per_serv),
        daily=daily_stats,
    )
