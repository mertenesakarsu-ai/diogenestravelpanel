from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Query, Header, Depends, Body
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
from functools import wraps
from passlib.context import CryptContext
import requests
import json
import pymssql
from sqlalchemy.orm import Session
from sqlalchemy import func

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection - Used ONLY for logging
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
mongo_db = client[os.environ['DB_NAME']]

# SQL Server connection - Used for all business data
from sql_models import (
    SessionLocal, engine, 
    SQLUser, SQLFlight, SQLReservation, SQLOperation, SQLHotel, SQLPackage, SQLPackageLeg,
    test_sql_connection, init_sql_db
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency to get SQL database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    password: str  # hashed password
    role: str  # "admin", "reservation", "operation", "flight"
    status: str = "active"  # "active", "inactive"
    profile_picture: Optional[str] = None  # URL or base64 image
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str
    status: str = "active"

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    status: str
    profile_picture: Optional[str] = None
    created_at: datetime

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

# Package Tour Models
class PackageLeg(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    step_number: int
    leg_type: str  # "hotel", "transfer", "airport_pickup", "airport_dropoff"
    location: str
    hotel_name: Optional[str] = None
    hotel_stars: Optional[int] = None
    check_in_date: Optional[str] = None  # Will be calculated based on reservation start date
    check_out_date: Optional[str] = None
    duration_nights: int = 0
    room_type: Optional[str] = None
    board_type: Optional[str] = None
    notes: Optional[str] = None

class Package(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    package_code: str  # e.g., "EISK7"
    name: str  # e.g., "Istanbul-Cappadocia 7 Days Tour"
    description: Optional[str] = None
    total_nights: int = 0
    legs: List[PackageLeg] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PackageCreate(BaseModel):
    package_code: str
    name: str
    description: Optional[str] = None
    total_nights: int = 0
    legs: List[PackageLeg] = []
    is_active: bool = True

# Source Agencies - predefined list
SOURCE_AGENCIES = ["THV", "EURO TOURS", "SELECT HOLIDAYS", "AZURO"]

# Reservation Models (Updated for multi-leg package tours)
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
    pax_adults: int = 0
    pax_children: int = 0
    pax_infants: int = 0
    status: str  # "confirmed", "pending", "cancelled"
    source_agency: str = "THV"  # New field: Source agency
    package_id: Optional[str] = None  # New field: Link to package if multi-leg tour
    current_leg: int = 0  # New field: Current leg number (0 = not started)
    room_type: Optional[str] = None
    board_type: Optional[str] = None
    destination: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
    pax_adults: int = 2
    pax_children: int = 0
    pax_infants: int = 0
    status: str = "pending"
    source_agency: str = "THV"
    package_id: Optional[str] = None
    current_leg: int = 0
    room_type: Optional[str] = None
    board_type: Optional[str] = None
    destination: Optional[str] = None
    notes: Optional[str] = None

# Hotel Models
class Hotel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str  # Otel kodu (örn: "3*ANT")
    name: str  # Otel adı
    category: str = ""  # Kategori (OTEL, 3 YILDIZ, vb.)
    region: str = ""  # Bölgesi
    region_code: str = ""  # Bölge kodu
    transfer_region: str = ""  # Transfer bölgesi
    phone1: str = ""
    phone2: str = ""
    fax: str = ""
    email: str = ""
    email2: str = ""
    email3: str = ""
    website: str = ""
    address: str = ""
    address2: str = ""
    city: str = ""
    postal_code: str = ""
    country: str = ""
    service_type: str = "Otel"  # Servis türü
    manager: str = ""  # Yönetici
    notes: str = ""  # Internal notlar
    active: bool = True  # Aktif/Pasif
    latitude: float = 0.0  # Enlem
    longitude: float = 0.0  # Boylam
    stars: int = 0  # Yıldız sayısı
    paximum_id: str = ""  # Paximum entegrasyon ID
    giata: str = ""  # Giata kodu
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class HotelCreate(BaseModel):
    code: str
    name: str
    category: str = ""
    region: str = ""
    region_code: str = ""
    transfer_region: str = ""
    phone1: str = ""
    phone2: str = ""
    fax: str = ""
    email: str = ""
    email2: str = ""
    email3: str = ""
    website: str = ""
    address: str = ""
    address2: str = ""
    city: str = ""
    postal_code: str = ""
    country: str = ""
    service_type: str = "Otel"
    manager: str = ""
    notes: str = ""
    active: bool = True
    latitude: float = 0.0
    longitude: float = 0.0
    stars: int = 0
    paximum_id: str = ""
    giata: str = ""

# Operation Models
class FlightInfo(BaseModel):
    """Flight information for operations"""
    flightCode: str
    date: str  # YYYY-MM-DD format
    time: str  # HH:MM format
    from_location: str = Field(alias="from")
    to: str
    airline: str = ""

class Operation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reservationId: Optional[str] = None  # Link to reservation
    voucherNo: str = ""  # Voucher number from reservation
    
    # Flight Information
    arrivalFlight: Optional[Dict[str, Any]] = None  # Arrival flight details
    returnFlight: Optional[Dict[str, Any]] = None  # Return flight details (optional)
    transferFlight: Optional[Dict[str, Any]] = None  # Transfer flight details (optional)
    
    # Hotel Information
    currentHotel: str = ""
    hotelCheckIn: str = ""  # YYYY-MM-DD HH:MM format
    hotelCheckOut: str = ""  # YYYY-MM-DD HH:MM format
    
    # Legacy fields (for backward compatibility)
    flightCode: str = ""
    type: str = "transfer"  # "arrival", "departure", "transfer"
    from_location: str = Field(default="", alias="from")
    to: str = ""
    date: str = ""
    time: str = ""
    passengers: int = 0
    hotel: str = ""
    transferTime: str = ""
    notes: str = ""
    status: str = "scheduled"  # "scheduled", "in_progress", "completed"
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OperationCreate(BaseModel):
    reservationId: Optional[str] = None
    voucherNo: str = ""
    
    # Flight Information
    arrivalFlight: Optional[Dict[str, Any]] = None
    returnFlight: Optional[Dict[str, Any]] = None
    transferFlight: Optional[Dict[str, Any]] = None
    
    # Hotel Information
    currentHotel: str = ""
    hotelCheckIn: str = ""
    hotelCheckOut: str = ""
    
    # Legacy fields
    flightCode: str = ""
    type: str = "transfer"
    from_location: str = Field(default="", alias="from")
    to: str = ""
    date: str = ""
    time: str = ""
    passengers: int = 0
    hotel: str = ""
    transferTime: str = ""
    notes: str = ""
    status: str = "scheduled"

# Health Check Model
class HealthStatus(BaseModel):
    database: str
    total_flights: int
    total_reservations: int
    total_users: int
    total_logs: int
    status: str

# ==================== PERMISSION SYSTEM ====================

# Role-based permissions mapping
PERMISSIONS = {
    "admin": {
        "flights": ["read", "create", "update", "delete", "upload"],
        "reservations": ["read", "create", "update", "delete", "upload"],
        "operations": ["read", "create", "update", "delete", "upload"],
        "hotels": ["read", "create", "update", "delete", "upload"],
        "users": ["read", "create", "update", "delete"],
        "logs": ["read"],
        "management": ["read"]
    },
    "flight": {
        "flights": ["read", "create", "update", "delete", "upload"],
        "reservations": ["read"],
        "operations": ["read"],
        "users": [],
        "logs": [],
        "management": ["read"]
    },
    "reservation": {
        "flights": ["read"],
        "reservations": ["read", "create", "update", "delete", "upload"],
        "operations": ["read"],
        "hotels": ["read", "create", "update", "delete", "upload"],
        "users": [],
        "logs": [],
        "management": ["read"]
    },
    "operation": {
        "flights": ["read"],
        "reservations": ["read"],
        "operations": ["read", "create", "update", "delete", "upload"],
        "users": [],
        "logs": [],
        "management": ["read"]
    },
    "management": {
        "flights": ["read"],
        "reservations": ["read"],
        "operations": ["read"],
        "users": [],
        "logs": [],
        "management": ["read"]
    }
}

def get_current_user_sync(x_user_id: Optional[str], sql_db: Session) -> Optional[Dict]:
    """Get current user from header - SQL Server"""
    if not x_user_id:
        return None
    
    from sql_helpers import get_user_by_id_sql
    user = get_user_by_id_sql(sql_db, x_user_id)
    return user

def check_permission(resource: str, action: str):
    """Decorator to check if user has permission for an action"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get user from kwargs or headers
            x_user_id = kwargs.get('x_user_id')
            if not x_user_id:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            user = await get_current_user(x_user_id)
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            
            user_role = user.get('role', '')
            
            # Check if user has permission
            if user_role not in PERMISSIONS:
                raise HTTPException(status_code=403, detail="Invalid role")
            
            role_permissions = PERMISSIONS[user_role]
            if resource not in role_permissions or action not in role_permissions[resource]:
                raise HTTPException(
                    status_code=403, 
                    detail=f"You don't have permission to {action} {resource}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# ==================== ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "Diogenes Travel Panel API"}

# ===== FLIGHTS ENDPOINTS =====
@api_router.get("/flights", response_model=List[Flight])
async def get_flights(x_user_id: Optional[str] = Header(None)):
    # Check permission
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'read' not in PERMISSIONS[user_role].get('flights', []):
        raise HTTPException(status_code=403, detail="You don't have permission to view flights")
    
    flights = await db.flights.find({}, {"_id": 0}).to_list(1000)
    for flight in flights:
        if 'created_at' in flight and isinstance(flight['created_at'], str):
            flight['created_at'] = datetime.fromisoformat(flight['created_at'])
        if 'updated_at' in flight and isinstance(flight['updated_at'], str):
            flight['updated_at'] = datetime.fromisoformat(flight['updated_at'])
    return flights

@api_router.post("/flights", response_model=Flight)
async def create_flight(flight: FlightCreate, x_user_id: Optional[str] = Header(None)):
    # Check permission
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'create' not in PERMISSIONS[user_role].get('flights', []):
        raise HTTPException(status_code=403, detail="You don't have permission to create flights")
    
    flight_obj = Flight(**flight.model_dump())
    doc = flight_obj.model_dump(by_alias=True)
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.flights.insert_one(doc)
    
    # Log the action
    await log_action(user.get('email', 'system'), "CREATE", "flights", flight_obj.id, f"Created flight {flight_obj.flightCode}")
    
    return flight_obj

@api_router.put("/flights/{flight_id}", response_model=Flight)
async def update_flight(flight_id: str, flight: FlightCreate, x_user_id: Optional[str] = Header(None)):
    # Check permission
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'update' not in PERMISSIONS[user_role].get('flights', []):
        raise HTTPException(status_code=403, detail="You don't have permission to update flights")
    
    flight_obj = Flight(id=flight_id, **flight.model_dump())
    flight_obj.updated_at = datetime.now(timezone.utc)
    doc = flight_obj.model_dump(by_alias=True)
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.flights.update_one({"id": flight_id}, {"$set": doc})
    
    # Log the action
    await log_action(user.get('email', 'system'), "UPDATE", "flights", flight_id, f"Updated flight {flight_obj.flightCode}")
    
    return flight_obj

@api_router.delete("/flights/{flight_id}")
async def delete_flight(flight_id: str, x_user_id: Optional[str] = Header(None)):
    # Check permission
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'delete' not in PERMISSIONS[user_role].get('flights', []):
        raise HTTPException(status_code=403, detail="You don't have permission to delete flights")
    
    result = await db.flights.delete_one({"id": flight_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    # Log the action
    await log_action(user.get('email', 'system'), "DELETE", "flights", flight_id, f"Deleted flight {flight_id}")
    
    return {"message": "Flight deleted successfully"}

@api_router.post("/flights/upload")
async def upload_flights(file: UploadFile = File(...), x_user_id: Optional[str] = Header(None)):
    """Upload Excel or BAK file to add flights to database"""
    # Check permission
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'upload' not in PERMISSIONS[user_role].get('flights', []):
        raise HTTPException(status_code=403, detail="You don't have permission to upload flights")
    
    try:
        contents = await file.read()
        
        # Read Excel file
        if file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload Excel file.")
        
        # Expected columns: flightCode, airline, from, to, date, time, direction, passengers, hasPNR, pnr
        flights_added = 0
        for _, row in df.iterrows():
            flight_data = {
                "flightCode": str(row.get('flightCode', '')),
                "airline": str(row.get('airline', '')),
                "from": str(row.get('from', '')),
                "to": str(row.get('to', '')),
                "date": str(row.get('date', '')),
                "time": str(row.get('time', '')),
                "direction": str(row.get('direction', 'arrival')),
                "passengers": int(row.get('passengers', 0)),
                "hasPNR": bool(row.get('hasPNR', False)),
                "pnr": str(row.get('pnr', '')),
                "daysUntilFlight": int(row.get('daysUntilFlight', 0))
            }
            
            flight = Flight(**flight_data)
            doc = flight.model_dump(by_alias=True)
            doc['created_at'] = doc['created_at'].isoformat()
            doc['updated_at'] = doc['updated_at'].isoformat()
            
            await db.flights.insert_one(doc)
            flights_added += 1
        
        # Log the action
        await log_action(user.get('email', 'admin'), "IMPORT_EXCEL", "flights", "batch", f"Imported {flights_added} flights from {file.filename}")
        
        return {"message": f"Successfully imported {flights_added} flights", "count": flights_added}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@api_router.post("/flights/compare")
async def compare_flights(file: UploadFile = File(...), x_user_id: Optional[str] = Header(None)):
    """Compare uploaded Excel with database flights"""
    # Check permission
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'read' not in PERMISSIONS[user_role].get('flights', []):
        raise HTTPException(status_code=403, detail="You don't have permission to compare flights")
    
    try:
        contents = await file.read()
        
        if file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Get existing flights
        existing_flights = await db.flights.find({}, {"_id": 0}).to_list(1000)
        existing_codes = {f['flightCode']: f for f in existing_flights}
        
        new_flights = []
        updated_flights = []
        missing_flights = []
        
        # Check uploaded flights
        for _, row in df.iterrows():
            flight_code = str(row.get('flightCode', ''))
            if flight_code in existing_codes:
                # Check for differences
                existing = existing_codes[flight_code]
                if (existing.get('pnr') != str(row.get('pnr', '')) or 
                    existing.get('hasPNR') != bool(row.get('hasPNR', False))):
                    updated_flights.append({
                        "flightCode": flight_code,
                        "oldPNR": existing.get('pnr', ''),
                        "newPNR": str(row.get('pnr', '')),
                        "date": str(row.get('date', ''))
                    })
            else:
                new_flights.append({
                    "flightCode": flight_code,
                    "from": str(row.get('from', '')),
                    "to": str(row.get('to', '')),
                    "date": str(row.get('date', '')),
                    "hasPNR": bool(row.get('hasPNR', False))
                })
        
        # Check for flights in DB but not in upload
        uploaded_codes = set(df['flightCode'].astype(str).tolist())
        for code, flight in existing_codes.items():
            if code not in uploaded_codes:
                missing_flights.append({
                    "flightCode": code,
                    "date": flight.get('date', ''),
                    "from": flight.get('from', ''),
                    "to": flight.get('to', '')
                })
        
        return {
            "summary": {
                "new": len(new_flights),
                "updated": len(updated_flights),
                "missing": len(missing_flights)
            },
            "new_flights": new_flights,
            "updated_flights": updated_flights,
            "missing_flights": missing_flights
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing files: {str(e)}")

# ===== USERS ENDPOINTS =====
@api_router.post("/login", response_model=UserResponse)
async def login(credentials: UserLogin, sql_db: Session = Depends(get_db)):
    """Login with email and password - Using SQL Server"""
    # Find user by email in SQL Server
    user = sql_db.query(SQLUser).filter(SQLUser.email == credentials.email).first()
    
    if not user:
        # Log failed login attempt to MongoDB
        await mongo_db.logs.insert_one({
            "id": str(uuid.uuid4()),
            "user": credentials.email,
            "action": "LOGIN_FAILED",
            "entity": "users",
            "details": "User not found",
            "timestamp": datetime.now(timezone.utc)
        })
        raise HTTPException(status_code=401, detail="Email veya şifre hatalı")
    
    # Verify password
    if not pwd_context.verify(credentials.password, user.password):
        # Log failed login attempt to MongoDB
        await mongo_db.logs.insert_one({
            "id": str(uuid.uuid4()),
            "user": credentials.email,
            "action": "LOGIN_FAILED",
            "entity": "users",
            "details": "Wrong password",
            "timestamp": datetime.now(timezone.utc)
        })
        raise HTTPException(status_code=401, detail="Email veya şifre hatalı")
    
    # Check if user is active
    if user.status != 'active':
        raise HTTPException(status_code=403, detail="Kullanıcı hesabı aktif değil")
    
    # Log successful login to MongoDB
    await mongo_db.logs.insert_one({
        "id": str(uuid.uuid4()),
        "user": user.email,
        "action": "LOGIN_SUCCESS",
        "entity": "users",
        "entityId": user.id,
        "details": f"User {user.email} logged in successfully",
        "timestamp": datetime.now(timezone.utc)
    })
    
    # Return user without password
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "status": user.status,
        "profile_picture": user.profile_picture,
        "created_at": user.created_at
    }

@api_router.get("/users", response_model=List[User])
async def get_users(x_user_id: Optional[str] = Header(None), sql_db: Session = Depends(get_db)):
    # Get users from SQL Server
    try:
        sql_users = sql_db.query(SQLUser).all()
        users = []
        for sql_user in sql_users:
            users.append({
                'id': sql_user.id,
                'name': sql_user.name,
                'email': sql_user.email,
                'password': sql_user.password,
                'role': sql_user.role,
                'status': sql_user.status,
                'profile_picture': sql_user.profile_picture,
                'created_at': sql_user.created_at
            })
        return users
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

@api_router.get("/users/{user_id}/permissions")
async def get_user_permissions(user_id: str):
    """Get permissions for a specific user"""
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_role = user.get('role', '')
    permissions = PERMISSIONS.get(user_role, {})
    
    return {
        "user": user,
        "permissions": permissions
    }

@api_router.post("/users/init")
async def initialize_users():
    """Initialize default users if they don't exist"""
    # Check if users already exist
    existing_count = await db.users.count_documents({})
    if existing_count > 0:
        return {"message": "Users already initialized", "count": existing_count}
    
    default_users = [
        {
            "name": "Admin User",
            "email": "admin@diogenestravel.com",
            "password": pwd_context.hash("admin123"),
            "role": "admin",
            "status": "active"
        },
        {
            "name": "Rezervasyon Manager",
            "email": "reservation@diogenestravel.com",
            "password": pwd_context.hash("reservation123"),
            "role": "reservation",
            "status": "active"
        },
        {
            "name": "Operasyon Manager",
            "email": "operation@diogenestravel.com",
            "password": pwd_context.hash("operation123"),
            "role": "operation",
            "status": "active"
        },
        {
            "name": "Uçak Manager",
            "email": "flight@diogenestravel.com",
            "password": pwd_context.hash("flight123"),
            "role": "flight",
            "status": "active"
        },
        {
            "name": "Yönetim Manager",
            "email": "management@diogenestravel.com",
            "password": pwd_context.hash("management123"),
            "role": "management",
            "status": "active"
        }
    ]
    
    for user_data in default_users:
        user_obj = User(**user_data)
        doc = user_obj.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.users.insert_one(doc)
    
    return {"message": f"Initialized {len(default_users)} users", "count": len(default_users)}

@api_router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, x_user_id: Optional[str] = Header(None)):
    # Check permission - only admin can create users
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = current_user.get('role', '')
    if user_role not in PERMISSIONS or 'create' not in PERMISSIONS[user_role].get('users', []):
        raise HTTPException(status_code=403, detail="You don't have permission to create users")
    
    # Hash password before storing
    user_data = user.model_dump()
    user_data['password'] = pwd_context.hash(user_data['password'])
    
    user_obj = User(**user_data)
    doc = user_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.users.insert_one(doc)
    
    await log_action(current_user.get('email', 'admin'), "CREATE", "users", user_obj.id, f"Created user {user_obj.email}")
    
    return user_obj

@api_router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user: UserCreate, x_user_id: Optional[str] = Header(None)):
    # Check permission - only admin can update users
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = current_user.get('role', '')
    if user_role not in PERMISSIONS or 'update' not in PERMISSIONS[user_role].get('users', []):
        raise HTTPException(status_code=403, detail="You don't have permission to update users")
    
    user_obj = User(id=user_id, **user.model_dump())
    doc = user_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.users.update_one({"id": user_id}, {"$set": doc})
    await log_action(current_user.get('email', 'admin'), "UPDATE", "users", user_id, f"Updated user {user_obj.email}")
    
    return user_obj

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str, x_user_id: Optional[str] = Header(None)):
    # Check permission - only admin can delete users
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = current_user.get('role', '')
    if user_role not in PERMISSIONS or 'delete' not in PERMISSIONS[user_role].get('users', []):
        raise HTTPException(status_code=403, detail="You don't have permission to delete users")
    
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    await log_action(current_user.get('email', 'admin'), "DELETE", "users", user_id, f"Deleted user {user_id}")
    
    return {"message": "User deleted successfully"}

