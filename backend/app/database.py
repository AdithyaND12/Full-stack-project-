"""DB connection. Beginner idea: engine = phone line to MySQL,
SessionLocal = one phone call (one request), get_db = hang up after call."""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()  # reads backend/.env if present

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root@localhost/campus_mart?unix_socket=/tmp/mysql.sock")

# echo=False keeps logs clean; pool_pre_ping avoids "MySQL gone away" errors
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
