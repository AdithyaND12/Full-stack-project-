"""SQLAlchemy models = Python mirror of 01_schema.sql.
Table names MUST match MySQL exactly: Users, Categories, Listings, etc.
Beginner rule: one class = one table, one attribute = one column."""
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Enum, Boolean,
    TIMESTAMP, ForeignKey, UniqueConstraint, Index, text,
)
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "Users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    university_email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(15))
    role = Column(Enum("student", "faculty", "staff"), default="student")
    department = Column(String(50))
    is_verified = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    listings = relationship("Listing", back_populates="seller",
                            cascade="all, delete-orphan",
                            foreign_keys="Listing.seller_id")


class Category(Base):
    __tablename__ = "Categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255))

    listings = relationship("Listing", back_populates="category")


class Listing(Base):
    __tablename__ = "Listings"

    listing_id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(Integer, ForeignKey("Users.user_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("Categories.category_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    type = Column(Enum("sale", "rent", "service"), default="sale")
    condition = Column("condition", Enum("new", "like-new", "used"), default="used")
    status = Column(Enum("active", "sold", "rented", "inactive"), default="active")
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    seller = relationship("User", back_populates="listings", foreign_keys=[seller_id])
    category = relationship("Category", back_populates="listings")
    images = relationship("ListingImage", back_populates="listing", cascade="all, delete-orphan")
    rental = relationship("Rental", back_populates="listing", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_listings_category_status", "category_id", "status"),
        Index("idx_listings_price", "price"),
    )


class ListingImage(Base):
    __tablename__ = "Listing_Images"

    image_id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(Integer, ForeignKey("Listings.listing_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    image_url = Column(String(255), nullable=False)
    sort_order = Column(Integer, default=0)

    listing = relationship("Listing", back_populates="images")


class Rental(Base):
    __tablename__ = "Rentals"

    rental_id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(Integer, ForeignKey("Listings.listing_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, unique=True)
    price_per_day = Column(Numeric(10, 2), nullable=False)
    deposit = Column(Numeric(10, 2), default=0)
    max_duration_days = Column(Integer)

    listing = relationship("Listing", back_populates="rental")


class Conversation(Base):
    __tablename__ = "Conversations"

    conversation_id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(Integer, ForeignKey("Listings.listing_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("Users.user_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    seller_id = Column(Integer, ForeignKey("Users.user_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("listing_id", "buyer_id", name="uq_conversation"),)


class Message(Base):
    __tablename__ = "Messages"

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("Conversations.conversation_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("Users.user_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    body = Column(Text, nullable=False)
    sent_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    is_read = Column(Boolean, default=False)

    conversation = relationship("Conversation", back_populates="messages")


class Request(Base):
    """Want-to-buy board. buyer_id WHO wants, category_id WHICH shelf."""
    __tablename__ = "Requests"

    request_id = Column(Integer, primary_key=True, autoincrement=True)
    buyer_id = Column(Integer, ForeignKey("Users.user_id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("Categories.category_id", ondelete="SET NULL"))
    title = Column(String(100), nullable=False)
    max_price = Column(Numeric(10, 2))
    status = Column(Enum("open", "matched", "closed"), default="open")
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class Review(Base):
    """Trust rating after pickup. rating 1-5, one per buyer per listing."""
    __tablename__ = "Reviews"

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(Integer, ForeignKey("Listings.listing_id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("Users.user_id", ondelete="CASCADE"), nullable=False)
    seller_id = Column(Integer, ForeignKey("Users.user_id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class Notification(Base):
    __tablename__ = "Notifications"

    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users.user_id", ondelete="CASCADE"), nullable=False)
    body = Column(String(255), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
