"""Campus Mart API - complete. Run from backend/: uvicorn app.main:app --reload
Docs: http://127.0.0.1:8000/docs | Frontend: http://127.0.0.1:8000/"""
import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, text

from .database import get_db, engine, Base
from . import models
from .schemas import (
    RegisterIn, LoginIn, UserRead, CategoryRead, ListingCreate, ListingRead,
    MessageCreate, MessageRead, ConversationCreate, RequestCreate, RequestRead,
    ReviewCreate, NotificationRead,
)
from .auth import hash_pw, check_pw, make_token, need_user

app = FastAPI(title="Campus Mart API", version="1.0")
Base.metadata.create_all(bind=engine, checkfirst=True)

UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/health")
def health():
    return {"ok": True}


# ---------- Auth ----------
@app.post("/auth/register", response_model=UserRead)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if "@" not in data.university_email or not data.university_email.endswith((".ac.in", ".edu")):
        raise HTTPException(400, "Use your university email (@bmsce.ac.in / .edu)")
    if db.query(models.User).filter_by(university_email=data.university_email).first():
        raise HTTPException(400, "Email already registered")
    row = models.User(name=data.name, university_email=data.university_email,
                      password_hash=hash_pw(data.password), phone=data.phone,
                      department=data.department, is_verified=True)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.post("/auth/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(university_email=data.university_email).first()
    if not user or not check_pw(data.password, user.password_hash):
        raise HTTPException(401, "Wrong email or password")
    return {"token": make_token(user.user_id),
            "user": {"user_id": user.user_id, "name": user.name,
                     "university_email": user.university_email}}


@app.get("/me", response_model=UserRead)
def me(user: models.User = Depends(need_user)):
    return user


# ---------- Categories / Listings ----------
@app.get("/categories", response_model=list[CategoryRead])
def categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()


@app.get("/listings", response_model=list[ListingRead])
def list_listings(category: Optional[str] = None, q: Optional[str] = None,
                  min_price: Optional[float] = None, max_price: Optional[float] = None,
                  db: Session = Depends(get_db)):
    query = db.query(models.Listing)
    if category:
        query = query.join(models.Category).filter(models.Category.name == category)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(models.Listing.title.like(like),
                                 models.Listing.description.like(like)))
    if min_price is not None:
        query = query.filter(models.Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Listing.price <= max_price)
    return query.filter(models.Listing.status == "active").order_by(models.Listing.price).all()


@app.get("/listings/{listing_id}", response_model=ListingRead)
def one_listing(listing_id: int, db: Session = Depends(get_db)):
    row = db.get(models.Listing, listing_id)
    if not row:
        raise HTTPException(404, "Not found")
    return row


@app.post("/listings", response_model=ListingRead)
def create_listing(data: ListingCreate, db: Session = Depends(get_db),
                   user: models.User = Depends(need_user)):
    row = models.Listing(seller_id=user.user_id, **data.model_dump())
    db.add(row)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(400, str(getattr(e, "orig", e)))
    db.refresh(row)
    # auto-match: notify buyers whose request fits (same category + price in budget)
    try:
        matches = db.query(models.Request).filter(
            models.Request.status == "open",
            or_(models.Request.category_id.is_(None),
                models.Request.category_id == row.category_id),
            or_(models.Request.max_price.is_(None),
                models.Request.max_price >= row.price)).all()
        for m in matches:
            db.add(models.Notification(
                user_id=m.buyer_id,
                body=f"New match: {row.title} (Rs.{row.price}) fits your request!"))
            m.status = "matched"
        db.commit()
    except Exception:
        db.rollback()
    return row


@app.patch("/listings/{listing_id}/sold", response_model=ListingRead)
def mark_sold(listing_id: int, db: Session = Depends(get_db),
              user: models.User = Depends(need_user)):
    row = db.get(models.Listing, listing_id)
    if not row or row.seller_id != user.user_id:
        raise HTTPException(404, "Not yours")
    row.status = "sold"
    db.commit()
    db.refresh(row)
    return row


@app.post("/listings/{listing_id}/image")
def upload_image(listing_id: int, file: UploadFile = File(...),
                 db: Session = Depends(get_db), user: models.User = Depends(need_user)):
    row = db.get(models.Listing, listing_id)
    if not row or row.seller_id != user.user_id:
        raise HTTPException(404, "Not yours")
    ext = os.path.splitext(file.filename or "")[1][:8] or ".jpg"
    dest = UPLOAD_DIR / f"listing_{listing_id}_{file.filename}".replace("/", "_")
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    db.add(models.ListingImage(listing_id=listing_id, image_url=f"/uploads/{dest.name}"))
    db.commit()
    return {"url": f"/uploads/{dest.name}"}


