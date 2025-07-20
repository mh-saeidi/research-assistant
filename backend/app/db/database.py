from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url

from pydantic_settings import BaseSettings

from app.core.config import settings

POSTGRES_URL = settings.postgres_url

engine = create_engine(POSTGRES_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def create_database():
    parsed_url = make_url(POSTGRES_URL)

    db_name = parsed_url.database
    if not db_name:
        raise ValueError("Database name not found.")
    
    default_db_url = parsed_url._replace(database="postgres")

    temp_engine = create_engine(default_db_url)

    try:
        with temp_engine.connect() as connection:
            connection.execution_options(isolation_level="AUTOCOMMIT")

            db_exists_query = text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            result = connection.execute(db_exists_query).scalar_one_or_none()

            if result is None:
                print(f"Database '{db_name}' does not exist. Attempting to create it...")
                try:
                    create_db_query = text(f"CREATE DATABASE {db_name}")
                    connection.execute(create_db_query)
                    print(f"Database '{db_name}' created successfully.")
                except Exception as e:
                    print(f"Error creating database '{db_name}': {e}")
                    raise
            else:
                print(f"Database '{db_name}' already exists. Skipping creation.")
    except Exception as e:
        print(f"An error occurred during database existence check or creation: {e}")
        raise

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()