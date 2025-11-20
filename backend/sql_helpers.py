"""
SQL Server Helper Functions
Convert async MongoDB operations to sync SQL operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from sql_models import SQLUser, SQLFlight, SQLReservation, SQLOperation, SQLHotel, SQLPackage
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import json


# ==================== USER HELPERS ====================

def get_user_by_id_sql(db: Session, user_id: str) -> Optional[Dict]:
    """Get user by ID from SQL Server"""
    user = db.query(SQLUser).filter(SQLUser.id == user_id).first()
    if not user:
        return None
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "password": user.password,
        "role": user.role,
        "status": user.status,
        "profile_picture": user.profile_picture,
        "created_at": user.created_at
    }


def get_all_users_sql(db: Session) -> List[Dict]:
    """Get all users from SQL Server"""
    users = db.query(SQLUser).all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "password": u.password,
            "role": u.role,
            "status": u.status,
            "profile_picture": u.profile_picture,
            "created_at": u.created_at
        }
        for u in users
    ]


def count_users_sql(db: Session) -> int:
    """Count users in SQL Server"""
    return db.query(func.count(SQLUser.id)).scalar()


def create_user_sql(db: Session, user_data: Dict) -> Dict:
    """Create user in SQL Server"""
    new_user = SQLUser(
        id=user_data['id'],
        name=user_data['name'],
        email=user_data['email'],
        password=user_data['password'],
        role=user_data['role'],
        status=user_data.get('status', 'active'),
        profile_picture=user_data.get('profile_picture'),
        created_at=user_data.get('created_at', datetime.now(timezone.utc))
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "password": new_user.password,
        "role": new_user.role,
        "status": new_user.status,
        "profile_picture": new_user.profile_picture,
        "created_at": new_user.created_at
    }


def update_user_sql(db: Session, user_id: str, user_data: Dict) -> bool:
    """Update user in SQL Server"""
    user = db.query(SQLUser).filter(SQLUser.id == user_id).first()
    if not user:
        return False
    
    for key, value in user_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    db.commit()
    return True


def delete_user_sql(db: Session, user_id: str) -> bool:
    """Delete user from SQL Server"""
    user = db.query(SQLUser).filter(SQLUser.id == user_id).first()
    if not user:
        return False
    
    db.delete(user)
    db.commit()
    return True


def update_profile_picture_sql(db: Session, user_id: str, profile_picture: str) -> bool:
    """Update user's profile picture"""
    user = db.query(SQLUser).filter(SQLUser.id == user_id).first()
    if not user:
        return False
    
    user.profile_picture = profile_picture
    db.commit()
    return True


# ==================== FLIGHT HELPERS ====================

def get_all_flights_sql(db: Session) -> List[Dict]:
    """Get all flights from SQL Server"""
    flights = db.query(SQLFlight).all()
    return [
        {
            "id": f.id,
            "flightCode": f.flightCode,
            "airline": f.airline,
            "from": f.from_location,
            "to": f.to,
            "date": f.date,
            "time": f.time,
            "direction": f.direction,
            "passengers": f.passengers,
            "hasPNR": f.hasPNR,
            "pnr": f.pnr,
            "daysUntilFlight": f.daysUntilFlight,
            "created_at": f.created_at,
            "updated_at": f.updated_at
        }
        for f in flights
    ]


