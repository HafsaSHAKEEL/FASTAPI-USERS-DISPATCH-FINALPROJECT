import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the database URL from the environment variables
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")


def get_db():
    """
    Provides a database session for use in a FastAPI endpoint.

    This function creates a new database session using the SessionLocal class,
    and ensures that the session is properly closed after use.

    Yields:
    - Session: A SQLAlchemy session object.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
