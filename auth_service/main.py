from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .config import get_settings
from .database import SessionLocal, get_db
from .models import Role, User
from .schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from .security import create_token, hash_password, verify_password


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    if settings.bootstrap_admin_email and settings.bootstrap_admin_password:
        async with SessionLocal() as db:
            email = settings.bootstrap_admin_email.lower()
            if not await db.scalar(select(User).where(User.email == email)):
                db.add(User(name="Administrator", email=email,
                            password_hash=hash_password(settings.bootstrap_admin_password),
                            role=Role.admin))
                try:
                    await db.commit()
                except IntegrityError:
                    await db.rollback()  # another replica bootstrapped it first
    yield


app = FastAPI(title="SOAT Identity Service", version="1.0.0", lifespan=lifespan)


@app.get("/health", tags=["Operations"])
async def health():
    return {"status": "ok"}


@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    email = data.email.lower()
    if await db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(name=data.name, email=email, password_hash=hash_password(data.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@app.post("/auth/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=create_token(user))
