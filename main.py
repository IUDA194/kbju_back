from fastapi import FastAPI

from app.routers.barcode import router as barcode_router
from app.routers.user import router as user_router

app = FastAPI(
    title="KBJU Bot API",
    version="0.0.3",
)

app.include_router(barcode_router)
app.include_router(user_router)
