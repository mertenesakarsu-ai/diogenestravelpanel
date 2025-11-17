from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import pandas as pd
import io


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ==================== MODELS ====================

# Flight Models
class Flight(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    flightCode: str
    airline: str = ""
    from_location: str = Field(alias="from")
    to: str
    date: str
    time: str
    direction: str  # "arrival" or "departure"
    passengers: int = 0
    hasPNR: bool = False
    pnr: str = ""
    daysUntilFlight: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FlightCreate(BaseModel):
    flightCode: str
    airline: str = ""
    from_location: str = Field(alias="from")
    to: str
    date: str
    time: str
    direction: str
    passengers: int = 0
    hasPNR: bool = False
    pnr: str = ""
    daysUntilFlight: int = 0

# User Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    role: str  # "admin", "reservation", "operation", "flight"
    status: str = "active"  # "active", "inactive"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    name: str
    email: str
    role: str
    status: str = "active"

# Log Models
class SystemLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user: str
    action: str  # "CREATE", "UPDATE", "DELETE", "IMPORT_EXCEL", etc.
    entity: str  # "flights", "reservations", "users"
    entityId: str = ""
    details: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Reservation Models
class Reservation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    voucherNo: str
    leader_name: str
    leader_passport: str
    product_code: str
    product_name: str
    hotel: str
    arrivalDate: str
    departureDate: str
    pax: int
    status: str  # "confirmed", "pending", "cancelled"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReservationCreate(BaseModel):
    voucherNo: str
    leader_name: str
    leader_passport: str
    product_code: str
    product_name: str
    hotel: str
    arrivalDate: str
    departureDate: str
    pax: int
    status: str = "pending"

# Health Check Model
class HealthStatus(BaseModel):
    database: str
    total_flights: int
    total_reservations: int
    total_users: int
    total_logs: int
    status: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()