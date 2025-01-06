from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

import pytz
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
)
from sqlalchemy import Boolean, Float, Text
from sqlalchemy import CHAR, Date
from sqlalchemy import DECIMAL, TIMESTAMP
from sqlalchemy import Enum
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType
import os
from config import constant

UTC = pytz.utc
IST = pytz.timezone("Asia/Kolkata")

host = constant.get("db_host")
database = constant.get("db_name")
port = constant.get("db_port")
user = constant.get("db_username")
db_url = f"mysql+aiomysql://{user}:{password}@{host}:{port}/{database}"
# db_url = "mysql+aiomysql://root:my-secret-pw@127.0.0.1:3306/learn"

engine = create_async_engine(db_url, echo=True)
Sessionlocal = async_sessionmaker(
    autoflush=False, autocommit=False, bind=engine, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    phone = Column(String(15), nullable=True)
    address = Column(String(500), nullable=True)
    role = Column(Enum('customer', 'admin', name="user_roles"),
                  default='customer')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(IST))


async def get_db():
    # async with engine.begin() as conn:
    # await conn.run_sync(Base.metadata.create_all)
    db = Sessionlocal()
    try:
        yield db
    finally:
        await db.close()
