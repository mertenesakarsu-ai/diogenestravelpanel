"""
SQL Server Models using SQLAlchemy ORM
All business/operational data is stored in SQL Server
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# SQL Server connection string
SQL_SERVER_HOST = os.environ['SQL_SERVER_HOST']
SQL_SERVER_PORT = os.environ['SQL_SERVER_PORT']
SQL_SERVER_DB = os.environ['SQL_SERVER_DB']
SQL_SERVER_USER = os.environ['SQL_SERVER_USER']
SQL_SERVER_PASSWORD = os.environ['SQL_SERVER_PASSWORD']

# SQLAlchemy connection string for SQL Server
# Format: mssql+pymssql://user:password@host:port/database
connection_string = f"mssql+pymssql://{SQL_SERVER_USER}:{SQL_SERVER_PASSWORD}@{SQL_SERVER_HOST}:{SQL_SERVER_PORT}/{SQL_SERVER_DB}"

# Create engine
engine = create_engine(
    connection_string,
    echo=False,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# ==================== SQL SERVER MODELS ====================

class SQLUser(Base):
    """User model for SQL Server"""
    __tablename__ = "users"
    
    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password = Column(String(200), nullable=False)  # hashed password
    role = Column(String(50), nullable=False)  # admin, reservation, operation, flight, management
    status = Column(String(50), default="active")  # active, inactive
    profile_picture = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SQLFlight(Base):
    """Flight model for SQL Server"""
    __tablename__ = "flights"
    
    id = Column(String(100), primary_key=True)
    flightCode = Column(String(50), nullable=False, index=True)
    airline = Column(String(100), default="")
    from_location = Column(String(100), nullable=False)
    to = Column(String(100), nullable=False)
    date = Column(String(20), nullable=False)
    time = Column(String(20), nullable=False)
    direction = Column(String(20), nullable=False)  # arrival or departure
    passengers = Column(Integer, default=0)
    hasPNR = Column(Boolean, default=False)
    pnr = Column(String(50), default="")
    daysUntilFlight = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class SQLReservation(Base):
    """Reservation model for SQL Server"""
    __tablename__ = "reservations"
    
    id = Column(String(100), primary_key=True)
    voucherNo = Column(String(100), nullable=False, unique=True, index=True)
    leader_name = Column(String(200), nullable=False)
    leader_passport = Column(String(100), nullable=False)
    product_code = Column(String(100), nullable=False)
    product_name = Column(String(200), nullable=False)
    hotel = Column(String(200), nullable=False)
    arrivalDate = Column(String(20), nullable=False)
    departureDate = Column(String(20), nullable=False)
    pax = Column(Integer, nullable=False)
    pax_adults = Column(Integer, default=0)
    pax_children = Column(Integer, default=0)
    pax_infants = Column(Integer, default=0)
    status = Column(String(50), nullable=False)  # confirmed, pending, cancelled
    source_agency = Column(String(100), default="THV")
    package_id = Column(String(100), nullable=True)
    current_leg = Column(Integer, default=0)
    room_type = Column(String(100), nullable=True)
    board_type = Column(String(100), nullable=True)
    destination = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class SQLOperation(Base):
    """Operation model for SQL Server"""
    __tablename__ = "operations"
    
    id = Column(String(100), primary_key=True)
    reservationId = Column(String(100), nullable=True)
    voucherNo = Column(String(100), default="", index=True)
    
    # Flight Information (stored as JSON strings)
    arrivalFlight = Column(Text, nullable=True)  # JSON string
    returnFlight = Column(Text, nullable=True)   # JSON string
    transferFlight = Column(Text, nullable=True)  # JSON string
    
    # Hotel Information
    currentHotel = Column(String(200), default="")
    hotelCheckIn = Column(String(50), default="")
    hotelCheckOut = Column(String(50), default="")
    
    # Legacy fields
    flightCode = Column(String(50), default="")
    type = Column(String(50), default="")
    from_location = Column(String(100), default="")
    to = Column(String(100), default="")
    date = Column(String(20), default="")
    time = Column(String(20), default="")
    passengers = Column(Integer, default=0)
    hotel = Column(String(200), default="")
    transferTime = Column(String(20), default="")
    notes = Column(Text, default="")
    status = Column(String(50), default="scheduled")
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class SQLHotel(Base):
    """Hotel model for SQL Server"""
    __tablename__ = "hotels"
    
    id = Column(String(100), primary_key=True)
    code = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), default="")
    region = Column(String(100), default="")
    region_code = Column(String(50), default="")
    transfer_region = Column(String(100), default="")
    phone1 = Column(String(50), default="")
    phone2 = Column(String(50), default="")
    fax = Column(String(50), default="")
    email = Column(String(200), default="")
    email2 = Column(String(200), default="")
    email3 = Column(String(200), default="")
    website = Column(String(200), default="")
    address = Column(Text, default="")
    address2 = Column(Text, default="")
    city = Column(String(100), default="")
    postal_code = Column(String(20), default="")
    country = Column(String(100), default="")
    service_type = Column(String(50), default="Otel")
    manager = Column(String(200), default="")
    notes = Column(Text, default="")
    active = Column(Boolean, default=True)
    latitude = Column(Float, default=0.0)
    longitude = Column(Float, default=0.0)
    stars = Column(Integer, default=0)
    paximum_id = Column(String(100), default="")
    giata = Column(String(100), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class SQLPackageLeg(Base):
    """Package Leg model for SQL Server"""
    __tablename__ = "package_legs"
    
    id = Column(String(100), primary_key=True)
    package_id = Column(String(100), ForeignKey('packages.id'), nullable=False)
    step_number = Column(Integer, nullable=False)
    leg_type = Column(String(50), nullable=False)  # hotel, transfer, airport_pickup, airport_dropoff
    location = Column(String(200), nullable=False)
    hotel_name = Column(String(200), nullable=True)
    hotel_stars = Column(Integer, nullable=True)
    check_in_date = Column(String(20), nullable=True)
    check_out_date = Column(String(20), nullable=True)
    duration_nights = Column(Integer, default=0)
    room_type = Column(String(100), nullable=True)
    board_type = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)


class SQLPackage(Base):
    """Package Tour model for SQL Server"""
    __tablename__ = "packages"
    
    id = Column(String(100), primary_key=True)
    package_code = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    total_nights = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationship to legs
    legs = relationship("SQLPackageLeg", backref="package", cascade="all, delete-orphan")


# ==================== DATABASE INITIALIZATION ====================

def init_sql_db():
    """Create all tables in SQL Server"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ SQL Server tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating SQL Server tables: {e}")
        return False


def get_sql_db():
    """Dependency to get SQL database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Test connection
def test_sql_connection():
    """Test SQL Server connection"""
    try:
        with engine.connect() as connection:
            print("✅ SQL Server connection successful!")
            return True
    except Exception as e:
        print(f"❌ SQL Server connection failed: {e}")
        return False