@api_router.patch("/users/{user_id}/profile-picture")
async def update_profile_picture(
    user_id: str, 
    profile_picture: str = Body(..., embed=True),
    x_user_id: Optional[str] = Header(None)
):
    """Update user's profile picture - users can only update their own picture"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Users can only update their own profile picture (except admin can update anyone's)
    if current_user.get('id') != user_id and current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="You can only update your own profile picture")
    
    # Update profile picture
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"profile_picture": profile_picture}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get updated user
    updated_user = await db.users.find_one({"id": user_id})
    if updated_user:
        updated_user['_id'] = str(updated_user['_id'])
        await log_action(current_user.get('email', 'user'), "UPDATE", "users", user_id, "Updated profile picture")
        return {"message": "Profile picture updated successfully", "profile_picture": profile_picture}
    
    raise HTTPException(status_code=500, detail="Failed to update profile picture")


# ===== BACKUP ENDPOINTS =====
@api_router.post("/backup/create")
async def create_backup(x_user_id: Optional[str] = Header(None)):
    """Create a backup of all data"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Only admin can create backups
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Only administrators can create backups")
    
    try:
        # Collect all data
        backup_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
            "users": [],
            "flights": [],
            "reservations": [],
            "operations": [],
            "logs": []
        }
        
        # Get all users
        users = await db.users.find({}, {"_id": 0}).to_list(None)
        for user in users:
            if 'created_at' in user and isinstance(user['created_at'], datetime):
                user['created_at'] = user['created_at'].isoformat()
        backup_data["users"] = users
        
        # Get all flights
        flights = await db.flights.find({}, {"_id": 0}).to_list(None)
        for flight in flights:
            if 'created_at' in flight and isinstance(flight['created_at'], datetime):
                flight['created_at'] = flight['created_at'].isoformat()
        backup_data["flights"] = flights
        
        # Get all reservations
        reservations = await db.reservations.find({}, {"_id": 0}).to_list(None)
        for reservation in reservations:
            if 'created_at' in reservation and isinstance(reservation['created_at'], datetime):
                reservation['created_at'] = reservation['created_at'].isoformat()
        backup_data["reservations"] = reservations
        
        # Get all operations
        operations = await db.operations.find({}, {"_id": 0}).to_list(None)
        for operation in operations:
            if 'created_at' in operation and isinstance(operation['created_at'], datetime):
                operation['created_at'] = operation['created_at'].isoformat()
        backup_data["operations"] = operations
        
        # Get recent logs
        logs = await db.logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(1000).to_list(1000)
        for log in logs:
            if 'timestamp' in log and isinstance(log['timestamp'], datetime):
                log['timestamp'] = log['timestamp'].isoformat()
        backup_data["logs"] = logs
        
        # Convert to JSON
        import json
        backup_json = json.dumps(backup_data, indent=2, ensure_ascii=False)
        
        # Log the action
        await log_action(current_user.get('email', 'admin'), "BACKUP", "system", "full_backup", "Created full system backup")
        
        # Return as file download
        from fastapi.responses import Response
        return Response(
            content=backup_json,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename=diogenes_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup creation failed: {str(e)}")


# ===== LOGS ENDPOINTS =====
@api_router.get("/logs", response_model=List[SystemLog])
async def get_logs(limit: int = 100, x_user_id: Optional[str] = Header(None)):
    # Check permission - only admin can view logs
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'read' not in PERMISSIONS[user_role].get('logs', []):
        raise HTTPException(status_code=403, detail="You don't have permission to view logs")
    
    logs = await db.logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    for log in logs:
        if 'timestamp' in log and isinstance(log['timestamp'], str):
            log['timestamp'] = datetime.fromisoformat(log['timestamp'])
    return logs

# ===== RESERVATIONS ENDPOINTS =====
@api_router.get("/reservations", response_model=List[Reservation])
async def get_reservations(x_user_id: Optional[str] = Header(None)):
    # Check permission
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'read' not in PERMISSIONS[user_role].get('reservations', []):
        raise HTTPException(status_code=403, detail="You don't have permission to view reservations")
    
    reservations = await db.reservations.find({}, {"_id": 0}).to_list(1000)
    for reservation in reservations:
        if 'created_at' in reservation and isinstance(reservation['created_at'], str):
            reservation['created_at'] = datetime.fromisoformat(reservation['created_at'])
    return reservations

@api_router.post("/reservations", response_model=Reservation)
async def create_reservation(reservation: ReservationCreate, x_user_id: Optional[str] = Header(None)):
    # Check permission
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'create' not in PERMISSIONS[user_role].get('reservations', []):
        raise HTTPException(status_code=403, detail="You don't have permission to create reservations")
    
    reservation_obj = Reservation(**reservation.model_dump())
    doc = reservation_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.reservations.insert_one(doc)
    
    await log_action(user.get('email', 'system'), "CREATE", "reservations", reservation_obj.id, f"Created reservation {reservation_obj.voucherNo}")
    
    return reservation_obj

@api_router.post("/reservations/upload")
async def upload_reservations(file: UploadFile = File(...), x_user_id: Optional[str] = Header(None)):
    """Upload Excel file to add reservations to database"""
    # Check permission
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'upload' not in PERMISSIONS[user_role].get('reservations', []):
        raise HTTPException(status_code=403, detail="You don't have permission to upload reservations")
    
    try:
        contents = await file.read()
        
        # Read Excel file
        if file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload Excel file.")
        
        # Expected columns: voucherNo, leader_name, leader_passport, product_code, product_name, hotel, arrivalDate, departureDate, pax, status
        reservations_added = 0
        for _, row in df.iterrows():
            reservation_data = {
                "voucherNo": str(row.get('voucherNo', '')),
                "leader_name": str(row.get('leader_name', '')),
                "leader_passport": str(row.get('leader_passport', '')),
                "product_code": str(row.get('product_code', '')),
                "product_name": str(row.get('product_name', '')),
                "hotel": str(row.get('hotel', '')),
                "arrivalDate": str(row.get('arrivalDate', '')),
                "departureDate": str(row.get('departureDate', '')),
                "pax": int(row.get('pax', 0)),
                "status": str(row.get('status', 'pending'))
            }
            
            reservation = Reservation(**reservation_data)
            doc = reservation.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            
            await db.reservations.insert_one(doc)
            reservations_added += 1
        
        # Log the action
        await log_action(user.get('email', 'admin'), "IMPORT_EXCEL", "reservations", "batch", f"Imported {reservations_added} reservations from {file.filename}")
        
        return {"message": f"Successfully imported {reservations_added} reservations", "count": reservations_added}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# ===== OPERATIONS ENDPOINTS =====
@api_router.get("/operations")
async def get_operations(
    date: Optional[str] = None, 
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    type: str = "all", 
    x_user_id: Optional[str] = Header(None)
):
    """Get operations for a specific date or date range"""
    # Check permission
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'read' not in PERMISSIONS[user_role].get('operations', []):
        raise HTTPException(status_code=403, detail="You don't have permission to view operations")
    
    query = {}
    
    # Handle date filtering - priority: date range > single date
    if start_date and end_date:
        # Date range filtering
        query["date"] = {"$gte": start_date, "$lte": end_date}
    elif date:
        # Single date filtering
        query["date"] = date
    
    if type != "all":
        query["type"] = type
    
    operations = await db.operations.find(query, {"_id": 0}).to_list(1000)
    return operations

@api_router.get("/operations/{operation_id}/details")
async def get_operation_details(operation_id: str, x_user_id: Optional[str] = Header(None)):
    """Get detailed operation information with reservation data"""
    # Check permission
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'read' not in PERMISSIONS[user_role].get('operations', []):
        raise HTTPException(status_code=403, detail="You don't have permission to view operations")
    
    # Get operation
    operation = await db.operations.find_one({"id": operation_id}, {"_id": 0})
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    # Get linked reservation if exists
    reservation = None
    if operation.get('reservationId'):
        reservation = await db.reservations.find_one({"id": operation['reservationId']}, {"_id": 0})
    
    # Combine data
    result = {
        "operation": operation,
        "reservation": reservation,
        "passengers": []
    }
    
    # Add passenger information from reservation
    if reservation:
        result["passengers"] = [{
            "name": reservation.get('leader_name', ''),
            "passport": reservation.get('leader_passport', ''),
            "adults": reservation.get('pax_adults', 0),
            "children": reservation.get('pax_children', 0),
            "infants": reservation.get('pax_infants', 0),
            "total": reservation.get('pax', 0)
        }]
    
    return result

@api_router.post("/operations", response_model=Operation)
async def create_operation(operation: OperationCreate, x_user_id: Optional[str] = Header(None)):
    # Check permission
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'create' not in PERMISSIONS[user_role].get('operations', []):
        raise HTTPException(status_code=403, detail="You don't have permission to create operations")
    
    operation_obj = Operation(**operation.model_dump())
    doc = operation_obj.model_dump(by_alias=True)
    doc['created_at'] = doc['created_at'].isoformat()
    await db.operations.insert_one(doc)
    
    await log_action(user.get('email', 'system'), "CREATE", "operations", operation_obj.id, f"Created operation {operation_obj.flightCode}")
    
    return operation_obj

@api_router.post("/operations/upload")
async def upload_operations(file: UploadFile = File(...), x_user_id: Optional[str] = Header(None)):
    """Upload Excel file to add operations to database"""
    # Check permission
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'upload' not in PERMISSIONS[user_role].get('operations', []):
        raise HTTPException(status_code=403, detail="You don't have permission to upload operations")
    
    try:
        contents = await file.read()
        
        # Read Excel file
        if file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload Excel file.")
        
        # Expected columns: flightCode, type, from, to, date, time, passengers, hotel, transferTime, notes
        operations_added = 0
        for _, row in df.iterrows():
            operation_data = {
                "flightCode": str(row.get('flightCode', '')),
                "type": str(row.get('type', 'transfer')),
                "from": str(row.get('from', '')),
                "to": str(row.get('to', '')),
                "date": str(row.get('date', '')),
                "time": str(row.get('time', '')),
                "passengers": int(row.get('passengers', 0)),
                "hotel": str(row.get('hotel', '')),
                "transferTime": str(row.get('transferTime', '')),
                "notes": str(row.get('notes', ''))
            }
            
            operation = Operation(**operation_data)
            doc = operation.model_dump(by_alias=True)
            doc['created_at'] = doc['created_at'].isoformat()
            
            await db.operations.insert_one(doc)
            operations_added += 1
        
        # Log the action
        await log_action(user.get('email', 'admin'), "IMPORT_EXCEL", "operations", "batch", f"Imported {operations_added} operations from {file.filename}")
        
        return {"message": f"Successfully imported {operations_added} operations", "count": operations_added}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# ===== FLIGHT DETAILS API (RapidAPI Integration) =====
# Simple in-memory cache to minimize API calls
flight_details_cache = {}

@api_router.get("/operations/flight-details/{flight_code}")
async def get_flight_details(flight_code: str, airport_code: str = "IST", x_user_id: Optional[str] = Header(None)):
    """Get real-time flight details from Aerodatabox API"""
    # Check permission
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'read' not in PERMISSIONS[user_role].get('operations', []):
        raise HTTPException(status_code=403, detail="You don't have permission to view flight details")
    
    # Check cache first (cache for 15 minutes)
    cache_key = f"{flight_code}_{airport_code}"
    current_time = datetime.now(timezone.utc)
    
    if cache_key in flight_details_cache:
        cached_data, cached_time = flight_details_cache[cache_key]
        time_diff = (current_time - cached_time).total_seconds()
        if time_diff < 900:  # 15 minutes = 900 seconds
            return cached_data
    
    # Get API credentials from environment
    rapidapi_key = os.environ.get('RAPIDAPI_KEY')
    rapidapi_host = os.environ.get('RAPIDAPI_HOST')
    
    if not rapidapi_key or not rapidapi_host:
        raise HTTPException(status_code=500, detail="Flight API credentials not configured")
    
    try:
        # Call Aerodatabox API to search for flights
        # First, try to get flights from/to the airport
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host
        }
        
        # Query parameters for airport flights
        url = f"https://{rapidapi_host}/flights/number/{flight_code}"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Flight API error: {response.text}")
        
        data = response.json()
        
        # Parse and structure the response
        if not data:
            return {"error": "Flight not found", "flight_code": flight_code}
        
        # Get the most recent flight
        flight_data = data[0] if isinstance(data, list) else data
        
        # Extract comprehensive flight information
        result = {
            "flight_number": flight_data.get('number'),
            "callsign": flight_data.get('callsign', ''),
            "status": flight_data.get('status', 'Unknown'),
            
            # Airline info
            "airline": {
                "name": flight_data.get('airline', {}).get('name', ''),
                "iata": flight_data.get('airline', {}).get('iata', ''),
                "icao": flight_data.get('airline', {}).get('icao', '')
            },
            
            # Aircraft info
            "aircraft": {
                "model": flight_data.get('aircraft', {}).get('model', ''),
                "registration": flight_data.get('aircraft', {}).get('reg', ''),
                "image": flight_data.get('aircraft', {}).get('image', '')
            },
            
            # Departure info
            "departure": {
                "airport": flight_data.get('departure', {}).get('airport', {}).get('name', ''),
                "iata": flight_data.get('departure', {}).get('airport', {}).get('iata', ''),
                "icao": flight_data.get('departure', {}).get('airport', {}).get('icao', ''),
                "terminal": flight_data.get('departure', {}).get('terminal', ''),
                "gate": flight_data.get('departure', {}).get('gate', ''),
                "scheduled_time": flight_data.get('departure', {}).get('scheduledTime', {}).get('local', ''),
                "estimated_time": flight_data.get('departure', {}).get('estimatedTime', {}).get('local', ''),
                "actual_time": flight_data.get('departure', {}).get('actualTime', {}).get('local', ''),
                "delay": flight_data.get('departure', {}).get('delay', 0)
            },
            
            # Arrival info
            "arrival": {
                "airport": flight_data.get('arrival', {}).get('airport', {}).get('name', ''),
                "iata": flight_data.get('arrival', {}).get('airport', {}).get('iata', ''),
                "icao": flight_data.get('arrival', {}).get('airport', {}).get('icao', ''),
                "terminal": flight_data.get('arrival', {}).get('terminal', ''),
                "gate": flight_data.get('arrival', {}).get('gate', ''),
                "baggage": flight_data.get('arrival', {}).get('baggageBelt', ''),
                "scheduled_time": flight_data.get('arrival', {}).get('scheduledTime', {}).get('local', ''),
                "estimated_time": flight_data.get('arrival', {}).get('estimatedTime', {}).get('local', ''),
                "actual_time": flight_data.get('arrival', {}).get('actualTime', {}).get('local', ''),
                "delay": flight_data.get('arrival', {}).get('delay', 0)
            },
            
            # Additional info
            "duration": flight_data.get('duration', {}).get('scheduled', 0),
            "distance": flight_data.get('distance', 0),
            "last_updated": current_time.isoformat()
        }
        
        # Cache the result
        flight_details_cache[cache_key] = (result, current_time)
        
        # Log the action
        await log_action(user.get('email', 'system'), "VIEW", "flight_details", flight_code, f"Viewed flight details for {flight_code}")
        
        return result
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Flight API request timeout")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Flight API connection error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching flight details: {str(e)}")

