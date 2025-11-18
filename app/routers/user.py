from fastapi import APIRouter

from app.views.user import get_me_view
from app.schemas.user import UserMeResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

router.add_api_route(
    "/me",
    get_me_view,
    methods=["GET"],
    response_model=UserMeResponse,
)
