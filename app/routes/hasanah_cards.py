from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.models import HasanahCards
from app.database import get_db
from app.services.jwt import token_required
from datetime import datetime
import random

router = APIRouter(prefix="/api/card", tags=["HasanahCards"])

@router.get("/", response_model=dict)
def get_card(user_id: int = Depends(token_required), db: Session = Depends(get_db)):
    submission = db.query(HasanahCards).filter_by(user_id=user_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Card not found")
    return submission.to_dict()

@router.post("/", response_model=dict)
def add_card(
    request: Request,
    user_id: int = Depends(token_required),
    db: Session = Depends(get_db)
):
    feature_input = request.json()

    expired_date_data = datetime.utcnow().date().replace(year=datetime.utcnow().year + 5)
    card_no_data = ''.join([str(random.randint(0, 9)) for _ in range(16)])

    card = HasanahCards(
        card_no=card_no_data,
        expired_date=expired_date_data,
        user_id=user_id,
        pin=feature_input['pin'],
        card_category_id=int(feature_input['card_category'])
    )

    db.add(card)
    db.commit()
    db.refresh(card)

    return {"message": "Card inserted successfully"}