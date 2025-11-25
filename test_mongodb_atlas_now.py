#!/usr/bin/env python3
"""MongoDB Atlas Bağlantı Testi"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv('/app/backend/.env')

def test_mongodb_atlas():
    """MongoDB Atlas bağlantısını test et"""
    
    print("=" * 80)
    print("MongoDB Atlas Bağlantı Testi")
    print("=" * 80)
    
    # Environment değişkenlerini al
    mongo_url = os.getenv('MONGO_URL')
    db_name = os.getenv('DB_NAME')
    
    print(f"\n📋 Konfigürasyon:")
    print(f"   Database: {db_name}")
    print(f"   MongoDB URL: {mongo_url[:50]}..." if mongo_url else "   MongoDB URL: Bulunamadı!")
    
    if not mongo_url or not db_name:
        print("\n❌ HATA: MONGO_URL veya DB_NAME environment variable bulunamadı!")
        return False
    
    try:
        print("\n🔌 MongoDB Atlas'a bağlanılıyor...")
        
        # MongoDB bağlantısı oluştur
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=10000)
        
        # Bağlantıyı test et
        print("   Sunucu bilgileri alınıyor...")
        server_info = client.server_info()
        
        print(f"\n✅ BAĞLANTI BAŞARILI!")
        print(f"   MongoDB Versiyonu: {server_info['version']}")
        print(f"   Platform: {server_info.get('platform', 'N/A')}")
        
        # Database'e bağlan
        db = client[db_name]
        
        # Mevcut koleksiyonları listele
        collections = db.list_collection_names()
        print(f"\n📂 Database: {db_name}")
        print(f"   Toplam Koleksiyon Sayısı: {len(collections)}")
        
        if collections:
            print(f"\n   Koleksiyonlar:")
            for collection_name in collections:
                count = db[collection_name].count_documents({})
                print(f"   - {collection_name}: {count} belge")
        else:
            print("\n   ℹ️ Henüz hiç koleksiyon yok (bu normal, database yeni oluşturulmuş olabilir)")
        
        # Test yazma işlemi
        print(f"\n🧪 Yazma testi yapılıyor...")
        test_collection = db['_connection_test']
        test_doc = {'test': 'MongoDB Atlas bağlantı testi', 'timestamp': 'now'}
        result = test_collection.insert_one(test_doc)
        print(f"   ✅ Test belgesi yazıldı (ID: {result.inserted_id})")
        
        # Test silme işlemi
        test_collection.delete_one({'_id': result.inserted_id})
        print(f"   ✅ Test belgesi silindi")
        
        print(f"\n" + "=" * 80)
        print("✅ TÜM TESTLER BAŞARILI - MongoDB Atlas Tam Çalışıyor!")
        print("=" * 80)
        
        client.close()
        return True
        
    except Exception as e:
        print(f"\n❌ BAĞLANTI HATASI!")
        print(f"   Hata Tipi: {type(e).__name__}")
        print(f"   Hata Mesajı: {str(e)}")
        print(f"\n" + "=" * 80)
        return False

if __name__ == "__main__":
    success = test_mongodb_atlas()
    sys.exit(0 if success else 1)
