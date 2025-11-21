# 🚀 HƯỚNG DẪN CHẠY PROJECT FASTAPI CHATBOT

## 📋 Yêu cầu

- Python 3.11+
- pip hoặc Docker
- API Keys:
  - `GEMINI_API_KEY` (Google Gemini AI)
  - `HUGGINGFACE_TOKEN` (HuggingFace embeddings)

---

## ⚙️ CÀI ĐẶT VÀ CHẠY

### Option 1: Chạy Local với Python (Khuyến nghị cho development)

#### Bước 1: Clone và vào thư mục project

```bash
cd e:\Documents\Projects_Myself\Chatbot_FastAPI
```

#### Bước 2: Tạo virtual environment

```bash
# Tạo venv
python -m venv venv

# Activate venv
# Windows (Git Bash):
source venv/Scripts/activate

# Windows (CMD):
venv\Scripts\activate

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Linux/Mac:
source venv/bin/activate
```

#### Bước 3: Cài đặt dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Bước 4: Cấu hình .env

```bash
# Copy template
cp .env.example .env

# Chỉnh sửa .env với editor (VS Code, Notepad++, etc.)
# Điền các giá trị sau:
```

File `.env` cần có:

```env
# Google Gemini API
GEMINI_API_KEY=your_actual_gemini_api_key_here

# HuggingFace API (cho embeddings)
HUGGINGFACE_TOKEN=your_actual_huggingface_token_here

# Server Configuration
BASE_URL=http://localhost:5000
HOST=0.0.0.0
PORT=5000

# Database (COMMENTED - not used yet)
# DATABASE_URL=postgresql://user:pass@localhost:5432/db_name
```

**Lấy API Keys:**

- **GEMINI_API_KEY**: https://ai.google.dev/gemini-api/docs/api-key
- **HUGGINGFACE_TOKEN**: https://huggingface.co/settings/tokens

#### Bước 5: Chạy server

```bash
# Chạy với uvicorn
uvicorn app:app --host 0.0.0.0 --port 5000 --reload

# Hoặc chạy trực tiếp file Python
python app.py
```

Server sẽ chạy tại: **http://localhost:5000**

#### Bước 6: Test API

Mở browser hoặc dùng curl:

```bash
# Test root endpoint
curl http://localhost:5000/

# Test health check
curl http://localhost:5000/health-check

# Test chat endpoint
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d "{\"prompt\": \"Xin chào, bạn là ai?\"}"
```

---

### Option 2: Chạy với Docker Compose

#### Bước 1: Cấu hình .env

```bash
cp .env.example .env
# Chỉnh sửa .env với GEMINI_API_KEY và HUGGINGFACE_TOKEN
```

#### Bước 2: Build và chạy

```bash
# Build và start container
docker compose up -d

# Xem logs
docker compose logs -f fastapi

# Test
curl http://localhost:5000/health-check
```

#### Bước 3: Dừng container

```bash
docker compose down
```

---

## 🧪 TEST API

### 1. Root Endpoint

```bash
curl http://localhost:5000/
```

Response:

```json
{
  "status": "ok",
  "message": "Fashion Chatbot API is running",
  "version": "1.0.0",
  "endpoints": {
    "chat": "POST /chat",
    "search": "POST /api/fashion/search",
    "health": "GET /health-check"
  }
}
```

### 2. Health Check

```bash
curl http://localhost:5000/health-check
```

Response:

```json
{
  "status": "ok",
  "message": "API is running (DB not connected)",
  "version": "1.0.0",
  "database_connected": false
}
```

### 3. Chat với Gemini AI

**Cách 1: Gửi prompt trực tiếp**

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d "{
    \"prompt\": \"Xin chào, bạn là ai?\",
    \"chatInput\": []
  }"
```

**Cách 2: Gửi chatInput (format frontend)**

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d "{
    \"chatInput\": [
      {\"role\": \"user\", \"content\": \"Xin chào, bạn là ai?\"}
    ],
    \"sessionId\": 123456
  }"
```

**Cách 3: Dùng file JSON (khuyến nghị)**

Tạo file `test_request.json`:

```json
{
  "chatInput": [{ "role": "user", "content": "Xin chào, bạn là ai?" }],
  "sessionId": 123456
}
```

Test:

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

Response:

```json
{
  "output": "Tôi là trợ lý AI thời trang, được thiết kế để hỗ trợ tư vấn...",
  "intent": "unknown"
}
```

### 4. Test Search Product Intent (tạm thời disabled)

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d "{
    \"prompt\": \"Tìm áo thun nam màu xanh\",
    \"chatInput\": []
  }"
