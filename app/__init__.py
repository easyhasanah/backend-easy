from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import Config
from app.models import Base, engine
from app.routes.users import router as users_router
from app.routes.submissions import router as submissions_router
from app.routes.hasanah_cards import router as hasanah_cards_router
from app.routes.card_categories import router as card_categories_router

def create_app() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    Base.metadata.create_all(bind=engine)

    app.include_router(users_router)
    app.include_router(submissions_router)
    app.include_router(hasanah_cards_router)
    app.include_router(card_categories_router)

    return app

app = create_app()
