"""
DIOGENESSEJOUR Database Service
Bu dosya DIOGENESSEJOUR database'inden veri çekmek için kullanılır.
"""
import pymssql
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_diogenes_connection():
    """DIOGENESSEJOUR database'ine bağlantı oluştur"""
    try:
        conn = pymssql.connect(
            server=os.environ.get('SQL_SERVER_HOST'),
            user=os.environ.get('SQL_SERVER_USER'),
            password=os.environ.get('SQL_SERVER_PASSWORD'),
            database='DIOGENESSEJOUR',  # DIOGENESSEJOUR database
            port=os.environ.get('SQL_SERVER_PORT', '1433')
        )
        return conn
    except Exception as e:
        logger.error(f"DIOGENESSEJOUR connection error: {e}")
        raise

def test_diogenes_connection() -> bool:
    """DIOGENESSEJOUR database bağlantısını test et"""
    try:
        conn = get_diogenes_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DB_NAME()")
        db_name = cursor.fetchone()[0]
        conn.close()
        logger.info(f"✅ Successfully connected to DIOGENESSEJOUR database: {db_name}")
        return True
    except Exception as e:
        logger.error(f"❌ DIOGENESSEJOUR connection test failed: {e}")
        return False

# ==================== MUSTERI (CUSTOMERS) ====================