```

Response:

```json
{
  "output": "Chức năng tìm kiếm sản phẩm tạm thời chưa khả dụng. Database đang được triển khai.",
  "intent": "search_product"
}
```

---

## 📁 CẤU TRÚC PROJECT

```
Chatbot_FastAPI/
├── app.py                      # Main FastAPI app (DB imports commented)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── .env                        # Your actual config (create this)
├── Dockerfile                  # Docker build config
├── docker-compose.yml          # Docker Compose (postgres commented)
│
├── ai_powered/
│   ├── __init__.py
│   ├── gemini.py               # Gemini chat logic (search_product commented)
│   ├── converter.py            # Text to vector embeddings
│   ├── load_docx.py            # Load DOCX knowledge base
│   └── build_docx_vector_db.py
│
├── routers/
│   ├── __init__.py
│   └── search.py               # Search router (fully commented)
│
├── db.py                       # Database connection (not used yet)
├── models.py                   # SQLAlchemy models (not used yet)
├── schemas.py                  # Pydantic schemas (not used yet)
│
└── media/                      # DOCX files for knowledge base
```

---

## 🔧 COMMENTED FEATURES (Chưa khả dụng)

### Database Search Product

Các phần sau đã được comment và sẽ bật lại khi database deploy:

1. **app.py**:

   - Import `sqlalchemy.orm.Session` (line 5)
   - Import `routers.search` (line 8)
   - Import `db.get_db, engine` (line 9)
   - Import `schemas.HealthCheckResponse` (line 10)
   - `app.include_router(search.router)` (line 27)
   - DB health check logic (lines 50-66)

2. **ai_powered/gemini.py**:

   - Product search API call (lines 112-135)
   - Replaced with mock message

3. **routers/search.py**:

   - Toàn bộ search endpoint (commented)
   - Chỉ giữ lại test endpoint

4. **docker-compose.yml**:
   - PostgreSQL service (commented)
   - DATABASE_URL environment (commented)
   - depends_on postgres (commented)

---

## 🔓 BẬT LẠI DATABASE SEARCH (Khi deploy)

### Bước 1: Uncomment code

1. **app.py** - Bỏ comment:

   ```python
   from sqlalchemy.orm import Session
   from routers import search
   from db import get_db, engine
   from schemas import HealthCheckResponse
   app.include_router(search.router)
   ```

2. **ai_powered/gemini.py** - Bỏ comment search logic:

   ```python
   # Uncomment lines 112-135
   ```

3. **routers/search.py** - Bỏ comment toàn bộ search endpoint

4. **docker-compose.yml** - Bỏ comment postgres service

### Bước 2: Setup database

```bash
# Chạy postgres
docker compose up -d postgres

# Chạy migration/init script
python generate_embeddings.py
```

### Bước 3: Restart API

```bash
docker compose restart fastapi
```

---

## 🐛 TROUBLESHOOTING

### Lỗi: "GEMINI_API_KEY not set"

```bash
# Kiểm tra .env file có tồn tại
ls .env

# Kiểm tra giá trị
cat .env | grep GEMINI_API_KEY

# Đảm bảo không có space
GEMINI_API_KEY=your_key_here  # ✓ Correct
GEMINI_API_KEY = your_key_here  # ✗ Wrong (có space)
```

### Lỗi: ModuleNotFoundError

```bash
# Cài lại dependencies
pip install -r requirements.txt

# Hoặc cài từng package thiếu
pip install fastapi uvicorn python-dotenv google-generativeai
```

### Lỗi: Port 5000 đã được sử dụng

```bash
# Tìm process đang dùng port 5000
# Windows:
netstat -ano | findstr :5000

# Linux/Mac:
lsof -i :5000

# Kill process hoặc đổi port trong .env
PORT=8000
```

### Container không start

```bash
# Xem logs
docker compose logs fastapi

# Rebuild
docker compose up -d --build

# Kiểm tra .env
cat .env
```

---

## 📝 LƯU Ý

- **Database search product** tạm thời disabled
- Chỉ cần **GEMINI_API_KEY** và **HUGGINGFACE_TOKEN**
- KHÔNG cần **GOOGLE_API_KEY** (đã loại bỏ)
- KHÔNG cần **DATABASE_URL** (chưa deploy DB)
- ChromaDB knowledge base vẫn hoạt động bình thường
- Intent classification vẫn hoạt động

---

## ✅ CHECKLIST

- [ ] Copy `.env.example` thành `.env`
- [ ] Điền `GEMINI_API_KEY` vào `.env`
- [ ] Điền `HUGGINGFACE_TOKEN` vào `.env`
- [ ] Activate virtual environment
- [ ] Cài `pip install -r requirements.txt`
- [ ] Chạy `uvicorn app:app --reload`
- [ ] Test `curl http://localhost:5000/health-check`
- [ ] Test chat endpoint với Gemini AI

---

## 🎯 NEXT STEPS

Sau khi database PostgreSQL được deploy:

1. Uncomment các phần DB trong code
2. Cấu hình `DATABASE_URL` trong `.env`
3. Chạy `python generate_embeddings.py`
4. Restart API server
5. Test search product endpoint

**Hiện tại chỉ cần chạy chatbot với Gemini AI, không cần database!** ✨
