from datetime import date

from sqlalchemy.orm import Session

from app.models import User, DailyNutrition
from app.schemas.user import UserProfile, DailyStats, UserMeResponse
from app.schemas.user import TelegramUser


def get_or_create_user_from_telegram(db: Session, tg_user: TelegramUser) -> User:
    user = db.query(User).filter_by(telegram_id=tg_user.id).first()

    if user:
        # Обновляем базовые поля профиля
        user.username = tg_user.username
        user.first_name = tg_user.first_name
        user.last_name = tg_user.last_name
        user.language_code = tg_user.language_code
        user.is_premium = bool(tg_user.is_premium or False)
    else:
        user = User(
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
            language_code=tg_user.language_code,
            is_premium=bool(tg_user.is_premium or False),
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    return user


def add_to_daily_nutrition(
    db: Session,
    user: User,
    kcal: float,
    protein: float,
    fat: float,
    carbs: float,
) -> DailyNutrition:
    today = date.today()
    record = (
        db.query(DailyNutrition)
        .filter_by(user_id=user.id, date=today)
        .first()
    )

    if not record:
        record = DailyNutrition(
            user_id=user.id,
            date=today,
            kcal_total=0.0,
            protein_total=0.0,
            fat_total=0.0,
            carbs_total=0.0,
        )
        db.add(record)

    record.kcal_total += kcal
    record.protein_total += protein
    record.fat_total += fat
    record.carbs_total += carbs

    db.commit()
    db.refresh(record)
    return record


def get_user_by_telegram_id(db: Session, telegram_id: int) -> User | None:
    return db.query(User).filter_by(telegram_id=telegram_id).first()


def get_today_stats(db: Session, user_id: int) -> DailyNutrition | None:
    return (
        db.query(DailyNutrition)
        .filter_by(user_id=user_id, date=date.today())
        .first()
    )


def get_me(db: Session, telegram_id: int) -> UserMeResponse | None:
    user = get_user_by_telegram_id(db, telegram_id)
    if not user:
        return None

    today_stats = get_today_stats(db, user.id)

    if today_stats:
        daily = DailyStats(
            date=today_stats.date,
            kcal=today_stats.kcal_total,
            protein=today_stats.protein_total,
            fat=today_stats.fat_total,
            carbs=today_stats.carbs_total,
        )
    else:
        daily = None

    return UserMeResponse(
        profile=UserProfile.model_validate(user),
        today=daily,
    )