# ===== SEARCH ENDPOINT (for Management Department) =====
@api_router.get("/search")
async def search_passenger(query: str = Query(..., min_length=2), x_user_id: Optional[str] = Header(None)):
    """Search for passenger across all systems"""
    # Check permission
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'read' not in PERMISSIONS[user_role].get('management', []):
        raise HTTPException(status_code=403, detail="You don't have permission to search across departments")
    
    results = {
        "reservations": [],
        "flights": []
    }
    
    # Search in reservations
    reservations = await db.reservations.find({
        "$or": [
            {"leader_name": {"$regex": query, "$options": "i"}},
            {"leader_passport": {"$regex": query, "$options": "i"}},
            {"voucherNo": {"$regex": query, "$options": "i"}}
        ]
    }, {"_id": 0}).to_list(100)
    
    results["reservations"] = reservations
    
    # Search in flights (by PNR or flight code)
    flights = await db.flights.find({
        "$or": [
            {"pnr": {"$regex": query, "$options": "i"}},
            {"flightCode": {"$regex": query, "$options": "i"}}
        ]
    }, {"_id": 0}).to_list(100)
    
    results["flights"] = flights
    
    return results

# ===== PACKAGE TOUR MANAGEMENT =====

@api_router.get("/packages")
async def get_all_packages(x_user_id: Optional[str] = Header(None)):
    """Get all package tours"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    packages = await db.packages.find({}, {"_id": 0}).to_list(1000)
    return packages

@api_router.get("/packages/{package_id}")
async def get_package(package_id: str, x_user_id: Optional[str] = Header(None)):
    """Get a specific package tour by ID"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    package = await db.packages.find_one({"id": package_id}, {"_id": 0})
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    
    return package

