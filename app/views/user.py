from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserMeResponse
from app.service.user import get_me


async def get_me_view(
    telegram_id: int,
    db: Session = Depends(get_db)
) -> UserMeResponse:
    """
    Возвращает профиль и дневную статистику по telegram_id.
    Ошибки:
        400 — если передан некорректный telegram_id
        404 — пользователь не найден
    """
    if telegram_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="telegram_id должен быть положительным числом"
        )

    response = get_me(db, telegram_id)

    if not response:
        raise HTTPException(
            status_code=404,
            detail=f"Пользователь с telegram_id={telegram_id} не найден"
        )

    return response
