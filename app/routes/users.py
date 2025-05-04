from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.models import Users
from app.database import get_db
from app.services.jwt import token_required
import jwt
import datetime
import bcrypt
from app.config import Config

router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)

@router.get("/", dependencies=[Depends(token_required)])
def get_by_id(user_id: int = Depends(token_required), db: Session = Depends(get_db)):
    user = db.query(Users).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    return user.to_dict()

@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    username = str(body['username'])
    password = str(body['password'])

    user = db.query(Users).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=401, detail="username atau password salah")

    if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        token = jwt.encode({
            'userId': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, Config.SECRET_KEY, algorithm='HS256')

        return {
            "status": "Success",
            "token": token
        }
    else:
        raise HTTPException(status_code=401, detail="username atau password salah")