@api_router.post("/packages")
async def create_package(package: PackageCreate, x_user_id: Optional[str] = Header(None)):
    """Create a new package tour"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Only admin can create packages
    if user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Only administrators can create packages")
    
    # Check if package code already exists
    existing = await db.packages.find_one({"package_code": package.package_code})
    if existing:
        raise HTTPException(status_code=400, detail="Package code already exists")
    
    new_package = Package(**package.model_dump())
    doc = new_package.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.packages.insert_one(doc)
    await log_action(user['email'], "CREATE", "packages", new_package.id, f"Created package: {package.package_code}")
    
    return new_package

@api_router.put("/packages/{package_id}")
async def update_package(package_id: str, package: PackageCreate, x_user_id: Optional[str] = Header(None)):
    """Update an existing package tour"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Only admin can update packages
    if user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Only administrators can update packages")
    
    existing = await db.packages.find_one({"id": package_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Package not found")
    
    update_data = package.model_dump()
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.packages.update_one({"id": package_id}, {"$set": update_data})
    await log_action(user['email'], "UPDATE", "packages", package_id, f"Updated package: {package.package_code}")
    
    return {"message": "Package updated successfully"}

@api_router.delete("/packages/{package_id}")
async def delete_package(package_id: str, x_user_id: Optional[str] = Header(None)):
    """Delete a package tour"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Only admin can delete packages
    if user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Only administrators can delete packages")
    
    result = await db.packages.delete_one({"id": package_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Package not found")
    
    await log_action(user['email'], "DELETE", "packages", package_id, "Deleted package")
    
    return {"message": "Package deleted successfully"}

# ===== HOTELS ENDPOINTS =====
@api_router.get("/hotels", response_model=List[Hotel])
async def get_hotels(
    search: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    active_only: bool = True,
    x_user_id: Optional[str] = Header(None)
):
    """Get list of hotels with optional filters"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'read' not in PERMISSIONS[user_role].get('hotels', []):
        raise HTTPException(status_code=403, detail="You don't have permission to view hotels")
    
    # Build query
    query = {}
    if active_only:
        query["active"] = True
    if region:
        query["region"] = region
    if category:
        query["category"] = category
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"code": {"$regex": search, "$options": "i"}},
            {"region": {"$regex": search, "$options": "i"}},
            {"city": {"$regex": search, "$options": "i"}}
        ]
    
    hotels = await db.hotels.find(query, {"_id": 0}).to_list(10000)
    return hotels