def create_flight_sql(db: Session, flight_data: Dict) -> Dict:
    """Create flight in SQL Server"""
    new_flight = SQLFlight(
        id=flight_data['id'],
        flightCode=flight_data['flightCode'],
        airline=flight_data.get('airline', ''),
        from_location=flight_data['from'],
        to=flight_data['to'],
        date=flight_data['date'],
        time=flight_data['time'],
        direction=flight_data['direction'],
        passengers=flight_data.get('passengers', 0),
        hasPNR=flight_data.get('hasPNR', False),
        pnr=flight_data.get('pnr', ''),
        daysUntilFlight=flight_data.get('daysUntilFlight', 0),
        created_at=flight_data.get('created_at', datetime.now(timezone.utc)),
        updated_at=flight_data.get('updated_at', datetime.now(timezone.utc))
    )
    db.add(new_flight)
    db.commit()
    db.refresh(new_flight)
    
    return {
        "id": new_flight.id,
        "flightCode": new_flight.flightCode,
        "airline": new_flight.airline,
        "from": new_flight.from_location,
        "to": new_flight.to,
        "date": new_flight.date,
        "time": new_flight.time,
        "direction": new_flight.direction,
        "passengers": new_flight.passengers,
        "hasPNR": new_flight.hasPNR,
        "pnr": new_flight.pnr,
        "daysUntilFlight": new_flight.daysUntilFlight,
        "created_at": new_flight.created_at,
        "updated_at": new_flight.updated_at
    }


def update_flight_sql(db: Session, flight_id: str, flight_data: Dict) -> bool:
    """Update flight in SQL Server"""
    flight = db.query(SQLFlight).filter(SQLFlight.id == flight_id).first()
    if not flight:
        return False
    
    flight.flightCode = flight_data.get('flightCode', flight.flightCode)
    flight.airline = flight_data.get('airline', flight.airline)
    flight.from_location = flight_data.get('from', flight.from_location)
    flight.to = flight_data.get('to', flight.to)
    flight.date = flight_data.get('date', flight.date)
    flight.time = flight_data.get('time', flight.time)
    flight.direction = flight_data.get('direction', flight.direction)
    flight.passengers = flight_data.get('passengers', flight.passengers)
    flight.hasPNR = flight_data.get('hasPNR', flight.hasPNR)
    flight.pnr = flight_data.get('pnr', flight.pnr)
    flight.daysUntilFlight = flight_data.get('daysUntilFlight', flight.daysUntilFlight)
    flight.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    return True


def delete_flight_sql(db: Session, flight_id: str) -> bool:
    """Delete flight from SQL Server"""
    flight = db.query(SQLFlight).filter(SQLFlight.id == flight_id).first()
    if not flight:
        return False
    
    db.delete(flight)
    db.commit()
    return True


# ==================== RESERVATION HELPERS ====================

def get_all_reservations_sql(db: Session) -> List[Dict]:
    """Get all reservations from SQL Server"""
    reservations = db.query(SQLReservation).all()
    return [
        {
            "id": r.id,
            "voucherNo": r.voucherNo,
            "leader_name": r.leader_name,
            "leader_passport": r.leader_passport,
            "product_code": r.product_code,
            "product_name": r.product_name,
            "hotel": r.hotel,
            "arrivalDate": r.arrivalDate,
            "departureDate": r.departureDate,
            "pax": r.pax,
            "pax_adults": r.pax_adults,
            "pax_children": r.pax_children,
            "pax_infants": r.pax_infants,
            "status": r.status,
            "source_agency": r.source_agency,
            "package_id": r.package_id,
            "current_leg": r.current_leg,
            "room_type": r.room_type,
            "board_type": r.board_type,
            "destination": r.destination,
            "notes": r.notes,
            "created_at": r.created_at,
            "updated_at": r.updated_at
        }
        for r in reservations
    ]


def get_reservation_by_id_sql(db: Session, reservation_id: str) -> Optional[Dict]:
    """Get reservation by ID from SQL Server"""
    r = db.query(SQLReservation).filter(SQLReservation.id == reservation_id).first()
    if not r:
        return None
    
    return {
        "id": r.id,
        "voucherNo": r.voucherNo,
        "leader_name": r.leader_name,
        "leader_passport": r.leader_passport,
        "product_code": r.product_code,
        "product_name": r.product_name,
        "hotel": r.hotel,
        "arrivalDate": r.arrivalDate,
        "departureDate": r.departureDate,
        "pax": r.pax,
        "pax_adults": r.pax_adults,
        "pax_children": r.pax_children,
        "pax_infants": r.pax_infants,
        "status": r.status,
        "source_agency": r.source_agency,
        "package_id": r.package_id,
        "current_leg": r.current_leg,
        "room_type": r.room_type,
        "board_type": r.board_type,
        "destination": r.destination,
        "notes": r.notes,
        "created_at": r.created_at,
        "updated_at": r.updated_at
    }


