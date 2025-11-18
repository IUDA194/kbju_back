from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User

class DailyNutrition(Base):
    __tablename__ = "daily_nutrition"
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_daily_nutrition_user_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    date: Mapped[datetime] = mapped_column(Date, index=True)

    kcal_total: Mapped[float] = mapped_column(Float, default=0.0)
    protein_total: Mapped[float] = mapped_column(Float, default=0.0)
    fat_total: Mapped[float] = mapped_column(Float, default=0.0)
    carbs_total: Mapped[float] = mapped_column(Float, default=0.0)

    user: Mapped["User"] = relationship(
        back_populates="daily_nutrition",
    )
