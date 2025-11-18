from typing import Any

import httpx

API_URL = "https://world.openfoodfacts.org/api/v0/product/{barcode}.json"


class ProductNotFoundError(Exception):
    """Продукт с таким штрихкодом не найден."""


async def fetch_product_data(barcode: str) -> dict[str, Any]:
    """
    Получает сырые данные продукта по штрихкоду из OpenFoodFacts.
    """
    url = API_URL.format(barcode=barcode)

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url)
    resp.raise_for_status()

    data = resp.json()
    if data.get("status") != 1:
        raise ProductNotFoundError(f"Продукт с штрихкодом {barcode} не найден")

    return data["product"]


def extract_bju(product: dict[str, Any]) -> dict[str, Any]:
    """
    Подготавливает данные БЖУ в формате, подходящем под NutritionResponse.
    """
    nutriments = product.get("nutriments", {})

    def get_float(key: str) -> float | None:
        value = nutriments.get(key)
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    name = (
        product.get("product_name")
        or product.get("generic_name")
        or product.get("brands")
        or "Без названия"
    )

    serving_size = product.get("serving_size")

    return {
        "name": name,
        "per_100g": {
            "kcal": get_float("energy-kcal_100g"),
            "protein": get_float("proteins_100g"),
            "fat": get_float("fat_100g"),
            "carbs": get_float("carbohydrates_100g"),
        },
        "serving": {
            "size": serving_size,
            "kcal": get_float("energy-kcal_serving"),
            "protein": get_float("proteins_serving"),
            "fat": get_float("fat_serving"),
            "carbs": get_float("carbohydrates_serving"),
        },
    }
