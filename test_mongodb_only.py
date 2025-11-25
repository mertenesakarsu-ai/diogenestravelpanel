#!/usr/bin/env python3
"""
MongoDB Atlas Bağlantı Testi
Sadece MongoDB Atlas bağlantısını test eder
"""

import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from dotenv import load_dotenv

# Backend .env dosyasını yükle
load_dotenv('/app/backend/.env')

async def test_mongodb_connection():
    """MongoDB Atlas bağlantısını test et"""
    
    print("=" * 60)
    print("🔍 MONGODB ATLAS BAĞLANTI TESTİ")
    print("=" * 60)
    
    mongo_url = os.getenv('MONGO_URL')
    db_name = os.getenv('DB_NAME', 'DiogenesLOG')
    
    if not mongo_url:
        print("❌ HATA: MONGO_URL .env dosyasında bulunamadı!")
        return False
    
    # Güvenlik için URL'yi kısmi göster
    masked_url = mongo_url[:30] + "..." + mongo_url[-20:] if len(mongo_url) > 50 else mongo_url
    print(f"\n📍 Bağlantı URL'si: {masked_url}")
    print(f"🗄️  Database Adı: {db_name}")
    
    try:
        print("\n🔄 MongoDB Atlas'a bağlanılıyor...")
        
        # MongoDB client oluştur
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=10000)
        
        # Bağlantıyı test et
        await client.admin.command('ping')
        print("✅ MongoDB Atlas bağlantısı BAŞARILI!")
        
        # Database'e erişimi test et
        db = client[db_name]
        print(f"✅ '{db_name}' database'ine erişim BAŞARILI!")
        
        # Mevcut koleksiyonları listele
        collections = await db.list_collection_names()
        print(f"\n📚 Mevcut Koleksiyonlar ({len(collections)} adet):")
        if collections:
            for i, coll in enumerate(collections, 1):
                # Her koleksiyondaki kayıt sayısını al
                count = await db[coll].count_documents({})
                print(f"   {i}. {coll} ({count} kayıt)")
        else:
            print("   ℹ️  Henüz koleksiyon yok (database boş)")
        
        # Test verisi yazma
        print("\n🔄 Test verisi yazılıyor...")
        test_collection = db['_connection_test']
        test_doc = {
            "test": True,
            "message": "MongoDB Atlas bağlantı testi başarılı",
            "timestamp": "2025-01-01T00:00:00Z"
        }
        result = await test_collection.insert_one(test_doc)
        print(f"✅ Test verisi yazıldı (ID: {result.inserted_id})")
        
        # Test verisini oku
        read_doc = await test_collection.find_one({"_id": result.inserted_id})
        if read_doc:
            print("✅ Test verisi okundu")
        
        # Test verisini sil (temizlik)
        await test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Test verisi silindi (temizlik)")
        
        # Bağlantıyı kapat
        client.close()
        
        print("\n" + "=" * 60)
        print("🎉 MONGODB ATLAS TEST SONUCU: BAŞARILI")
        print("=" * 60)
        print("\n✅ Tüm MongoDB Atlas operasyonları çalışıyor:")
        print("   • Bağlantı kurma")
        print("   • Database erişimi")
        print("   • Veri yazma (insert)")
        print("   • Veri okuma (read)")
        print("   • Veri silme (delete)")
        print("\n🚀 MongoDB Atlas kullanıma hazır!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ HATA: MongoDB Atlas bağlantısı başarısız!")
        print(f"   Hata detayı: {str(e)}")
        print("\n🔍 Olası sorunlar:")
        print("   1. MONGO_URL doğru mu?")
        print("   2. MongoDB Atlas cluster'ı çalışıyor mu?")
        print("   3. IP whitelist yapılandırması doğru mu?")
        print("   4. Kullanıcı adı ve şifre doğru mu?")
        
        return False

async def main():
    """Ana fonksiyon"""
    success = await test_mongodb_connection()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
