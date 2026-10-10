"""FastAPI application entrypoint: mounts routers, CORS, health check."""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, auth, cases, chat, documents, search, sources
from app.config import settings

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.APP_NAME,
    description="Educational Egyptian legal Q&A backend (source-grounded, never fabricated citations).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(cases.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(sources.router)
app.include_router(admin.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": settings.APP_NAME, "env": settings.ENV}


@app.get("/", tags=["health"])
def root():
    return {"message": f"{settings.APP_NAME} backend is running.", "docs": "/docs"}
