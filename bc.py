import sys
import requests
from typing import Any, Dict


API_URL = "https://world.openfoodfacts.org/api/v0/product/{barcode}.json"


def fetch_product_data(barcode: str) -> Dict[str, Any]:
    """
    Получает сырые данные продукта по штрихкоду из OpenFoodFacts.
    """
    url = API_URL.format(barcode=barcode)
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != 1:
        raise ValueError(f"Продукт с штрихкодом {barcode} не найден в OpenFoodFacts")

    return data["product"]


def extract_bju(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Достаёт БЖУ и калорийность из ответа OpenFoodFacts.
    Значения — на 100 г (или 100 мл), если есть.
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

    return {
        "name": product.get("product_name") or product.get("generic_name") or "Без названия",
        "kcal_100g": get_float("energy-kcal_100g"),
        "protein_100g": get_float("proteins_100g"),
        "fat_100g": get_float("fat_100g"),
        "carbs_100g": get_float("carbohydrates_100g"),
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("Использование: python nutrition_from_barcode.py <BARCODE>")
        print("Пример:   python nutrition_from_barcode.py 5449000131805")
        sys.exit(1)

    barcode = sys.argv[1].strip()

    try:
        product = fetch_product_data(barcode)
        bju = extract_bju(product)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

    print(f"Продукт: {bju['name']}")
    print("На 100 г (или 100 мл):")
    print(f"  Калории: {bju['kcal_100g'] or 'нет данных'} ккал")
    print(f"  Белки:   {bju['protein_100g'] or 'нет данных'} г")
    print(f"  Жиры:    {bju['fat_100g'] or 'нет данных'} г")
    print(f"  Углеводы:{bju['carbs_100g'] or 'нет данных'} г")


if __name__ == "__main__":
    main()

