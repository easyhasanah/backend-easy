from fastapi import APIRouter, Depends, HTTPException, Request, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models import CardCategories
from app.database import get_db
from app.services.jwt import token_required

router = APIRouter(prefix="/api/card-categories", tags=["CardCategories"])

class CardCategoryResponse(BaseModel):
    type: str
    limit: int

@router.get("/", response_model=CardCategoryResponse)
async def get_card_category_by_id(
    limit_category: int = Query(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(token_required),
):
    card_category = db.query(CardCategories).filter_by(id=limit_category).first()
    if not card_category:
        raise HTTPException(status_code=404, detail="Card Category not found")

    return card_category