@api_router.get("/hotels/{hotel_id}", response_model=Hotel)
async def get_hotel(hotel_id: str, x_user_id: Optional[str] = Header(None)):
    """Get a specific hotel by ID"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'read' not in PERMISSIONS[user_role].get('hotels', []):
        raise HTTPException(status_code=403, detail="You don't have permission to view hotels")
    
    hotel = await db.hotels.find_one({"id": hotel_id}, {"_id": 0})
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    return hotel

@api_router.post("/hotels", response_model=Hotel)
async def create_hotel(hotel: HotelCreate, x_user_id: Optional[str] = Header(None)):
    """Create a new hotel"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'create' not in PERMISSIONS[user_role].get('hotels', []):
        raise HTTPException(status_code=403, detail="You don't have permission to create hotels")
    
    # Check if hotel code already exists
    existing = await db.hotels.find_one({"code": hotel.code})
    if existing:
        raise HTTPException(status_code=400, detail="Hotel code already exists")
    
    new_hotel = Hotel(**hotel.model_dump())
    doc = new_hotel.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.hotels.insert_one(doc)
    await log_action(user['email'], "CREATE", "hotels", new_hotel.id, f"Created hotel: {hotel.name}")
    
    return new_hotel

@api_router.put("/hotels/{hotel_id}")
async def update_hotel(hotel_id: str, hotel: HotelCreate, x_user_id: Optional[str] = Header(None)):
    """Update an existing hotel"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'update' not in PERMISSIONS[user_role].get('hotels', []):
        raise HTTPException(status_code=403, detail="You don't have permission to update hotels")
    
    existing = await db.hotels.find_one({"id": hotel_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    update_data = hotel.model_dump()
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.hotels.update_one({"id": hotel_id}, {"$set": update_data})
    await log_action(user['email'], "UPDATE", "hotels", hotel_id, f"Updated hotel: {hotel.name}")
    
    return {"message": "Hotel updated successfully"}

@api_router.delete("/hotels/{hotel_id}")
async def delete_hotel(hotel_id: str, x_user_id: Optional[str] = Header(None)):
    """Delete a hotel"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'delete' not in PERMISSIONS[user_role].get('hotels', []):
        raise HTTPException(status_code=403, detail="You don't have permission to delete hotels")
    
    result = await db.hotels.delete_one({"id": hotel_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    await log_action(user['email'], "DELETE", "hotels", hotel_id, "Deleted hotel")
    
    return {"message": "Hotel deleted successfully"}

@api_router.post("/hotels/upload")
async def upload_hotels(file: UploadFile = File(...), x_user_id: Optional[str] = Header(None)):
    """Upload Excel file to add hotels to database"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await get_current_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = user.get('role', '')
    if user_role not in PERMISSIONS or 'upload' not in PERMISSIONS[user_role].get('hotels', []):
        raise HTTPException(status_code=403, detail="You don't have permission to upload hotels")
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are supported")
    
    try:
        # Read Excel file
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Excel column mapping (Turkish to English)
        column_mapping = {
            'Otel ': 'code',
            'Adı': 'name',
            'Kategori ': 'category',
            'Bölgesi': 'region',
            'Bölge': 'region_code',
            'Transfer Bölgesi': 'transfer_region',
            'Telefon 1': 'phone1',
            'Telefon 2': 'phone2',
            'Fax ': 'fax',
            'Email ': 'email',
            'EMail 2': 'email2',
            'EMail 3': 'email3',
            'Web ': 'website',
            'Adres': 'address',
            'Adres 2': 'address2',
            'Şehir': 'city',
            'Posta Kodu': 'postal_code',
            'Ülke': 'country',
            'Servis Türü': 'service_type',
            'Yönetici': 'manager',
            'Intern Not': 'notes',
            'Aktif': 'active',
            'Enlem': 'latitude',
            'Boylam': 'longitude',
            'Paximum ID': 'paximum_id',
            'Giata': 'giata'
        }
        
        # Process data
        hotels_added = 0
        hotels_updated = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Extract and clean data
                code = str(row.get('Otel ', '')).strip()
                name = str(row.get('Adı', '')).strip()
                
                if not code or code == 'nan' or not name or name == 'nan':
                    continue
                
                # Extract category and determine stars
                category = str(row.get('Kategori ', 'OTEL')).strip()
                stars = 0
                if 'YILDIZ' in category.upper() or '*' in category:
                    # Try to extract number
                    import re
                    star_match = re.search(r'(\d+)', category)
                    if star_match:
                        stars = int(star_match.group(1))
                
                # Build hotel data
                hotel_data = {
                    'code': code,
                    'name': name,
                    'category': category if category != 'nan' else 'OTEL',
                    'region': str(row.get('Bölgesi', '')).strip() if str(row.get('Bölgesi', '')).strip() != 'nan' else '',
                    'region_code': str(row.get('Bölge', '')).strip() if str(row.get('Bölge', '')).strip() != 'nan' else '',
                    'transfer_region': str(row.get('Transfer Bölgesi', '')).strip() if str(row.get('Transfer Bölgesi', '')).strip() != 'nan' else '',
                    'phone1': str(row.get('Telefon 1', '')).strip() if str(row.get('Telefon 1', '')).strip() != 'nan' else '',
                    'phone2': str(row.get('Telefon 2', '')).strip() if str(row.get('Telefon 2', '')).strip() != 'nan' else '',
                    'fax': str(row.get('Fax ', '')).strip() if str(row.get('Fax ', '')).strip() != 'nan' else '',
                    'email': str(row.get('Email ', '')).strip() if str(row.get('Email ', '')).strip() != 'nan' else '',
                    'email2': str(row.get('EMail 2', '')).strip() if str(row.get('EMail 2', '')).strip() != 'nan' else '',
                    'email3': str(row.get('EMail 3', '')).strip() if str(row.get('EMail 3', '')).strip() != 'nan' else '',
                    'website': str(row.get('Web ', '')).strip() if str(row.get('Web ', '')).strip() != 'nan' else '',
                    'address': str(row.get('Adres', '')).strip() if str(row.get('Adres', '')).strip() != 'nan' else '',
                    'address2': str(row.get('Adres 2', '')).strip() if str(row.get('Adres 2', '')).strip() != 'nan' else '',
                    'city': str(row.get('Şehir', '')).strip() if str(row.get('Şehir', '')).strip() != 'nan' else '',
                    'postal_code': str(row.get('Posta Kodu', '')).strip() if str(row.get('Posta Kodu', '')).strip() != 'nan' else '',
                    'country': str(row.get('Ülke', '')).strip() if str(row.get('Ülke', '')).strip() != 'nan' else '',
                    'service_type': str(row.get('Servis Türü', 'Otel')).strip() if str(row.get('Servis Türü', 'Otel')).strip() != 'nan' else 'Otel',
                    'manager': str(row.get('Yönetici', '')).strip() if str(row.get('Yönetici', '')).strip() != 'nan' else '',
                    'notes': str(row.get('Intern Not', '')).strip() if str(row.get('Intern Not', '')).strip() != 'nan' else '',
                    'active': True if str(row.get('Aktif', 'True')).strip() == 'True' else False,
                    'latitude': float(row.get('Enlem', 0)) if pd.notna(row.get('Enlem')) else 0.0,
                    'longitude': float(row.get('Boylam', 0)) if pd.notna(row.get('Boylam')) else 0.0,
                    'stars': stars,
                    'paximum_id': str(row.get('Paximum ID', '')).strip() if str(row.get('Paximum ID', '')).strip() != 'nan' else '',
                    'giata': str(row.get('Giata', '')).strip() if str(row.get('Giata', '')).strip() != 'nan' else ''
                }
                
                # Check if hotel exists
                existing_hotel = await db.hotels.find_one({"code": code})
                
                if existing_hotel:
                    # Update existing hotel
                    hotel_data['updated_at'] = datetime.now(timezone.utc).isoformat()
                    await db.hotels.update_one({"code": code}, {"$set": hotel_data})
                    hotels_updated += 1
                else:
                    # Create new hotel
                    hotel_data['id'] = str(uuid.uuid4())
                    hotel_data['created_at'] = datetime.now(timezone.utc).isoformat()
                    hotel_data['updated_at'] = datetime.now(timezone.utc).isoformat()
                    await db.hotels.insert_one(hotel_data)
                    hotels_added += 1
                    
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
                continue
        
        # Log the action
        await log_action(
            user['email'], 
            "IMPORT_EXCEL", 
            "hotels", 
            "", 
            f"Imported {hotels_added} new hotels, updated {hotels_updated} hotels from Excel"
        )
        
        result = {
            "message": "Hotels uploaded successfully",
            "hotels_added": hotels_added,
            "hotels_updated": hotels_updated,
            "total_processed": hotels_added + hotels_updated,
            "errors": errors[:10] if errors else []  # Return first 10 errors only
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing Excel file: {str(e)}")

@api_router.get("/reservations/{reservation_id}/journey")
async def get_reservation_journey(reservation_id: str, x_user_id: Optional[str] = Header(None)):
    """Get passenger journey timeline for a multi-leg reservation"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get reservation
    reservation = await db.reservations.find_one({"id": reservation_id}, {"_id": 0})
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    # If no package, return simple single-leg journey
    if not reservation.get('package_id'):
        return {
            "reservation": reservation,
            "package": None,
            "journey": [{
                "step_number": 1,
                "leg_type": "hotel",
                "location": reservation.get('destination', 'N/A'),
                "hotel_name": reservation.get('hotel', 'N/A'),
                "check_in_date": reservation.get('arrivalDate', ''),
                "check_out_date": reservation.get('departureDate', ''),
                "duration_nights": 0,
                "room_type": reservation.get('room_type'),
                "board_type": reservation.get('board_type'),
                "status": "confirmed" if reservation.get('status') == 'confirmed' else "pending"
            }]
        }
    
    # Get package details
    package = await db.packages.find_one({"id": reservation['package_id']}, {"_id": 0})
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    
    # Calculate dates for each leg based on reservation start date
    from datetime import datetime, timedelta
    start_date = datetime.strptime(reservation['arrivalDate'], "%Y-%m-%d")
    
    journey = []
    current_date = start_date
    
    for leg in package.get('legs', []):
        leg_data = leg.copy()
        
        if leg['leg_type'] in ['hotel', 'accommodation']:
            leg_data['check_in_date'] = current_date.strftime("%d.%m.%Y")
            checkout_date = current_date + timedelta(days=leg.get('duration_nights', 0))
            leg_data['check_out_date'] = checkout_date.strftime("%d.%m.%Y")
            current_date = checkout_date
        else:
            # Transfer or other types
            leg_data['check_in_date'] = current_date.strftime("%d.%m.%Y")
            leg_data['check_out_date'] = current_date.strftime("%d.%m.%Y")
        
        # Determine status based on current_leg
        if leg['step_number'] < reservation.get('current_leg', 0):
            leg_data['status'] = 'completed'
        elif leg['step_number'] == reservation.get('current_leg', 0):
            leg_data['status'] = 'in_progress'
        else:
            leg_data['status'] = 'pending'
        
        journey.append(leg_data)
    
    return {
        "reservation": reservation,
        "package": package,
        "journey": journey
    }

@api_router.get("/source-agencies")
async def get_source_agencies():
    """Get list of source agencies"""
    return SOURCE_AGENCIES

# ===== HEALTH CHECK =====
@api_router.get("/health", response_model=HealthStatus)
async def health_check(sql_db: Session = Depends(get_db)):
    try:
        # Count from SQL Server (business data)
        total_flights = sql_db.query(func.count(SQLFlight.id)).scalar()
        total_reservations = sql_db.query(func.count(SQLReservation.id)).scalar()
        total_users = sql_db.query(func.count(SQLUser.id)).scalar()
        
        # Count from MongoDB (logs only)
        total_logs = await mongo_db.logs.count_documents({})
        
        return HealthStatus(
            database="SQL Server + MongoDB (logs)",
            total_flights=total_flights,
            total_reservations=total_reservations,
            total_users=total_users,
            total_logs=total_logs,
            status="healthy"
        )
    except Exception as e:
        return HealthStatus(
            database=f"error: {str(e)}",
            total_flights=0,
            total_reservations=0,
            total_users=0,
            total_logs=0,
            status="unhealthy"
        )


# ===== DATABASE STATUS =====
@api_router.get("/database/status/simple")
async def get_database_status_simple(sql_db: Session = Depends(get_db)):
    """Get simple database connection status (no auth required)"""
    try:
        # SQL Server status
        sql_server_host = os.getenv('SQL_SERVER_HOST', 'N/A')
        sql_server_db = os.getenv('SQL_SERVER_DB', 'N/A')
        
        # Get counts from SQL Server
        users_count = sql_db.query(func.count(SQLUser.id)).scalar()
        flights_count = sql_db.query(func.count(SQLFlight.id)).scalar()
        reservations_count = sql_db.query(func.count(SQLReservation.id)).scalar()
        operations_count = sql_db.query(func.count(SQLOperation.id)).scalar()
        hotels_count = sql_db.query(func.count(SQLHotel.id)).scalar()
        
        total_sql_records = users_count + flights_count + reservations_count + operations_count + hotels_count
        
        # MongoDB status
        mongo_host = os.getenv('MONGO_URL', 'N/A')
        logs_count = await mongo_db.logs.count_documents({})
        
        return {
            "sqlserver": {
                "connected": True,
                "host": sql_server_host,
                "database": sql_server_db,
                "type": "İlişkisel Veritabanı (SQL Server)",
                "records": total_sql_records,
                "breakdown": {
                    "users": users_count,
                    "flights": flights_count,
                    "reservations": reservations_count,
                    "operations": operations_count,
                    "hotels": hotels_count
                },
                "status": "Sistem verilerini SQL Server'da saklıyor"
            },
            "mongodb": {
                "connected": True,
                "host": mongo_host.split('@')[-1] if '@' in mongo_host else mongo_host,
                "database": os.getenv('DB_NAME', 'N/A'),
                "type": "Doküman Veritabanı (MongoDB)",
                "records": logs_count,
                "status": "Sadece log kayıtları için kullanılıyor"
            }
        }
    except Exception as e:
        return {
            "sqlserver": {
                "connected": False,
                "error": str(e)
            },
            "mongodb": {
                "connected": False,
                "error": str(e)
            }
        }

# ===== HELPER FUNCTIONS =====
async def log_action(user: str, action: str, entity: str, entity_id: str, details: str = ""):
    """Log system actions"""
    log = SystemLog(
        user=user,
        action=action,
        entity=entity,
        entityId=entity_id,
        details=details
    )
    doc = log.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.logs.insert_one(doc)

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

@app.on_event("startup")
async def startup_db():
    """Initialize SQL Server tables and users on startup"""
    try:
        # Test SQL Server connection
        print("\n" + "=" * 60)
        print("  SQL SERVER INITIALIZATION")
        print("=" * 60)
        
        if not test_sql_connection():
            print("❌ SQL Server connection failed!")
            return
        
        # Create tables if not exist
        init_sql_db()
        
        # Check if users exist in SQL Server
        sql_db = SessionLocal()
        try:
            users_count = sql_db.query(SQLUser).count()
            
            if users_count == 0:
                print("⚠️  No users found in SQL Server. Initializing default users...")
                
                default_users = [
                    SQLUser(
                        id=str(uuid.uuid4()),
                        name="Admin User",
                        email="admin@diogenestravel.com",
                        password=pwd_context.hash("admin123"),
                        role="admin",
                        status="active",
                        profile_picture=None,
                        created_at=datetime.now(timezone.utc)
                    ),
                    SQLUser(
                        id=str(uuid.uuid4()),
                        name="Reservation Manager",
                        email="reservation@diogenestravel.com",
                        password=pwd_context.hash("reservation123"),
                        role="reservation",
                        status="active",
                        profile_picture=None,
                        created_at=datetime.now(timezone.utc)
                    ),
                    SQLUser(
                        id=str(uuid.uuid4()),
                        name="Operation Manager",
                        email="operation@diogenestravel.com",
                        password=pwd_context.hash("operation123"),
                        role="operation",
                        status="active",
                        profile_picture=None,
                        created_at=datetime.now(timezone.utc)
                    ),
                    SQLUser(
                        id=str(uuid.uuid4()),
                        name="Flight Manager",
                        email="flight@diogenestravel.com",
                        password=pwd_context.hash("flight123"),
                        role="flight",
                        status="active",
                        profile_picture=None,
                        created_at=datetime.now(timezone.utc)
                    ),
                    SQLUser(
                        id=str(uuid.uuid4()),
                        name="Management User",
                        email="management@diogenestravel.com",
                        password=pwd_context.hash("management123"),
                        role="management",
                        status="active",
                        profile_picture=None,
                        created_at=datetime.now(timezone.utc)
                    )
                ]
                
                sql_db.add_all(default_users)
                sql_db.commit()
                print(f"✅ Successfully initialized {len(default_users)} default users in SQL Server")
            else:
                print(f"ℹ️  Found {users_count} users in SQL Server")
        finally:
            sql_db.close()
            
    except Exception as e:
        print(f"❌ Error during startup initialization: {e}")
        import traceback
        traceback.print_exc()

# ==================== DATABASE RESTORE ENDPOINTS ====================

from restore_service import (
    start_restore, check_restore_status, wait_for_restore,
    list_databases, get_database_tables, get_table_schema
)

@api_router.post("/database/restore")
async def restore_database(
    s3_key: str = Body(..., embed=True),
    target_db_name: str = Body(default='DIOGENESSEJOUR', embed=True),
    wait_for_completion: bool = Body(default=True, embed=True),
    x_user_id: Optional[str] = Header(None)
):
    """
    Restore database from S3 .bak file
    
    Args:
        s3_key: S3 object key (e.g., 'sql-backups/DIOGENESSEJOUR_26_02.bak')
        target_db_name: Target database name (default: DIOGENESSEJOUR)
        wait_for_completion: Wait for restore to complete before returning (default: True)
    """
    # Check permission - only admin can restore database
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = current_user.get('role', '')
    if user_role != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can restore database")
    
    # Start restore
    result = start_restore(s3_key, target_db_name)
    
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('message', 'Restore failed'))
    
    task_id = result.get('task_id')
    
    # Wait for completion if requested
    if wait_for_completion and task_id:
        wait_result = wait_for_restore(task_id, timeout=1200)  # 20 minutes timeout
        
        return {
            "message": "Restore process completed",
            "restore_start": result,
            "restore_completion": wait_result,
            "database_name": target_db_name
        }
    else:
        return {
            "message": "Restore process started",
            "task_id": task_id,
            "restore_info": result,
            "database_name": target_db_name,
            "note": "Use /api/database/restore/status endpoint to check progress"
        }


@api_router.get("/database/restore/status")
async def get_restore_status(
    task_id: Optional[int] = Query(None),
    x_user_id: Optional[str] = Header(None)
):
    """
    Check restore task status
    
    Args:
        task_id: Optional task ID to check specific task
    """
    # Check permission - only admin can check restore status
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = current_user.get('role', '')
    if user_role != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can check restore status")
    
    result = check_restore_status(task_id)
    
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('message', 'Failed to get status'))
    
    return result


