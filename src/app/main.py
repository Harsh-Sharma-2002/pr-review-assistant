from fastapi import FastAPI
from src.app.routes.webhook import router as webhook_router


app = FastAPI()

app.include_router(webhook_router, prefix="/webhook")

