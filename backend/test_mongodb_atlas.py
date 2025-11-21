#!/usr/bin/env python3
import pymongo
from pymongo import MongoClient
import ssl

# MongoDB Atlas bağlantı bilgileri
mongo_url = "mongodb+srv://diogenestravel:tXCKrueuPdOTIDdZ@diogeneslog.dp4o2p2.mongodb.net/?retryWrites=true&w=majority&appName=DiogenesLOG"

print("MongoDB Atlas bağlantısı test ediliyor...")
print(f"URL: {mongo_url[:50]}...")

try:
    # Standart bağlantı
    print("\n1. Standart bağlantı deneniyor...")
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=10000)
    client.admin.command('ping')
    print("✅ BAŞARILI! MongoDB Atlas'a bağlandı (standart)")
    print(f"Database: {client.list_database_names()}")
    client.close()
except Exception as e:
    print(f"❌ HATA (standart): {e}")

try:
    # TLS ayarları ile
    print("\n2. TLS=True ile deneniyor...")
    client = MongoClient(
        mongo_url,
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=10000
    )
    client.admin.command('ping')
    print("✅ BAŞARILI! MongoDB Atlas'a bağlandı (TLS)")
    print(f"Database: {client.list_database_names()}")
    client.close()
except Exception as e:
    print(f"❌ HATA (TLS): {e}")

try:
    # SSL context ile
    print("\n3. SSL Context ile deneniyor...")
    client = MongoClient(
        mongo_url,
        ssl=True,
        ssl_cert_reqs=ssl.CERT_NONE,
        serverSelectionTimeoutMS=10000
    )
    client.admin.command('ping')
    print("✅ BAŞARILI! MongoDB Atlas'a bağlandı (SSL context)")
    print(f"Database: {client.list_database_names()}")
    client.close()
except Exception as e:
    print(f"❌ HATA (SSL context): {e}")

print("\n\nTest tamamlandı!")