def create_reservation_sql(db: Session, reservation_data: Dict) -> Dict:
    """Create reservation in SQL Server"""
    new_reservation = SQLReservation(
        id=reservation_data['id'],
        voucherNo=reservation_data['voucherNo'],
        leader_name=reservation_data['leader_name'],
        leader_passport=reservation_data['leader_passport'],
        product_code=reservation_data['product_code'],
        product_name=reservation_data['product_name'],
        hotel=reservation_data['hotel'],
        arrivalDate=reservation_data['arrivalDate'],
        departureDate=reservation_data['departureDate'],
        pax=reservation_data['pax'],
        pax_adults=reservation_data.get('pax_adults', 0),
        pax_children=reservation_data.get('pax_children', 0),
        pax_infants=reservation_data.get('pax_infants', 0),
        status=reservation_data['status'],
        source_agency=reservation_data.get('source_agency', 'THV'),
        package_id=reservation_data.get('package_id'),
        current_leg=reservation_data.get('current_leg', 0),
        room_type=reservation_data.get('room_type'),
        board_type=reservation_data.get('board_type'),
        destination=reservation_data.get('destination'),
        notes=reservation_data.get('notes'),
        created_at=reservation_data.get('created_at', datetime.now(timezone.utc)),
        updated_at=reservation_data.get('updated_at', datetime.now(timezone.utc))
    )
    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)
    
    return get_reservation_by_id_sql(db, new_reservation.id)


# ==================== OPERATION HELPERS ====================

def get_operations_sql(db: Session, filters: Optional[Dict] = None) -> List[Dict]:
    """Get operations from SQL Server with optional filters"""
    query = db.query(SQLOperation)
    
    if filters:
        if 'date' in filters:
            query = query.filter(SQLOperation.date == filters['date'])
        if 'start_date' in filters and 'end_date' in filters:
            query = query.filter(
                SQLOperation.date >= filters['start_date'],
                SQLOperation.date <= filters['end_date']
            )
        if 'type' in filters and filters['type'] != 'all':
            query = query.filter(SQLOperation.type == filters['type'])
    
    operations = query.all()
    
    result = []
    for op in operations:
        # Parse JSON fields
        arrival_flight = json.loads(op.arrivalFlight) if op.arrivalFlight else None
        return_flight = json.loads(op.returnFlight) if op.returnFlight else None
        transfer_flight = json.loads(op.transferFlight) if op.transferFlight else None
        
        result.append({
            "id": op.id,
            "reservationId": op.reservationId,
            "voucherNo": op.voucherNo,
            "arrivalFlight": arrival_flight,
            "returnFlight": return_flight,
            "transferFlight": transfer_flight,
            "currentHotel": op.currentHotel,
            "hotelCheckIn": op.hotelCheckIn,
            "hotelCheckOut": op.hotelCheckOut,
            "flightCode": op.flightCode,
            "type": op.type,
            "from": op.from_location,
            "to": op.to,
            "date": op.date,
            "time": op.time,
            "passengers": op.passengers,
            "hotel": op.hotel,
            "transferTime": op.transferTime,
            "notes": op.notes,
            "status": op.status,
            "created_at": op.created_at,
            "updated_at": op.updated_at
        })
    
    return result


