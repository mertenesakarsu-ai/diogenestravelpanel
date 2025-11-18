from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Query, Header, Depends
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

# Operation Models
class Operation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    flightCode: str
    type: str  # "transfer", "tour", etc.
    from_location: str = Field(alias="from")
    to: str
    date: str
    time: str
    passengers: int = 0
    hotel: str = ""
    transferTime: str = ""
    notes: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OperationCreate(BaseModel):
    flightCode: str
    type: str
    from_location: str = Field(alias="from")
    to: str
    date: str
    time: str
    passengers: int = 0
    hotel: str = ""
    transferTime: str = ""
    notes: str = ""

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
        "reservations": [],
        "operations": [],
        "users": [],
        "logs": [],
        "management": []
    },
    "reservation": {
        "flights": [],
        "reservations": ["read", "create", "update", "delete", "upload"],
        "operations": [],
        "users": [],
        "logs": [],
        "management": []
    },
    "operation": {
        "flights": [],
        "reservations": [],
        "operations": ["read", "create", "update", "delete", "upload"],
        "users": [],
        "logs": [],
        "management": []
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
async def compare_flights(file: UploadFile = File(...)):
    """Compare uploaded Excel with database flights"""
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
@api_router.get("/users", response_model=List[User])
async def get_users():
    users = await db.users.find({}, {"_id": 0}).to_list(1000)
    for user in users:
        if 'created_at' in user and isinstance(user['created_at'], str):
            user['created_at'] = datetime.fromisoformat(user['created_at'])
    return users

@api_router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    user_obj = User(**user.model_dump())
    doc = user_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.users.insert_one(doc)
    
    await log_action("admin", "CREATE", "users", user_obj.id, f"Created user {user_obj.email}")
    
    return user_obj

@api_router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user: UserCreate):
    user_obj = User(id=user_id, **user.model_dump())
    doc = user_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.users.update_one({"id": user_id}, {"$set": doc})
    await log_action("admin", "UPDATE", "users", user_id, f"Updated user {user_obj.email}")
    
    return user_obj

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    await log_action("admin", "DELETE", "users", user_id, f"Deleted user {user_id}")
    
    return {"message": "User deleted successfully"}

# ===== LOGS ENDPOINTS =====
@api_router.get("/logs", response_model=List[SystemLog])
async def get_logs(limit: int = 100):
    logs = await db.logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    for log in logs:
        if 'timestamp' in log and isinstance(log['timestamp'], str):
            log['timestamp'] = datetime.fromisoformat(log['timestamp'])
    return logs

# ===== RESERVATIONS ENDPOINTS =====
@api_router.get("/reservations", response_model=List[Reservation])
async def get_reservations():
    reservations = await db.reservations.find({}, {"_id": 0}).to_list(1000)
    for reservation in reservations:
        if 'created_at' in reservation and isinstance(reservation['created_at'], str):
            reservation['created_at'] = datetime.fromisoformat(reservation['created_at'])
    return reservations

@api_router.post("/reservations", response_model=Reservation)
async def create_reservation(reservation: ReservationCreate):
    reservation_obj = Reservation(**reservation.model_dump())
    doc = reservation_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.reservations.insert_one(doc)
    
    await log_action("system", "CREATE", "reservations", reservation_obj.id, f"Created reservation {reservation_obj.voucherNo}")
    
    return reservation_obj

@api_router.post("/reservations/upload")
async def upload_reservations(file: UploadFile = File(...)):
    """Upload Excel file to add reservations to database"""
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
        await log_action("admin", "IMPORT_EXCEL", "reservations", "batch", f"Imported {reservations_added} reservations from {file.filename}")
        
        return {"message": f"Successfully imported {reservations_added} reservations", "count": reservations_added}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# ===== OPERATIONS ENDPOINTS =====
@api_router.get("/operations")
async def get_operations(date: Optional[str] = None, type: str = "all"):
    """Get operations for a specific date"""
    query = {}
    
    if date:
        query["date"] = date
    
    if type != "all":
        query["type"] = type
    
    operations = await db.operations.find(query, {"_id": 0}).to_list(1000)
    return operations

@api_router.post("/operations", response_model=Operation)
async def create_operation(operation: OperationCreate):
    operation_obj = Operation(**operation.model_dump())
    doc = operation_obj.model_dump(by_alias=True)
    doc['created_at'] = doc['created_at'].isoformat()
    await db.operations.insert_one(doc)
    
    await log_action("system", "CREATE", "operations", operation_obj.id, f"Created operation {operation_obj.flightCode}")
    
    return operation_obj

@api_router.post("/operations/upload")
async def upload_operations(file: UploadFile = File(...)):
    """Upload Excel file to add operations to database"""
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
        await log_action("admin", "IMPORT_EXCEL", "operations", "batch", f"Imported {operations_added} operations from {file.filename}")
        
        return {"message": f"Successfully imported {operations_added} operations", "count": operations_added}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# ===== SEARCH ENDPOINT (for Management Department) =====
@api_router.get("/search")
async def search_passenger(query: str = Query(..., min_length=2)):
    """Search for passenger across all systems"""
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
    except Exception as e:
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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()