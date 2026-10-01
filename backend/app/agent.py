"""Campus Mart LLM agent: OpenRouter + LangGraph + live MySQL tools.

Beginner map:
  * ChatOpenAI (via OpenRouter) = the brain (cloud model, needs
    OPENROUTER_API_KEY, internet required).
  * @tool fns   = the hands. The LLM can ONLY touch the DB through these
                  6 narrow tools — it can never write raw SQL, see passwords,
                  or delete anything.
  * create_react_agent = the LangGraph loop: think -> call tool -> read
                  result -> repeat (max 5 rounds) -> final answer.
  * Keyword overlap re-ranks search hits by meaning,
    so "cheap calculator for sem 3" finds the fx-991ES (no local
    embeddings needed).

Env vars (in backend/.env):
  OPENROUTER_API_KEY = sk-or-v1-... (required)
  OPENROUTER_MODEL   = nvidia/nemotron-3-ultra-550b-a55b:free (default, free)
"""
import os
import re
from typing import Any, Optional

from dotenv import load_dotenv

load_dotenv()

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from sqlalchemy import or_, text
from sqlalchemy.orm import Session

CHAT_MODEL = os.getenv(
    "OPENROUTER_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
MAX_STEPS = 5

SYSTEM = """You are Campus AI, the shopping assistant for Campus Mart, a campus-only \
student marketplace (MySQL: Users, Categories, Listings, Listing_Images, Rentals, \
Conversations, Messages, Requests, Reviews).

Rules:
1. Answer ONLY from tool results. Never invent listings, prices, or sellers.
2. Cite listings as [id:123] when you mention one. Prices in Rs.
3. If nothing matches, say so plainly and suggest posting a Want-to-Buy Request.
4. Refuse destructive, admin, or personal-data requests (delete/drop/passwords/\
phones/emails). There is no tool for those — say you cannot do that.
5. Keep answers short. End with a campus-pickup hint (library / student center) \
when recommending an item.
"""

SCHEMA_TEXT = """Tables you can use (via tools only):
- Categories(category_id, name, description)
- Listings(listing_id, seller_id, category_id, title, description, price, \
type[sale|rent|service], condition[new|like-new|used], status, created_at)
- Listing_Images(image_id, listing_id, image_url)
- Rentals(listing_id, price_per_day, deposit, max_duration_days)
- Conversations(conversation_id, listing_id, buyer_id, seller_id)
- Messages(message_id, conversation_id, sender_id, body, sent_at)
- Requests(request_id, buyer_id, category_id, title, max_price, status)
- Reviews(review_id, listing_id, reviewer_id, seller_id, rating 1-5, comment)
No password/phone/email columns exist for you. No writes except via tools."""

_llm: Optional[ChatOpenAI] = None


def get_llm() -> ChatOpenAI:
    """Lazy singleton: importing this module never fails if key is missing."""
    global _llm
    if _llm is None:
        key = os.getenv("OPENROUTER_API_KEY", OPENROUTER_API_KEY) or ""
        if not key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. Add it to backend/.env "
                "and restart the server.")
        _llm = ChatOpenAI(
            model=os.getenv("OPENROUTER_MODEL", CHAT_MODEL),
            temperature=0,
            openai_api_key=key,
            openai_api_base=OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": "http://127.0.0.1:8000",
                "X-Title": "Campus Mart",
            },
        )
    return _llm


def llm_ok() -> bool:
    """Ping check used by GET /agent/health and before running the graph."""
    try:
        get_llm().invoke("Reply with exactly: OK")
        return True
    except Exception:
        return False


# Backwards-compat alias (old health endpoint / tests may call this).
def ollama_ok() -> bool:
    return llm_ok()


