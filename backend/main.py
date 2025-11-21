from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TedCar 2.0 API", description="Backend for TedCar 2.0", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .routers import auth, vehicles

app.include_router(auth.router)
app.include_router(vehicles.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to TedCar 2.0 API"}
