from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, Request, Security
from jose import JWTError, jwt
from fastapi import FastAPI, HTTPException, Depends
from fastapi.routing import APIRouter
from slowapi import Limiter
from models.users_model import User, get_db
from reqSchemas.UsersSchema import UserCreate, get_password_hash, verify_password
# import jwt
from sqlalchemy.exc import NoResultFound
from datetime import datetime, timedelta
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import pytz
from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi import _rate_limit_exceeded_handler, Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from config import constant


limiter = Limiter(key_func=get_remote_address)
FastAPI().state.limiter = limiter
FastAPI().add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
SECRET_KEY = constant.get("SECRET")
ALGORITHM = constant.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = constant.get("ACCESS_TOKEN_EXPIRE_MINUTES")
UTC = pytz.utc
IST = pytz.timezone("Asia/Kolkata")
userR = APIRouter(prefix='/user', tags=['User'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


async def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(IST) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # If valid, return payload
    except JWTError:
        return None  # Return None if invalid or expired


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = await verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=401, detail="Token is invalid or expired")
    return payload


async def get_admin_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = await verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=401, detail="Token is invalid or expired"
        )
    result = await db.execute(select(User).filter(User.email == payload["sub"]))
    user = result.scalars().first()
    if str(user.role).lower() != 'admin':
        raise HTTPException(
            status_code=401, detail="Token is invalid or expired"
        )
    return payload


@userR.post("/register")
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        existing_user = await db.execute(select(User).filter(User.email == user.email))
        user_data = existing_user.scalars().one()
    except NoResultFound:
        user_data = None
    if user_data:
        print(user_data.__dict__)
        raise HTTPException(status_code=400, detail="Email already registered")
    passwd = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        password_hash=passwd,
        name=user.name,
        phone=user.phone,
        address=user.address
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email, "name": new_user.name}


@userR.post("/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user_data = await db.execute(select(User).filter(User.email == form_data.username))
    user = user_data.scalars().first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token_data = {"sub": user.email, "user_id": user.id}
    access_token = await create_access_token(data=token_data)
    return {"access_token": access_token, "token_type": "bearer"}


@userR.post("/validate-token")
async def validate_token(request: Request, token: str = Depends(oauth2_scheme)):
    payload = await verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=401, detail="Token is invalid or expired")
    return payload


@userR.get("/dbhealthcheck")
@limiter.limit("3/minute")
async def dbheatltcheck(request: Request, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User))
    if not user:
        raise HTTPException(
            status_code=500, detail="Database not connected"
        )
    return {"status": "up", "timestamp": datetime.now(IST)}
