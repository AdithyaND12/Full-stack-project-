"""Pydantic schemas = what FastAPI accepts (Create) and returns (Read)."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class RegisterIn(BaseModel):
    name: str
    university_email: str
    password: str
    phone: Optional[str] = None
    department: Optional[str] = None


class LoginIn(BaseModel):
    university_email: str
    password: str


class UserRead(BaseModel):
    user_id: int
    name: str
    university_email: str
    role: Optional[str] = None
    is_verified: bool = False

    class Config:
        from_attributes = True


class CategoryRead(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ListingCreate(BaseModel):
    category_id: int
    title: str
    description: Optional[str] = None
    price: Decimal
    type: Optional[str] = "sale"
    condition: Optional[str] = "used"


class ListingRead(BaseModel):
    listing_id: int
    seller_id: int
    category_id: int
    title: str
    description: Optional[str] = None
    price: Decimal
    type: Optional[str] = None
    condition: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    conversation_id: int
    body: str


class MessageRead(BaseModel):
    message_id: int
    conversation_id: int
    sender_id: int
    body: str
    sent_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    listing_id: int


class RequestCreate(BaseModel):
    category_id: Optional[int] = None
    title: str
    max_price: Optional[Decimal] = None


class RequestRead(BaseModel):
    request_id: int
    buyer_id: int
    title: str
    max_price: Optional[Decimal] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    listing_id: int
    rating: int
    comment: Optional[str] = None


class NotificationRead(BaseModel):
    notification_id: int
    body: str
    is_read: bool = False

    class Config:
        from_attributes = True
