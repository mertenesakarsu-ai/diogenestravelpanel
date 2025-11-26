# Diogenes Travel Panel

Tamamen IP-whitelist ile korunan bir operasyon paneli. FastAPI backend'i, React
frontend'i ve Nginx reverse proxy katmanı birlikte çalışıyor.

## Monorepo Yapısı

- `backend/` – FastAPI + SQL Server + MongoDB loglama katmanı
- `frontend/` – React (CRACO) SPA
- `deploy/nginx/` – Reverse proxy ve IP whitelist konfigürasyonu
- `IP_WHITELIST_*.md` – Kurulum/test raporları

## Geliştirme Ortamı

### Lokalhost Kurulum Adımları - Özet

1. **Depoyu klonlayın** ve proje klasörüne geçin.
2. **Backend** için sanal ortam kurup bağımlılıkları yükleyin, `.env` değerlerini
   doldurun ve `uvicorn server:app --reload --port 8001` ile başlatın.
3. **Frontend** dizinine geçip `yarn install` + `yarn start` çalıştırın; `.env`
   içinde `REACT_APP_BACKEND_URL=http://127.0.0.1:8001` olduğundan React app
   tüm API çağrılarını yereldeki FastAPI’ye yönlendirir.
4. Tarayıcıdan `http://127.0.0.1:3000/login` adresini açın.

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

`backend/.env` dosyasında en az şu değişkenler olmalı:

```
MONGO_URL=mongodb+srv://...
DB_NAME=diogenes
SQLSERVER_SERVER=...
SQLSERVER_DB=...
SQLSERVER_USER=...
SQLSERVER_PASSWORD=...
IP_WHITELIST="217.131.25.91,127.0.0.1,::1"
ENABLE_BACKEND_IP_CHECK=false  # Nginx zaten IP kontrolünü yapıyor
```

Sunucuyu başlatmak için:

```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Uzak Sunucudan SQL Server'a Bağlanma (SSMS)

1. **Uzak masaüstüne bağlanın.** RDP ile eriştiğiniz Windows sunucusunda SQL Server
   Management Studio (SSMS) kurulu olmalı.
2. **SSMS'i açın** ve açılışta gelen `Connect to Server` penceresinde:
   - Server type: `Database Engine`
   - Server name: `diogenesdb.cfcuyemma1m9.eu-west-2.rds.amazonaws.com,1433`
     (backend `.env` içinde yer alan host/port)
   - Authentication: `SQL Server Authentication`
   - Login / Password: backend `.env` dosyasındaki `SQL_SERVER_USER` /
     `SQL_SERVER_PASSWORD`
3. **Connect** butonuna bastığınızda eğer IP'niz AWS Security Group veya RDS
   whitelist'inde ise bağlantı sağlanır. Bağlantı hatası alırsanız:
   - RDS güvenlik grubuna ilgili IP'nin ekli olduğundan emin olun.
   - Sunucudan outbound 1433 portunun açık olduğunu kontrol edin.
4. **Yeni veritabanı oluşturmak** için Object Explorer'da `Databases` üzerinde sağ
   tık → `New Database...` adımlarını izleyin.
5. **Schema değişiklikleri / sorgular** için `New Query` penceresini açıp T-SQL
   komutlarını çalıştırabilirsiniz. Production ortamında komutları çalıştırmadan
   önce yedek almayı unutmayın.

### 2. Frontend

```bash
cd frontend
yarn install
```

`frontend/.env` dosyasını oluşturun:

```
REACT_APP_BACKEND_URL=http://127.0.0.1:8001
REACT_APP_ENABLE_VISUAL_EDITS=false
```

Ardından:

```bash
yarn start
```

> **Not:** CRA dev sunucusu (3000) ile FastAPI (8001) yalnızca makinenizde
çalışır. Farklı bir Wi-Fi veya dış ağdan localhost’a erişemezsiniz; bu bağlantı
denemeleri doğrudan bilgisayarınıza yönlenmez. Başka bir cihazdan erişim
test edecekseniz projenizi aynı ağdaki başka bir cihazdan erişilebilecek bir
IP’ye (örn. `http://192.168.1.5:8001`) bind etmeniz ve güvenlik duvarınızı
konfigüre etmeniz gerekir.

## IP Whitelist Mantığı

1. **Nginx (deploy/nginx/diogenes.conf)** ilk savunma hattıdır.
   - `geo` bloğu yalnızca `217.131.25.91`, `127.0.0.1` ve `::1` IP'lerini kabul eder.
   - Hem `/api/*` hem de SPA rotaları (örn. `/login`) IP filtresinden geçer.
   - Red edilen kullanıcılar için `frontend/public/access-denied.html`
     dosyası tek başına gösterilir, böylece başka bir asset yüklemeye gerek
     kalmaz.

2. **Backend middleware** (opsiyonel) ikinci savunma hattıdır. `.env` içinde
   `ENABLE_BACKEND_IP_CHECK=true` yaparsanız FastAPI tarafında da aynı kontrol
   devreye girer.

## Nginx Konfigürasyonunu Deploy Etme

### Sunucu Kurulum Adımları (Prod)

