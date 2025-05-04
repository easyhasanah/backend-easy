from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.models import HasanahCards
from app.database import get_db
from app.services.jwt import token_required
from datetime import datetime
import random
import bcrypt

router = APIRouter(prefix="/api/card", tags=["HasanahCards"])

@router.get("/")
def get_card(user_id: int = Depends(token_required), db: Session = Depends(get_db)):
    submission = db.query(HasanahCards).filter_by(user_id=user_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Card not found")
    return submission.to_dict()

@router.post("/",  status_code=201)
async def add_card(
    request: Request,
    user_id: int = Depends(token_required),
    db: Session = Depends(get_db)
):
    feature_input = await request.json() 
    limit_category = int(feature_input['limit_category'])
    if(limit_category!=0):
        expired_date_data = datetime.utcnow().date().replace(year=datetime.utcnow().year + 5)
        card_no_data = ''.join([str(random.randint(0, 9)) for _ in range(16)])

        card = HasanahCards(
            card_no=card_no_data,
            expired_date=expired_date_data,
            user_id=user_id,
            card_category_id=limit_category
        )

        db.add(card)
        db.commit()
        db.refresh(card)
        return {"message": "Card inserted successfully"}
    else:
        return  {"message": "Card declined"}


@router.post("/pin",  status_code=201)
async def set_pin(
    request: Request,
    user_id: int = Depends(token_required),
    db: Session = Depends(get_db)
):
    hasanah_card = db.query(HasanahCards).filter_by(user_id=user_id).first()
    if not hasanah_card:
        raise HTTPException(status_code=404, detail="Card not found")
    feature_input = await request.json() 

    raw_pin = feature_input.get('pin')
    if not raw_pin:
        raise HTTPException(status_code=400, detail="PIN is required")

    if not raw_pin.isdigit() or len(raw_pin) != 6:
        raise HTTPException(status_code=400, detail="PIN must be a 6-digit number")

    hashed_pin = bcrypt.hashpw(raw_pin.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    hasanah_card.pin=hashed_pin
    db.commit()
    return {"message": "Pin create successfully"}