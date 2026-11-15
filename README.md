# ✅ Görev Yönetimi API

FastAPI ile yazılmış, test edilmiş ve Docker ile paketlenmiş bir REST API. Görevleri oluşturma, listeleme, filtreleme, güncelleme ve silme işlemlerini yapar.

## 🧰 Teknolojiler
Python · FastAPI · SQLAlchemy 2.0 · SQLite · Pydantic · Pytest · Docker

## ✨ Özellikler
- Tam **CRUD** (`POST / GET / PATCH / DELETE`)
- Duruma göre **filtreleme**, başlıkta **arama**, **sayfalama**
- Pydantic ile **girdi doğrulama** (ör. öncelik 1–5 dışındaysa `422`)
- Doğru HTTP durum kodları (`201`, `204`, `404`, `422`)
- Otomatik **Swagger** dokümantasyonu: `/docs`
- Bellek içi veritabanıyla çalışan **pytest** testleri
- `Dockerfile` ile tek komutla çalıştırma

## 🚀 Çalıştırma
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Tarayıcıda `http://127.0.0.1:8000/docs` adresini aç.

Docker ile:
```bash
docker build -t gorev-api .
docker run -p 8000:8000 gorev-api
```

## 🔌 Uç Noktalar
| Metot | Yol | Açıklama |
|---|---|---|
| GET | `/saglik` | Servis sağlık kontrolü |
| POST | `/gorevler` | Yeni görev |
| GET | `/gorevler?durum=&arama=&sayfa=&boyut=` | Listele / filtrele |
| GET | `/gorevler/{id}` | Tek görev |
| PATCH | `/gorevler/{id}` | Kısmi güncelleme |
| DELETE | `/gorevler/{id}` | Sil |

Örnek:
```bash
curl -X POST http://127.0.0.1:8000/gorevler \
  -H "Content-Type: application/json" \
  -d '{"baslik": "Rapor yaz", "oncelik": 2}'
```

## 🧪 Test
```bash
pytest -q
```

## 🔭 Geliştirme Fikirleri
- JWT ile kullanıcı girişi ve kullanıcıya özel görevler
- Alembic ile veritabanı göçleri
- PostgreSQL + docker-compose
- GitHub Actions ile otomatik test
