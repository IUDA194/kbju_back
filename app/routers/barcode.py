from fastapi import APIRouter

from app.views.barcode import get_bju_by_barcode, track_bju_by_barcode
from app.schemas.barcode import NutritionResponse, TrackBarcodeResponse

router = APIRouter(
    prefix="/barcode",
    tags=["barcode"],
)

router.add_api_route(
    "/{barcode}",
    get_bju_by_barcode,
    methods=["GET"],
    response_model=NutritionResponse,
)

router.add_api_route(
    "/{barcode}/track",
    track_bju_by_barcode,
    methods=["POST"],
    response_model=TrackBarcodeResponse,
)