def get_operation_by_id_sql(db: Session, operation_id: str) -> Optional[Dict]:
    """Get operation by ID from SQL Server"""
    op = db.query(SQLOperation).filter(SQLOperation.id == operation_id).first()
    if not op:
        return None
    
    arrival_flight = json.loads(op.arrivalFlight) if op.arrivalFlight else None
    return_flight = json.loads(op.returnFlight) if op.returnFlight else None
    transfer_flight = json.loads(op.transferFlight) if op.transferFlight else None
    
    return {
        "id": op.id,
        "reservationId": op.reservationId,
        "voucherNo": op.voucherNo,
        "arrivalFlight": arrival_flight,
        "returnFlight": return_flight,
        "transferFlight": transfer_flight,
        "currentHotel": op.currentHotel,
        "hotelCheckIn": op.hotelCheckIn,
        "hotelCheckOut": op.hotelCheckOut,
        "flightCode": op.flightCode,
        "type": op.type,
        "from": op.from_location,
        "to": op.to,
        "date": op.date,
        "time": op.time,
        "passengers": op.passengers,
        "hotel": op.hotel,
        "transferTime": op.transferTime,
        "notes": op.notes,
        "status": op.status,
        "created_at": op.created_at,
        "updated_at": op.updated_at
    }


def create_operation_sql(db: Session, operation_data: Dict) -> Dict:
    """Create operation in SQL Server"""
    # Convert flight dicts to JSON strings
    arrival_flight_json = json.dumps(operation_data.get('arrivalFlight')) if operation_data.get('arrivalFlight') else None
    return_flight_json = json.dumps(operation_data.get('returnFlight')) if operation_data.get('returnFlight') else None
    transfer_flight_json = json.dumps(operation_data.get('transferFlight')) if operation_data.get('transferFlight') else None
    
    new_operation = SQLOperation(
        id=operation_data['id'],
        reservationId=operation_data.get('reservationId'),
        voucherNo=operation_data.get('voucherNo', ''),
        arrivalFlight=arrival_flight_json,
        returnFlight=return_flight_json,
        transferFlight=transfer_flight_json,
        currentHotel=operation_data.get('currentHotel', ''),
        hotelCheckIn=operation_data.get('hotelCheckIn', ''),
        hotelCheckOut=operation_data.get('hotelCheckOut', ''),
        flightCode=operation_data.get('flightCode', ''),
        type=operation_data.get('type', 'transfer'),
        from_location=operation_data.get('from', ''),
        to=operation_data.get('to', ''),
        date=operation_data.get('date', ''),
        time=operation_data.get('time', ''),
        passengers=operation_data.get('passengers', 0),
        hotel=operation_data.get('hotel', ''),
        transferTime=operation_data.get('transferTime', ''),
        notes=operation_data.get('notes', ''),
        status=operation_data.get('status', 'scheduled'),
        created_at=operation_data.get('created_at', datetime.now(timezone.utc)),
        updated_at=operation_data.get('updated_at', datetime.now(timezone.utc))
    )
    db.add(new_operation)
    db.commit()
    db.refresh(new_operation)
    
    return get_operation_by_id_sql(db, new_operation.id)


# ==================== HOTEL HELPERS ====================

