from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from contextlib import contextmanager
import os

from models import Base  # Import from models.py

# ------------------------
#   ENV + ENGINE SETUP
# ------------------------

load_dotenv()

# Path setup
basedir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(basedir)
db_filename = "events.db"

# Full absolute path to the database inside the container
default_db_path = os.path.join(parent_dir, "data", db_filename)
print(default_db_path)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{default_db_path}")

# Ensure folder exists
os.makedirs(os.path.dirname(default_db_path), exist_ok=True)

# Database engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Create session 
SessionLocal = sessionmaker(
    bind=engine, 
    autocommit=False, 
    autoflush=False
)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Session:
    """
    Return a new database session.
    Use `with get_db() as db:` to close automatically
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def add_to_db(session, instance, return_bool=False):
    """
    Add and commit a new record to the database.

    Returns:
        If return_bool=True: (bool): True on success, False on failure.
        Else: (instance) returns the instance.
    """
    try:
        session.add(instance)
        session.commit()
        session.refresh(instance)
        return True if return_bool else instance
    except Exception as e:
        session.rollback()
        if return_bool:
            return False
        raise e