# ---------- Chat ----------
@app.post("/conversations")
def open_conversation(data: ConversationCreate, db: Session = Depends(get_db),
                      user: models.User = Depends(need_user)):
    lst = db.get(models.Listing, data.listing_id)
    if not lst:
        raise HTTPException(404, "Listing gone")
    if lst.seller_id == user.user_id:
        raise HTTPException(400, "Can't chat with yourself")
    conv = db.query(models.Conversation).filter_by(
        listing_id=data.listing_id, buyer_id=user.user_id).first()
    if not conv:
        conv = models.Conversation(listing_id=data.listing_id, buyer_id=user.user_id,
                                   seller_id=lst.seller_id)
        db.add(conv)
        db.commit()
        db.refresh(conv)
    return {"conversation_id": conv.conversation_id}


@app.get("/conversations/{cid}/messages", response_model=list[MessageRead])
def history(cid: int, db: Session = Depends(get_db), user: models.User = Depends(need_user)):
    return db.query(models.Message).filter_by(conversation_id=cid).order_by(models.Message.sent_at).all()


@app.post("/messages", response_model=MessageRead)
def send(data: MessageCreate, db: Session = Depends(get_db), user: models.User = Depends(need_user)):
    row = models.Message(conversation_id=data.conversation_id, sender_id=user.user_id, body=data.body)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# ---------- Requests / Reviews / Notifications ----------
@app.post("/requests", response_model=RequestRead)
def add_request(data: RequestCreate, db: Session = Depends(get_db), user: models.User = Depends(need_user)):
    row = models.Request(buyer_id=user.user_id, **data.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/requests", response_model=list[RequestRead])
def open_requests(db: Session = Depends(get_db)):
    return db.query(models.Request).filter_by(status="open").order_by(models.Request.created_at.desc()).all()


@app.post("/reviews")
def add_review(data: ReviewCreate, db: Session = Depends(get_db), user: models.User = Depends(need_user)):
    lst = db.get(models.Listing, data.listing_id)
    if not lst:
        raise HTTPException(404, "Listing gone")
    if not (1 <= data.rating <= 5):
        raise HTTPException(400, "Rating 1-5")
    db.add(models.Review(listing_id=data.listing_id, reviewer_id=user.user_id,
                         seller_id=lst.seller_id, rating=data.rating, comment=data.comment))
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(400, "You already reviewed this")
    return {"ok": True}


@app.get("/sellers/{uid}/trust")
def trust(uid: int, db: Session = Depends(get_db)):
    row = db.execute(text("SELECT * FROM Seller_Trust WHERE user_id=:u"), {"u": uid}).mappings().first()
    return dict(row) if row else {"user_id": uid, "avg_rating": None, "total_reviews": 0}


@app.get("/notifications", response_model=list[NotificationRead])
def notifs(db: Session = Depends(get_db), user: models.User = Depends(need_user)):
    return db.query(models.Notification).filter_by(user_id=user.user_id).order_by(
        models.Notification.created_at.desc()).limit(20).all()


# ---------- LLM agent (OpenRouter + LangGraph, read-only DB tools) ----------
class AgentAsk(BaseModel):
    question: str


@app.get("/agent/health")
def agent_health():
    from .agent import llm_ok, CHAT_MODEL
    ok = llm_ok()
    return {"openrouter_ok": ok, "ollama_ok": ok,
            "chat_model": CHAT_MODEL, "model": CHAT_MODEL}


@app.post("/agent/ask")
def agent_ask(data: AgentAsk, db: Session = Depends(get_db)):
    from . import agent as agent_mod
    q = (data.question or "").strip()
    if not q:
        raise HTTPException(400, "Empty question")
    if len(q) > 500:
        raise HTTPException(400, "Question too long (max 500 chars)")
    try:
        return agent_mod.ask(q, db)
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(500, f"Agent error: {e}")


# Serve frontend index at /
@app.get("/")
def index():
    idx = FRONTEND_DIR / "index.html"
    return FileResponse(str(idx)) if idx.exists() else {"msg": "API running, see /docs"}