def get_all_hotels_sql(db: Session, filters: Optional[Dict] = None) -> List[Dict]:
    """Get hotels from SQL Server with optional filters"""
    query = db.query(SQLHotel)
    
    if filters:
        if filters.get('active_only', True):
            query = query.filter(SQLHotel.active == True)
        if 'region' in filters and filters['region']:
            query = query.filter(SQLHotel.region == filters['region'])
        if 'category' in filters and filters['category']:
            query = query.filter(SQLHotel.category == filters['category'])
        if 'search' in filters and filters['search']:
            search_term = f"%{filters['search']}%"
            query = query.filter(
                (SQLHotel.name.like(search_term)) |
                (SQLHotel.code.like(search_term)) |
                (SQLHotel.region.like(search_term)) |
                (SQLHotel.city.like(search_term))
            )
    
    hotels = query.all()
    
    return [
        {
            "id": h.id,
            "code": h.code,
            "name": h.name,
            "category": h.category,
            "region": h.region,
            "region_code": h.region_code,
            "transfer_region": h.transfer_region,
            "phone1": h.phone1,
            "phone2": h.phone2,
            "fax": h.fax,
            "email": h.email,
            "email2": h.email2,
            "email3": h.email3,
            "website": h.website,
            "address": h.address,
            "address2": h.address2,
            "city": h.city,
            "postal_code": h.postal_code,
            "country": h.country,
            "service_type": h.service_type,
            "manager": h.manager,
            "notes": h.notes,
            "active": h.active,
            "latitude": h.latitude,
            "longitude": h.longitude,
            "stars": h.stars,
            "paximum_id": h.paximum_id,
            "giata": h.giata,
            "created_at": h.created_at,
            "updated_at": h.updated_at
        }
        for h in hotels
    ]


def get_hotel_by_id_sql(db: Session, hotel_id: str) -> Optional[Dict]:
    """Get hotel by ID from SQL Server"""
    h = db.query(SQLHotel).filter(SQLHotel.id == hotel_id).first()
    if not h:
        return None
    
    return {
        "id": h.id,
        "code": h.code,
        "name": h.name,
        "category": h.category,
        "region": h.region,
        "region_code": h.region_code,
        "transfer_region": h.transfer_region,
        "phone1": h.phone1,
        "phone2": h.phone2,
        "fax": h.fax,
        "email": h.email,
        "email2": h.email2,
        "email3": h.email3,
        "website": h.website,
        "address": h.address,
        "address2": h.address2,
        "city": h.city,
        "postal_code": h.postal_code,
        "country": h.country,
        "service_type": h.service_type,
        "manager": h.manager,
        "notes": h.notes,
        "active": h.active,
        "latitude": h.latitude,
        "longitude": h.longitude,
        "stars": h.stars,
        "paximum_id": h.paximum_id,
        "giata": h.giata,
        "created_at": h.created_at,
        "updated_at": h.updated_at
    }


def create_hotel_sql(db: Session, hotel_data: Dict) -> Dict:
    """Create hotel in SQL Server"""
    new_hotel = SQLHotel(
        id=hotel_data['id'],
        code=hotel_data['code'],
        name=hotel_data['name'],
        category=hotel_data.get('category', ''),
        region=hotel_data.get('region', ''),
        region_code=hotel_data.get('region_code', ''),
        transfer_region=hotel_data.get('transfer_region', ''),
        phone1=hotel_data.get('phone1', ''),
        phone2=hotel_data.get('phone2', ''),
        fax=hotel_data.get('fax', ''),
        email=hotel_data.get('email', ''),
        email2=hotel_data.get('email2', ''),
        email3=hotel_data.get('email3', ''),
        website=hotel_data.get('website', ''),
        address=hotel_data.get('address', ''),
        address2=hotel_data.get('address2', ''),
        city=hotel_data.get('city', ''),
        postal_code=hotel_data.get('postal_code', ''),
        country=hotel_data.get('country', ''),
        service_type=hotel_data.get('service_type', 'Otel'),
        manager=hotel_data.get('manager', ''),
        notes=hotel_data.get('notes', ''),
        active=hotel_data.get('active', True),
        latitude=hotel_data.get('latitude', 0.0),
        longitude=hotel_data.get('longitude', 0.0),
        stars=hotel_data.get('stars', 0),
        paximum_id=hotel_data.get('paximum_id', ''),
        giata=hotel_data.get('giata', ''),
        created_at=hotel_data.get('created_at', datetime.now(timezone.utc)),
        updated_at=hotel_data.get('updated_at', datetime.now(timezone.utc))
    )
    db.add(new_hotel)
    db.commit()
    db.refresh(new_hotel)
    
    return get_hotel_by_id_sql(db, new_hotel.id)