def build_tools(db: Session):
    """Tools close over ONE request-scoped MySQL session (thread-safe)."""

    @tool
    def db_schema() -> str:
        """What tables/columns exist. Call this when unsure what you can query."""
        return SCHEMA_TEXT

    @tool
    def search_listings(q: str = "", category: str = "",
                        max_price: Optional[float] = None,
                        type: str = "", limit: int = 10) -> str:
        """Search ACTIVE listings by keywords, with optional category / budget / \
type filters. Returns id, title, price, category, condition. Use this first \
for any 'find/cheapest/show me X' question."""
        from . import models
        query = db.query(models.Listing).join(
            models.Category,
            models.Listing.category_id == models.Category.category_id)
        if q:
            like = f"%{q}%"
            query = query.filter(or_(models.Listing.title.like(like),
                                     models.Listing.description.like(like)))
        if category:
            query = query.filter(models.Category.name == category)
        if max_price is not None:
            query = query.filter(models.Listing.price <= max_price)
        if type:
            query = query.filter(models.Listing.type == type)
        rows = query.filter(models.Listing.status == "active").order_by(
            models.Listing.price).limit(max(limit * 2, 10)).all()
        if not rows:
            return "No matching active listings."
        cands = [{"listing_id": r.listing_id, "title": r.title,
                  "price": float(r.price),
                  "category": db.get(models.Category, r.category_id).name,
                  "condition": r.condition, "type": r.type,
                  "text": f"{r.title} {(r.description or '')}"} for r in rows]
        # Meaning re-rank with keyword overlap (no external call — works
        # offline and with any OpenRouter model).
        if q and len(cands) > 1:
            qtok = set(re.findall(r"\w+", q.lower()))
            def _score(c):
                ctok = set(re.findall(r"\w+", c["text"].lower()))
                return len(qtok & ctok)
            cands = sorted(cands, key=_score, reverse=True)
        return "\n".join(
            f"[id:{c['listing_id']}] {c['title']} | Rs.{c['price']} | "
            f"{c['category']} | {c['condition']} | {c['type']}"
            for c in cands[:limit])

    @tool
    def get_listing(listing_id: int) -> str:
        """Full details of ONE listing: description, seller name, photos, \
rent terms if any."""
        from . import models
        r = db.get(models.Listing, listing_id)
        if not r:
            return "Listing not found."
        seller = db.get(models.User, r.seller_id)
        cat = db.get(models.Category, r.category_id)
        imgs = db.query(models.ListingImage).filter_by(
            listing_id=listing_id).all()
        rent = db.query(models.Rental).filter_by(
            listing_id=listing_id).first()
        out = (f"[id:{r.listing_id}] {r.title} | Rs.{float(r.price)} | "
               f"{cat.name if cat else '?'} | {r.condition} | {r.type} | "
               f"{r.status}\nDesc: {r.description or '-'}\n"
               f"Seller: {seller.name if seller else '?'}")
        if imgs:
            out += f"\nPhotos: {len(imgs)} available"
        if rent:
            out += (f"\nRent: Rs.{float(rent.price_per_day)}/day, "
                    f"deposit Rs.{float(rent.deposit)}")
        return out

    @tool
    def seller_trust(user_id: int) -> str:
        """Trust summary for a seller: avg rating, review count, completed \
sales (from the Seller_Trust view)."""
        row = db.execute(
            text("SELECT * FROM Seller_Trust WHERE user_id=:u"),
            {"u": user_id}).mappings().first()
        if not row:
            return "Seller not found."
        return (f"Seller {row['name']}: avg rating {row['avg_rating']}, "
                f"{row['total_reviews']} reviews, "
                f"{row['completed_sales']} completed sales.")

    @tool
    def category_stats() -> str:
        """Count + average price of ACTIVE listings per category."""
        rows = db.execute(text(
            "SELECT c.name, COUNT(*) n, ROUND(AVG(l.price),0) avg_p "
            "FROM Listings l JOIN Categories c "
            "ON l.category_id=c.category_id "
            "WHERE l.status='active' GROUP BY c.name ORDER BY n DESC")
        ).mappings().all()
        return "\n".join(
            f"{r['name']}: {r['n']} items, avg Rs.{r['avg_p']}" for r in rows)

    @tool
    def open_requests(limit: int = 10) -> str:
        """Open Want-to-Buy requests from buyers."""
        from . import models
        rows = db.query(models.Request).filter_by(
            status="open").order_by(
                models.Request.created_at.desc()).limit(limit).all()
        if not rows:
            return "No open requests."
        return "\n".join(
            f"[req:{r.request_id}] {r.title} (max Rs.{r.max_price})"
            for r in rows)

    return [db_schema, search_listings, get_listing,
            seller_trust, category_stats, open_requests]


def ask(question: str, db: Session) -> dict[str, Any]:
    """Run one question through the LangGraph ReAct agent. Returns
    {answer, listing_ids, tools_used}. Raises RuntimeError if key down."""
    try:
        llm = get_llm()
    except RuntimeError as e:
        raise RuntimeError(str(e))
    if not llm_ok():
        raise RuntimeError("OpenRouter is not reachable. Check OPENROUTER_API_KEY "
                           "and your internet connection.")
    agent = create_react_agent(llm, build_tools(db),
                               prompt=SYSTEM)
    result = agent.invoke(
        {"messages": [("user", question)]},
        {"recursion_limit": 2 * MAX_STEPS + 1})
    msgs = result.get("messages", [])
    answer = msgs[-1].content if msgs else "No answer."
    tools_used: list[str] = []
    for m in msgs:
        for call in getattr(m, "tool_calls", []) or []:
            name = call.get("name", "")
            if name and name not in tools_used:
                tools_used.append(name)
    listing_ids = sorted({int(x) for x in
                          re.findall(r"\[id:(\d+)\]", str(answer))})
    return {"answer": answer if isinstance(answer, str) else str(answer),
            "listing_ids": listing_ids, "tools_used": tools_used}