@api_router.get("/database/list")
async def list_all_databases(x_user_id: Optional[str] = Header(None)):
    """List all databases on SQL Server"""
    # Check permission - only admin can list databases
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = current_user.get('role', '')
    if user_role != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can list databases")
    
    result = list_databases()
    
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('message', 'Failed to list databases'))
    
    return result


@api_router.get("/database/{database_name}/tables")
async def get_tables(database_name: str, x_user_id: Optional[str] = Header(None)):
    """Get all tables in a database"""
    # Check permission - only admin can view database tables
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = current_user.get('role', '')
    if user_role != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can view database tables")
    
    result = get_database_tables(database_name)
    
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('message', 'Failed to get tables'))
    
    return result


@api_router.get("/database/{database_name}/tables/{table_name}/schema")
async def get_schema(
    database_name: str,
    table_name: str,
    schema_name: str = Query(default='dbo'),
    x_user_id: Optional[str] = Header(None)
):
    """Get detailed schema for a table"""
    # Check permission - only admin can view table schema
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_role = current_user.get('role', '')
    if user_role != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can view table schema")
    
    result = get_table_schema(database_name, table_name, schema_name)
    
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('message', 'Failed to get table schema'))
    
    return result


# ==================== DIOGENESSEJOUR DATABASE ENDPOINTS ====================