def get_customers(
    limit: int = 100,
    offset: int = 0,
    search: Optional[str] = None
) -> Dict[str, Any]:
    """
    Musteri tablosundan müşteri listesi çek
    
    Args:
        limit: Sayfa başına kayıt sayısı
        offset: Başlangıç offset'i
        search: Arama terimi (Adi, Unvan)
    
    Returns:
        Dict with customers list and total count
    """
    try:
        conn = get_diogenes_connection()
        cursor = conn.cursor(as_dict=True)
        
        # Count query
        count_query = "SELECT COUNT(*) as total FROM Musteri"
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append("(Adi LIKE %s OR Unvan LIKE %s)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        if where_conditions:
            count_query += " WHERE " + " AND ".join(where_conditions)
        
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # Data query with pagination
        data_query = """
            SELECT TOP %s 
                Turop, Voucher, Sira, Adi, Unvan, Yasi, Milliyet, 
                GelYeri, DonYeri, Grup1, Grup2, Grup3, Grup4, Grup5
            FROM Musteri
        """
        
        if where_conditions:
            data_query += " WHERE " + " AND ".join(where_conditions)
        
        data_query += " ORDER BY Turop, Voucher, Sira OFFSET %s ROWS"
        
        cursor.execute(data_query, [limit] + params + [offset])
        customers = cursor.fetchall()
        
        conn.close()
        
        # Map to English field names
        mapped_customers = []
        for customer in customers:
            mapped_customers.append({
                'tourOperator': customer.get('Turop', ''),
                'voucher': customer.get('Voucher', ''),
                'sequence': customer.get('Sira', 0),
                'name': customer.get('Adi', ''),
                'title': customer.get('Unvan', ''),
                'age': customer.get('Yasi', 0),
                'nationality': customer.get('Milliyet', ''),
                'arrivalFrom': customer.get('GelYeri', ''),
                'departureTo': customer.get('DonYeri', ''),
                'group1': customer.get('Grup1', ''),
                'group2': customer.get('Grup2', ''),
                'group3': customer.get('Grup3', ''),
                'group4': customer.get('Grup4', ''),
                'group5': customer.get('Grup5', '')
            })
        
        return {
            'customers': mapped_customers,
            'total': total,
            'limit': limit,
            'offset': offset
        }
    except Exception as e:
        logger.error(f"Error fetching customers: {e}")
        raise

# ==================== OTEL (HOTELS) ====================

def get_hotels(
    limit: int = 100,
    offset: int = 0,
    search: Optional[str] = None,
    region: Optional[str] = None
) -> Dict[str, Any]:
    """
    Otel tablosundan otel listesi çek
    
    Args:
        limit: Sayfa başına kayıt sayısı
        offset: Başlangıç offset'i
        search: Arama terimi (Adi)
        region: Bölge filtresi (Bolge)
    
    Returns:
        Dict with hotels list and total count
    """
    try:
        conn = get_diogenes_connection()
        cursor = conn.cursor(as_dict=True)
        
        # Count query
        count_query = "SELECT COUNT(*) as total FROM Otel"
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append("Adi LIKE %s")
            params.append(f"%{search}%")
        
        if region:
            where_conditions.append("Bolge = %s")
            params.append(region)
        
        if where_conditions:
            count_query += " WHERE " + " AND ".join(where_conditions)
        
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # Data query with pagination
        data_query = """
            SELECT TOP %s 
                Otel, Adi, Bolge, Kategori, Ulke, Tel, Fax, Email, 
                Yonetici, Adres, Sehir, PostaKodu, Web, Enlem, Boylam,
                PaxmaxKodu, Giata
            FROM Otel
        """
        
        if where_conditions:
            data_query += " WHERE " + " AND ".join(where_conditions)
        
        data_query += " ORDER BY Adi OFFSET %s ROWS"
        
        cursor.execute(data_query, [limit] + params + [offset])
        hotels = cursor.fetchall()
        
        conn.close()
        
        # Map to English field names
        mapped_hotels = []
        for hotel in hotels:
            # Extract stars from Kategori (e.g., "5 YILDIZ" -> 5)
            kategori = hotel.get('Kategori', '')
            stars = 0
            if 'YILDIZ' in kategori or 'STAR' in kategori.upper():
                try:
                    stars = int(''.join(filter(str.isdigit, kategori.split()[0])))
                except:
                    stars = 0
            
            mapped_hotels.append({
                'code': hotel.get('Otel', ''),
                'name': hotel.get('Adi', ''),
                'region': hotel.get('Bolge', ''),
                'category': hotel.get('Kategori', ''),
                'country': hotel.get('Ulke', ''),
                'phone': hotel.get('Tel', ''),
                'fax': hotel.get('Fax', ''),
                'email': hotel.get('Email', ''),
                'manager': hotel.get('Yonetici', ''),
                'address': hotel.get('Adres', ''),
                'city': hotel.get('Sehir', ''),
                'postalCode': hotel.get('PostaKodu', ''),
                'website': hotel.get('Web', ''),
                'latitude': hotel.get('Enlem', 0.0),
                'longitude': hotel.get('Boylam', 0.0),
                'stars': stars,
                'paximumCode': hotel.get('PaxmaxKodu', ''),
                'giataCode': hotel.get('Giata', '')
            })
        
        return {
            'hotels': mapped_hotels,
            'total': total,
            'limit': limit,
            'offset': offset
        }
    except Exception as e:
        logger.error(f"Error fetching hotels: {e}")
        raise

def get_hotel_regions() -> List[str]:
    """Tüm otel bölgelerini çek"""
    try:
        conn = get_diogenes_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT Bolge FROM Otel WHERE Bolge IS NOT NULL AND Bolge != '' ORDER BY Bolge")
        regions = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return regions
    except Exception as e:
        logger.error(f"Error fetching hotel regions: {e}")
        return []

# ==================== MUSTERIOPR (RESERVATIONS/OPERATIONS) ====================

def get_reservations(
    limit: int = 100,
    offset: int = 0,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> Dict[str, Any]:
    """
    MusteriOpr ve Musteri tablolarından rezervasyon listesi çek
    
    Args:
        limit: Sayfa başına kayıt sayısı
        offset: Başlangıç offset'i
        search: Arama terimi (Voucher, Turop)
        date_from: Başlangıç tarihi (YYYY-MM-DD)
        date_to: Bitiş tarihi (YYYY-MM-DD)
    
    Returns:
        Dict with reservations list and total count
    """
    try:
        conn = get_diogenes_connection()
        cursor = conn.cursor(as_dict=True)
        
        # Count query
        count_query = """
            SELECT COUNT(*) as total 
            FROM MusteriOpr mo
        """
        
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append("(mo.Voucher LIKE %s OR mo.Turop LIKE %s)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        if date_from:
            where_conditions.append("mo.GirTarih >= %s")
            params.append(date_from)
        
        if date_to:
            where_conditions.append("mo.GirTarih <= %s")
            params.append(date_to)
        
        if where_conditions:
            count_query += " WHERE " + " AND ".join(where_conditions)
        
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # Data query with JOIN to Musteri table
        data_query = """
            SELECT TOP %s
                mo.MusNo, mo.RezSira, mo.Turop, mo.Voucher, mo.GirTarih, 
                mo.GelTrfNo, mo.DonTrfNo, mo.InfKokRecNo,
                m.Adi as MusteriAdi, m.Unvan as MusteriUnvan, m.Milliyet
            FROM MusteriOpr mo
            LEFT JOIN Musteri m ON mo.Turop = m.Turop AND mo.Voucher = m.Voucher AND m.Sira = 1
        """
        
        if where_conditions:
            data_query += " WHERE " + " AND ".join(where_conditions)
        
        data_query += " ORDER BY mo.GirTarih DESC OFFSET %s ROWS"
        
        cursor.execute(data_query, [limit] + params + [offset])
        reservations = cursor.fetchall()
        
        conn.close()
        
        # Map to English field names
        mapped_reservations = []
        for res in reservations:
            mapped_reservations.append({
                'customerNo': res.get('MusNo', ''),
                'reservationSeq': res.get('RezSira', 0),
                'tourOperator': res.get('Turop', ''),
                'voucherNo': res.get('Voucher', ''),
                'checkInDate': res.get('GirTarih').strftime('%Y-%m-%d') if res.get('GirTarih') else '',
                'arrivalTransferNo': res.get('GelTrfNo', ''),
                'departureTransferNo': res.get('DonTrfNo', ''),
                'infoRootRecNo': res.get('InfKokRecNo', 0),
                'customerName': res.get('MusteriAdi', ''),
                'customerTitle': res.get('MusteriUnvan', ''),
                'nationality': res.get('Milliyet', '')
            })
        
        return {
            'reservations': mapped_reservations,
            'total': total,
            'limit': limit,
            'offset': offset
        }
    except Exception as e:
        logger.error(f"Error fetching reservations: {e}")
        raise

def get_operations(
    limit: int = 100,
    offset: int = 0,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    operation_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    MusteriOpr tablosundan operasyon listesi çek
    
    Args:
        limit: Sayfa başına kayıt sayısı
        offset: Başlangıç offset'i
        search: Arama terimi (Voucher)
        date_from: Başlangıç tarihi (YYYY-MM-DD)
        date_to: Bitiş tarihi (YYYY-MM-DD)
        operation_type: Operasyon tipi filtresi
    
    Returns:
        Dict with operations list and total count
    """
    try:
        conn = get_diogenes_connection()
        cursor = conn.cursor(as_dict=True)
        
        # Count query
        count_query = """
            SELECT COUNT(*) as total 
            FROM MusteriOpr mo
        """
        
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append("mo.Voucher LIKE %s")
            params.append(f"%{search}%")
        
        if date_from:
            where_conditions.append("mo.GirTarih >= %s")
            params.append(date_from)
        
        if date_to:
            where_conditions.append("mo.GirTarih <= %s")
            params.append(date_to)
        
        if where_conditions:
            count_query += " WHERE " + " AND ".join(where_conditions)
        
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # Data query with JOIN to Musteri table for passenger count
        data_query = """
            SELECT TOP %s
                mo.MusNo, mo.RezSira, mo.Turop, mo.Voucher, mo.GirTarih, 
                mo.GelTrfNo, mo.DonTrfNo,
                (SELECT COUNT(*) FROM Musteri m WHERE m.Turop = mo.Turop AND m.Voucher = mo.Voucher) as PaxCount
            FROM MusteriOpr mo
        """
        
        if where_conditions:
            data_query += " WHERE " + " AND ".join(where_conditions)
        
        data_query += " ORDER BY mo.GirTarih DESC OFFSET %s ROWS"
        
        cursor.execute(data_query, [limit] + params + [offset])
        operations = cursor.fetchall()
        
        conn.close()
        
        # Map to English field names
        mapped_operations = []
        for op in operations:
            mapped_operations.append({
                'id': f"{op.get('MusNo', '')}-{op.get('RezSira', 0)}",
                'customerNo': op.get('MusNo', ''),
                'reservationSeq': op.get('RezSira', 0),
                'tourOperator': op.get('Turop', ''),
                'voucherNo': op.get('Voucher', ''),
                'operationDate': op.get('GirTarih').strftime('%Y-%m-%d') if op.get('GirTarih') else '',
                'arrivalTransferNo': op.get('GelTrfNo', ''),
                'departureTransferNo': op.get('DonTrfNo', ''),
                'passengerCount': op.get('PaxCount', 0),
                'status': 'scheduled'  # Default status
            })
        
        return {
            'operations': mapped_operations,
            'total': total,
            'limit': limit,
            'offset': offset
        }
    except Exception as e:
        logger.error(f"Error fetching operations: {e}")
        raise

def get_reservation_details(voucher: str, tour_operator: str) -> Dict[str, Any]:
    """
    Belirli bir rezervasyonun detaylı bilgilerini çek (yolcu listesi dahil)
    
    Args:
        voucher: Voucher numarası
        tour_operator: Tur operatörü kodu
    
    Returns:
        Dict with reservation details and passenger list
    """
    try:
        conn = get_diogenes_connection()
        cursor = conn.cursor(as_dict=True)
        
        # Get reservation info
        cursor.execute("""
            SELECT mo.MusNo, mo.RezSira, mo.Turop, mo.Voucher, mo.GirTarih, 
                   mo.GelTrfNo, mo.DonTrfNo, mo.InfKokRecNo
            FROM MusteriOpr mo
            WHERE mo.Voucher = %s AND mo.Turop = %s
        """, (voucher, tour_operator))
        
        reservation = cursor.fetchone()
        
        if not reservation:
            conn.close()
            return None
        
        # Get passengers
        cursor.execute("""
            SELECT Sira, Adi, Unvan, Yasi, Milliyet, GelYeri, DonYeri
            FROM Musteri
            WHERE Voucher = %s AND Turop = %s
            ORDER BY Sira
        """, (voucher, tour_operator))
        
        passengers = cursor.fetchall()
        
        conn.close()
        
        # Map passengers
        mapped_passengers = []
        for passenger in passengers:
            mapped_passengers.append({
                'sequence': passenger.get('Sira', 0),
                'name': passenger.get('Adi', ''),
                'title': passenger.get('Unvan', ''),
                'age': passenger.get('Yasi', 0),
                'nationality': passenger.get('Milliyet', ''),
                'arrivalFrom': passenger.get('GelYeri', ''),
                'departureTo': passenger.get('DonYeri', '')
            })
        
        return {
            'reservation': {
                'customerNo': reservation.get('MusNo', ''),
                'reservationSeq': reservation.get('RezSira', 0),
                'tourOperator': reservation.get('Turop', ''),
                'voucherNo': reservation.get('Voucher', ''),
                'checkInDate': reservation.get('GirTarih').strftime('%Y-%m-%d') if reservation.get('GirTarih') else '',
                'arrivalTransferNo': reservation.get('GelTrfNo', ''),
                'departureTransferNo': reservation.get('DonTrfNo', ''),
                'infoRootRecNo': reservation.get('InfKokRecNo', 0)
            },
            'passengers': mapped_passengers,
            'passengerCount': len(mapped_passengers)
        }
    except Exception as e:
        logger.error(f"Error fetching reservation details: {e}")
        raise
