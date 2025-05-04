from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models import CardCategories
from app.database import get_db
from app.services.jwt import token_required

router = APIRouter(prefix="/api/card-categories", tags=["CardCategories"])

@router.post("/", response_model=dict)
def get_card_category_by_id(
    req: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(token_required),
):
    feature_input = req.json()

    category_id = int(feature_input['card_category_id'])

    card_category = db.query(CardCategories).filter_by(id=category_id).first()
    if not card_category:
        raise HTTPException(status_code=404, detail="Card Category not found")
    return card_category.to_dict()