from diogenes_service import (
    get_customers, get_hotels, get_hotel_regions,
    get_reservations, get_operations, get_reservation_details,
    test_diogenes_connection
)

@api_router.get("/diogenes/test")
async def test_diogenes_db(x_user_id: Optional[str] = Header(None)):
    """Test DIOGENESSEJOUR database connection"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    try:
        is_connected = test_diogenes_connection()
        return {
            "success": is_connected,
            "message": "DIOGENESSEJOUR database connection successful" if is_connected else "Connection failed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")


@api_router.get("/diogenes/customers")
async def get_diogenes_customers(
    limit: int = Query(default=100000, ge=1, le=100000),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = Query(default=None),
    x_user_id: Optional[str] = Header(None)
):
    """
    Get customers from DIOGENESSEJOUR database (Musteri table)
    
    Query params:
        - limit: Number of records per page (default: 100000 - tüm kayıtlar)
        - offset: Offset for pagination (default: 0)
        - search: Search term for name/title
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Permission check
    user_role = current_user.get('role', '')
    if not check_permission(user_role, "reservations", "read"):
        raise HTTPException(status_code=403, detail="No permission to view customers")
    
    try:
        result = get_customers(limit=limit, offset=offset, search=search)
        return result
    except Exception as e:
        logger.error(f"Error in get_diogenes_customers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch customers: {str(e)}")


@api_router.get("/diogenes/hotels")
async def get_diogenes_hotels(
    limit: int = Query(default=100000, ge=1, le=100000),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = Query(default=None),
    region: Optional[str] = Query(default=None),
    x_user_id: Optional[str] = Header(None)
):
    """
    Get hotels from DIOGENESSEJOUR database (Otel table)
    
    Query params:
        - limit: Number of records per page (default: 100000 - tüm kayıtlar)
        - offset: Offset for pagination (default: 0)
        - search: Search term for hotel name
        - region: Filter by region
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Permission check
    user_role = current_user.get('role', '')
    if not check_permission(user_role, "hotels", "read"):
        raise HTTPException(status_code=403, detail="No permission to view hotels")
    
    try:
        result = get_hotels(limit=limit, offset=offset, search=search, region=region)
        return result
    except Exception as e:
        logger.error(f"Error in get_diogenes_hotels: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch hotels: {str(e)}")


@api_router.get("/diogenes/hotels/regions")
async def get_diogenes_hotel_regions(x_user_id: Optional[str] = Header(None)):
    """Get all hotel regions from DIOGENESSEJOUR database"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    try:
        regions = get_hotel_regions()
        return {"regions": regions}
    except Exception as e:
        logger.error(f"Error in get_diogenes_hotel_regions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch regions: {str(e)}")


@api_router.get("/diogenes/reservations")
async def get_diogenes_reservations(
    limit: int = Query(default=100000, ge=1, le=100000),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = Query(default=None),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    x_user_id: Optional[str] = Header(None)
):
    """
    Get reservations from DIOGENESSEJOUR database (MusteriOpr + Musteri tables)
    
    Query params:
        - limit: Number of records per page (default: 100000 - tüm kayıtlar)
        - offset: Offset for pagination (default: 0)
        - search: Search term for voucher/tour operator
        - date_from: Filter by check-in date (YYYY-MM-DD)
        - date_to: Filter by check-in date (YYYY-MM-DD)
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Permission check
    user_role = current_user.get('role', '')
    if not check_permission(user_role, "reservations", "read"):
        raise HTTPException(status_code=403, detail="No permission to view reservations")
    
    try:
        result = get_reservations(
            limit=limit, 
            offset=offset, 
            search=search,
            date_from=date_from,
            date_to=date_to
        )
        return result
    except Exception as e:
        logger.error(f"Error in get_diogenes_reservations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch reservations: {str(e)}")


@api_router.get("/diogenes/operations")
async def get_diogenes_operations(
    limit: int = Query(default=100000, ge=1, le=100000),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = Query(default=None),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    operation_type: Optional[str] = Query(default=None),
    x_user_id: Optional[str] = Header(None)
):
    """
    Get operations from DIOGENESSEJOUR database (MusteriOpr table)
    
    Query params:
        - limit: Number of records per page (default: 100000 - tüm kayıtlar)
        - offset: Offset for pagination (default: 0)
        - search: Search term for voucher
        - date_from: Filter by operation date (YYYY-MM-DD)
        - date_to: Filter by operation date (YYYY-MM-DD)
        - operation_type: Filter by operation type
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Permission check
    user_role = current_user.get('role', '')
    if not check_permission(user_role, "operations", "read"):
        raise HTTPException(status_code=403, detail="No permission to view operations")
    
    try:
        result = get_operations(
            limit=limit,
            offset=offset,
            search=search,
            date_from=date_from,
            date_to=date_to,
            operation_type=operation_type
        )
        return result
    except Exception as e:
        logger.error(f"Error in get_diogenes_operations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch operations: {str(e)}")


