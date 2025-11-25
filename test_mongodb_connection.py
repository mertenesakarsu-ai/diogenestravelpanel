#!/usr/bin/env python3
"""MongoDB Atlas bağlantı testi"""

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

# .env dosyasını yükle
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

async def test_mongodb_atlas():
    """MongoDB Atlas bağlantısını test et"""
    
    print("=" * 60)
    print("MongoDB Atlas Bağlantı Testi")
    print("=" * 60)
    
    # Bağlantı bilgilerini göster (güvenlik için maskelenmiş)
    mongo_url = os.environ.get('MONGO_URL', '')
    db_name = os.environ.get('DB_NAME', '')
    
    print(f"\n📦 Database Adı: {db_name}")
    print(f"🔗 Connection URL: {mongo_url[:40]}...{mongo_url[-20:]}")
    
    try:
        # MongoDB Client oluştur
        print("\n🔄 MongoDB Atlas'a bağlanılıyor...")
        client = AsyncIOMotorClient(
            mongo_url,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000
        )
        
        # Database referansı al
        db = client[db_name]
        
        # Ping ile bağlantıyı test et
        print("🔄 Sunucu ping atılıyor...")
        await client.admin.command('ping')
        print("✅ MongoDB Atlas bağlantısı BAŞARILI!")
        
        # Koleksiyonları listele
        print("\n📚 Mevcut Koleksiyonlar:")
        collections = await db.list_collection_names()
        if collections:
            for coll in collections:
                count = await db[coll].count_documents({})
                print(f"  - {coll}: {count} kayıt")
        else:
            print("  (Henüz koleksiyon yok)")
        
        # Test verisi ekle
        print("\n🧪 Test verisi ekleniyor...")
        test_collection = db['connection_test']
        test_doc = {
            'test': 'MongoDB Atlas Connection Test',
            'timestamp': asyncio.get_event_loop().time(),
            'status': 'success'
        }
        result = await test_collection.insert_one(test_doc)
        print(f"✅ Test verisi eklendi (ID: {result.inserted_id})")
        
        # Test verisini oku
        print("🔄 Test verisi okunuyor...")
        retrieved = await test_collection.find_one({'_id': result.inserted_id})
        if retrieved:
            print("✅ Test verisi başarıyla okundu!")
            print(f"  Veri: {retrieved}")
        
        # Test verisini temizle
        print("🧹 Test verisi temizleniyor...")
        await test_collection.delete_one({'_id': result.inserted_id})
        print("✅ Test verisi temizlendi")
        
        print("\n" + "=" * 60)
        print("✅ SONUÇ: MongoDB Atlas tam çalışır durumda!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ HATA: MongoDB Atlas bağlantısı başarısız!")
        print(f"❌ Hata Detayı: {str(e)}")
        print("\n" + "=" * 60)
        print("❌ SONUÇ: MongoDB Atlas bağlantısı BAŞARISIZ!")
        print("=" * 60)
        return False
    finally:
        try:
            client.close()
            print("\n🔒 Bağlantı kapatıldı")
        except:
            pass

if __name__ == "__main__":
    result = asyncio.run(test_mongodb_atlas())
    exit(0 if result else 1)
