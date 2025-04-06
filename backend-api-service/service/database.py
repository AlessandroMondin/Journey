from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from functools import wraps
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# Create a data directory in the project root
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "sqlite"
os.makedirs(DATA_DIR, exist_ok=True)

# Database URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATA_DIR}/elevenlabs_rag.db"

# Create SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Transaction decorator
def transactional(func):
    """
    Decorator to make a function transactional.
    It will commit the transaction if the function executes successfully,
    or rollback if an exception occurs.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        db = kwargs.get("db")
        if db is None:
            # Try to find db in args
            for arg in args:
                if hasattr(arg, "commit") and hasattr(arg, "rollback"):
                    db = arg
                    break

        if db is None:
            raise ValueError("No database session found in function arguments")

        try:
            # Execute the function and get the result
            result = await func(*args, **kwargs)

            # Commit the transaction
            db.commit()

            # Refresh the result object if it has a primary key attribute
            if hasattr(result, "id") and result.id is None:
                db.refresh(result)

            # If result is a dictionary with objects that need refreshing
            if isinstance(result, dict):
                for key, value in result.items():
                    if hasattr(value, "id") and value.id is None:
                        db.refresh(value)

            return result
        except HTTPException as http_exc:
            logger.error(f"HTTP exception: {http_exc}")
            # Rollback on HTTP exceptions but preserve the exception
            db.rollback()
            raise http_exc
        except Exception as e:
            logger.error(f"Exception: {e}")
            # Rollback on other errors
            db.rollback()
            raise e

    return wrapper
