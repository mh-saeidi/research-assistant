from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, status

from app.db.database import create_database, engine
from app.db.models import Base
from app.api import users

import contextlib

@contextlib.asynccontextmanager
async def lifespan(app):
    """
    Ensures the database exists before the application starts serving requests.
    """
    print("Application startup: Checking and creating database...")
    try:
        create_database()
        Base.metadata.create_all(bind=engine)
        print("Database setup complete.")

    except Exception as e:
        print(f"Critical error during database setup: {e}")
        raise

    yield

    print("Application shutdown: Performing cleanup (e.g., closing connections)...")

app = FastAPI(
    title="Researcher AI",
    description="AI researcher agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    root_path="/api",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(users.router, prefix="/users", tags=["Users"])

@app.get("/", status_code=status.HTTP_200_OK, tags=["Health Check"])
def health_check():

    return "AI researcher agent is running!"