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


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

async def get_current_user(x_user_id: Optional[str] = Header(None)) -> Optional[Dict]:
    """Get current user from header"""
    if not x_user_id:
        return None
    
    user = await db.users.find_one({"id": x_user_id}, {"_id": 0})
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
async def login(credentials: UserLogin):
    """Login with email and password"""
    # Find user by email
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Email veya şifre hatalı")
    
    # Verify password
    if not pwd_context.verify(credentials.password, user.get('password', '')):
        raise HTTPException(status_code=401, detail="Email veya şifre hatalı")
    
    # Check if user is active
    if user.get('status') != 'active':
        raise HTTPException(status_code=403, detail="Kullanıcı hesabı aktif değil")
    
    # Convert created_at if needed
    if 'created_at' in user and isinstance(user['created_at'], str):
        user['created_at'] = datetime.fromisoformat(user['created_at'])
    
    # Return user without password
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "status": user["status"],
        "created_at": user["created_at"]
    }

@api_router.get("/users", response_model=List[User])
async def get_users(x_user_id: Optional[str] = Header(None)):
    # For login dropdown - allow unauthenticated access
    # In production, this should be protected or return limited info
    users = await db.users.find({}, {"_id": 0}).to_list(1000)
    for user in users:
        if 'created_at' in user and isinstance(user['created_at'], str):
            user['created_at'] = datetime.fromisoformat(user['created_at'])
    return users

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
async def health_check():
    try:
        # Count documents in collections
        total_flights = await db.flights.count_documents({})
        total_reservations = await db.reservations.count_documents({})
        total_users = await db.users.count_documents({})
        total_logs = await db.logs.count_documents({})
        
        return HealthStatus(
            database="connected",
            total_flights=total_flights,
            total_reservations=total_reservations,
            total_users=total_users,
            total_logs=total_logs,
            status="healthy"
        )
    except Exception:
        return HealthStatus(
            database="error",
            total_flights=0,
            total_reservations=0,
            total_users=0,
            total_logs=0,
            status="unhealthy"
        )

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
    """Initialize users on startup if database is empty"""
    try:
        users_count = await db.users.count_documents({})
        if users_count == 0:
            print("⚠️  No users found in database. Initializing default users...")
            
            default_users = [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Admin User",
                    "email": "admin@diogenestravel.com",
                    "password": pwd_context.hash("admin123"),
                    "role": "admin",
                    "status": "active",
                    "profile_picture": None,
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Reservation Manager",
                    "email": "reservation@diogenestravel.com",
                    "password": pwd_context.hash("reservation123"),
                    "role": "reservation",
                    "status": "active",
                    "profile_picture": None,
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Operation Manager",
                    "email": "operation@diogenestravel.com",
                    "password": pwd_context.hash("operation123"),
                    "role": "operation",
                    "status": "active",
                    "profile_picture": None,
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Flight Manager",
                    "email": "flight@diogenestravel.com",
                    "password": pwd_context.hash("flight123"),
                    "role": "flight",
                    "status": "active",
                    "profile_picture": None,
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Management User",
                    "email": "management@diogenestravel.com",
                    "password": pwd_context.hash("management123"),
                    "role": "management",
                    "status": "active",
                    "profile_picture": None,
                    "created_at": datetime.now(timezone.utc)
                }
            ]
            
            await db.users.insert_many(default_users)
            print(f"✅ Successfully initialized {len(default_users)} default users")
        else:
            print(f"ℹ️  Found {users_count} users in database")
    except Exception as e:
        print(f"❌ Error during startup initialization: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()