@api_router.get("/diogenes/reservations/{voucher}/{tour_operator}")
async def get_diogenes_reservation_details(
    voucher: str,
    tour_operator: str,
    x_user_id: Optional[str] = Header(None)
):
    """
    Get detailed reservation info including passenger list
    
    Path params:
        - voucher: Voucher number
        - tour_operator: Tour operator code
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Permission check
    user_role = current_user.get('role', '')
    if not check_permission(user_role, "reservations", "read"):
        raise HTTPException(status_code=403, detail="No permission to view reservation details")
    
    try:
        result = get_reservation_details(voucher, tour_operator)
        if not result:
            raise HTTPException(status_code=404, detail="Reservation not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_diogenes_reservation_details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch reservation details: {str(e)}")



# ==================== ADMIN PANEL ENDPOINTS ====================

@api_router.get("/database/status")
async def get_database_status(x_user_id: Optional[str] = Header(None), sql_db: Session = Depends(get_db)):
    """
    Get comprehensive database status including SQL Server and MongoDB statistics (Admin only)
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check admin permission
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # SQL Server statistics from diogenesDB
        sqlserver_status = {
            'connected': False,
            'records': 0,
            'host': os.environ.get('SQL_SERVER_HOST', 'N/A'),
            'database': os.environ.get('SQL_SERVER_DB', 'diogenesDB'),
            'type': 'İlişkisel Veritabanı (SQL Server)',
            'status': 'Bağlantı kontrol ediliyor...',
            'tables': {},
            'total_operations': 0,
            'total_customers': 0,
            'total_hotels': 0
        }
        
        try:
            # Get counts from SQL Server using SQLAlchemy
            users_count = sql_db.query(func.count(SQLUser.id)).scalar()
            flights_count = sql_db.query(func.count(SQLFlight.id)).scalar()
            reservations_count = sql_db.query(func.count(SQLReservation.id)).scalar()
            operations_count = sql_db.query(func.count(SQLOperation.id)).scalar()
            hotels_count = sql_db.query(func.count(SQLHotel.id)).scalar()
            packages_count = sql_db.query(func.count(SQLPackage.id)).scalar()
            
            # Get total records
            total_records = users_count + flights_count + reservations_count + operations_count + hotels_count + packages_count
            
            sqlserver_status.update({
                'connected': True,
                'records': total_records,
                'status': f'✅ Bağlı ve aktif ({total_records:,} toplam kayıt)',
                'tables': {
                    'users': users_count,
                    'flights': flights_count,
                    'reservations': reservations_count,
                    'operations': operations_count,
                    'hotels': hotels_count,
                    'packages': packages_count
                },
                'total_operations': operations_count,
                'total_customers': reservations_count,  # Using reservations as customers proxy
                'total_hotels': hotels_count
            })
        except Exception as e:
            logger.error(f"SQL Server status check failed: {e}")
            sqlserver_status['status'] = f'❌ Hata: {str(e)}'
        
        # MongoDB statistics (for logs only)
        mongodb_status = {
            'connected': False,
            'records': 0,
            'host': os.environ.get('MONGO_URL', 'N/A').split('@')[-1] if '@' in os.environ.get('MONGO_URL', '') else 'localhost:27017',
            'database': os.environ.get('DB_NAME', 'test_database'),
            'type': 'Doküman Veritabanı (MongoDB - Sadece Loglar)',
            'status': 'Bağlantı kontrol ediliyor...'
        }
        
        try:
            # Test MongoDB connection
            await mongo_db.command('ping')
            
            # Get logs count
            logs_count = await mongo_db.logs.count_documents({})
            
            mongodb_status.update({
                'connected': True,
                'records': logs_count,
                'status': f'✅ Bağlı ve aktif ({logs_count} log kaydı)'
            })
        except Exception as e:
            logger.error(f"MongoDB status check failed: {e}")
            mongodb_status.update({
                'status': f'⚠️ Log servisi: {str(e)}'
            })
        
        return {
            'sqlserver': sqlserver_status,
            'mongodb': mongodb_status
        }
        
    except Exception as e:
        logger.error(f"Error in get_database_status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch database status: {str(e)}")


@api_router.get("/admin/statistics")
async def get_admin_statistics(x_user_id: Optional[str] = Header(None), sql_db: Session = Depends(get_db)):
    """
    Get comprehensive statistics for admin dashboard
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check admin permission
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Get various statistics from diogenesDB using SQLAlchemy
        stats = {
            'total_operations': 0,
            'total_customers': 0,
            'total_hotels': 0,
            'active_reservations': 0,
            'total_passengers': 0,
            'hotels_by_region': [],
            'operations_by_date': [],
            'recent_reservations': []
        }
        
        # Total operations
        stats['total_operations'] = sql_db.query(func.count(SQLOperation.id)).scalar()
        
        # Total customers (using reservations as proxy)
        stats['total_customers'] = sql_db.query(func.count(SQLReservation.id)).scalar()
        
        # Total hotels
        stats['total_hotels'] = sql_db.query(func.count(SQLHotel.id)).scalar()
        
        # Active reservations (with future check-in dates)
        from datetime import date
        stats['active_reservations'] = sql_db.query(func.count(SQLReservation.id)).filter(
            SQLReservation.check_in_date >= date.today()
        ).scalar()
        
        # Total passengers
        total_pax = sql_db.query(func.sum(SQLReservation.pax)).scalar()
        stats['total_passengers'] = int(total_pax) if total_pax else 0
        
        # Hotels by region (top 10)
        hotel_regions = sql_db.query(
            SQLHotel.region,
            func.count(SQLHotel.id).label('count')
        ).filter(
            SQLHotel.region.isnot(None),
            SQLHotel.region != ''
        ).group_by(SQLHotel.region).order_by(func.count(SQLHotel.id).desc()).limit(10).all()
        
        stats['hotels_by_region'] = [
            {'region': region, 'count': count}
            for region, count in hotel_regions
        ]
        
        # Operations by date (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        operations_by_date = sql_db.query(
            func.date(SQLOperation.date).label('date'),
            func.count(SQLOperation.id).label('count')
        ).filter(
            SQLOperation.date >= thirty_days_ago
        ).group_by(func.date(SQLOperation.date)).order_by(func.date(SQLOperation.date).desc()).limit(30).all()
        
        stats['operations_by_date'] = [
            {
                'date': op_date.strftime('%Y-%m-%d') if op_date else '',
                'count': count
            }
            for op_date, count in operations_by_date
        ]
        
        # Recent reservations (last 10)
        recent_reservations = sql_db.query(SQLReservation).order_by(SQLReservation.check_in_date.desc()).limit(10).all()
        
        stats['recent_reservations'] = [
            {
                'voucher': res.id[:8] if res.id else 'N/A',
                'tourOperator': 'N/A',
                'checkInDate': res.check_in_date.strftime('%Y-%m-%d') if res.check_in_date else '',
                'customerName': res.passenger_name or 'N/A',
                'paxCount': res.pax or 0
            }
            for res in recent_reservations
        ]
        
        return stats
        
    except Exception as e:
        logger.error(f"Error in get_admin_statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {str(e)}")


@api_router.get("/admin/packages")
async def get_admin_packages(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = Query(default=None),
    x_user_id: Optional[str] = Header(None),
    sql_db: Session = Depends(get_db)
):
    """
    Get tour packages from diogenesDB database (packages table)
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_user = await get_current_user(x_user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check admin permission
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Build query
        query = sql_db.query(SQLPackage)
        
        # Apply search filter
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (SQLPackage.hotel_code.like(search_pattern)) | 
                (SQLPackage.description.like(search_pattern))
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        packages = query.order_by(SQLPackage.check_in_date.desc()).offset(offset).limit(limit).all()
        
        # Map to response format
        mapped_packages = []
        for pkg in packages:
            mapped_packages.append({
                'id': pkg.id,
                'hotelCode': pkg.hotel_code or '',
                'checkIn': pkg.check_in_date.strftime('%Y-%m-%d') if pkg.check_in_date else '',
                'checkOut': pkg.check_out_date.strftime('%Y-%m-%d') if pkg.check_out_date else '',
                'description': pkg.description or '',
                'packageCode': pkg.package_code or '',
                'tourOperator': pkg.tour_operator or ''
            })
        
        return {
            'packages': mapped_packages,
            'total': total,
            'limit': limit,
            'offset': offset
        }
        
    except Exception as e:
        logger.error(f"Error in get_admin_packages: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch packages: {str(e)}")




@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()