1. Uzak sunucuda backend ve frontend servislerinizi (örneğin supervisor veya
   systemd ile) 8001 ve 3000 portlarına bind edin.
2. `deploy/nginx/diogenes.conf` dosyasını sunucudaki `/etc/nginx/sites-available/`
   dizinine kopyalayın.
3. Gerekirse `upstream` portlarını veya `server_name` değerini güncelleyin.
4. `sudo ln -sf /etc/nginx/sites-available/diogenes.conf /etc/nginx/sites-enabled/diogenes.conf`
   ile site’ı etkinleştirin.
5. `sudo nginx -t` ile testi geçtikten sonra `sudo systemctl reload nginx` veya
   `sudo nginx -s reload` komutuyla konfigürasyonu devreye alın.
6. Whitelist IP’lerini `geo` bloğuna ekleyip yeniden yükleme yapmayı unutmayın.

1. `deploy/nginx/diogenes.conf` dosyasını sunucudaki
   `/etc/nginx/sites-available/` içine kopyalayın.
2. `upstream` bloklarındaki portlar (8001/3000) yaşam ortamınıza uyuyorsa
   değiştirmeye gerek yoktur. Farklıysa güncelleyin.
3. Site'ı etkinleştirin ve Nginx'i yeniden yükleyin:

```bash
sudo ln -sf /etc/nginx/sites-available/diogenes.conf /etc/nginx/sites-enabled/diogenes.conf
sudo nginx -t
sudo systemctl reload nginx
```

### Caddy ile Alternatif Reverse Proxy Kurulumu

`deploy/caddy/Caddyfile` dosyası, Nginx ile aynı whitelist politikasını Caddy 2
üzerinde uygular. Prod ortamda Caddy kullanmak için:

1. Caddy’yi kurun (ör. `apt install caddy` veya resmi script). Servis dosyası
   `/etc/caddy/Caddyfile` yolunu kullanır.
2. Bu repodaki `deploy/caddy/Caddyfile` dosyasını sunucuya kopyalayın ve IP
   listesi, backend/frontend portları gerekiyorsa güncelleyin.
3. Dosyayı `/etc/caddy/Caddyfile` olarak kaydedin ya da `sudo cp
   deploy/caddy/Caddyfile /etc/caddy/Caddyfile`.
4. `sudo caddy fmt --overwrite /etc/caddy/Caddyfile` ile biçimi kontrol edin
   (opsiyonel) ve `sudo caddy validate --config /etc/caddy/Caddyfile` komutuyla
   test edin.
5. `sudo systemctl reload caddy` (veya `sudo systemctl restart caddy`) komutuyla
   yeni konfigürasyonu devreye alın.
6. Caddy dosyasındaki `@allowed remote_ip ...` satırına yeni IP ekleyerek whitelist’i
   yönetebilirsiniz; değişiklik sonrası yeniden yükleme yapmayı unutmayın.

> Caddy konfigürasyonu izinli IP’ler için `/api/*` isteklerini `127.0.0.1:8001`
> backend’ine, diğer tüm rotaları `127.0.0.1:3000` React uygulamasına yönlendirir.
> İzinli olmayan IP’ler, Caddy’nin doğrudan döndürdüğü statik bir 403 HTML sayfası
> görür; böylece frontend asset’lerine dahi erişemezler.

### Lokal ortamda IP kontrolü nasıl test edilir?

- Sadece localhost’ta çalışıyorsanız IP filtrelemesi, uygulama sizin makinenizde
  olduğu için pratikte *zaten* tek bir IP’den (kendinizden) erişilebilir.
- Farklı bir Wi-Fi veya 4G üzerinden erişmeyi denerseniz bu talepler kendi
  laptop’ınıza ulaşamaz; bu yüzden whitelist devreye girmez.
- Gerçek whitelist davranışını görmek için Nginx konfigürasyonunu deploy ettiğiniz
  uzak sunucuya iki farklı ağ üzerinden bağlanın:
  1. İzinli IP (örneğin ev/ofis IP’niz) → site normal açılır.
  2. Farklı ağ veya mobil veri → Nginx 403 döner ve
     `frontend/public/access-denied.html` içeriği görüntülenir.
  Bu yöntem, IP kontrolünün (nginx seviyesinde) gerçekten çalıştığını doğrular.

## Whitelist'i Güncellemek

- **Geçici** olarak yeni bir IP açmanız gerekirse `deploy/nginx/diogenes.conf`
  içindeki `geo` ve `allow` bloklarına IP'yi ekleyip Nginx'i reload etmeniz
  yeterli.
- **Kalıcı** hale getirmek için aynı IP'yi `backend/.env` içindeki
  `IP_WHITELIST` değişkenine de ekleyin.

## Test

```bash
# İzin verilen IP'den
curl -I http://panel.domain.com/login  # 200

# İzin verilmeyen IP'den
curl -I http://panel.domain.com/login  # 403 + access-denied HTML
```

Kullanıcı farklı bir ağdan bağlandığında artık Nginx, giriş isteğini
`/access-denied.html` içeriği ile yanıtlar ve kullanıcı hiçbir şekilde `/login`
veya API uçlarına ulaşamaz.
