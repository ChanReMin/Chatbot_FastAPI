# 🤖 Fashion Chatbot FastAPI

AI-powered chatbot for fashion shopping assistance using FastAPI, Google Gemini AI, and HuggingFace embeddings.

## 📁 Cấu trúc project

```
Chatbot_FastAPI/
├── app.py                  # Main FastAPI application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
├── ai_powered/           # AI modules
│   ├── __init__.py
│   ├── converter.py      # Text to vector embedding (HuggingFace)
│   ├── gemini.py         # Gemini AI chat processing
│   ├── load_docx.py      # Load DOCX files
│   └── build_docx_vector_db.py  # Build ChromaDB from DOCX
└── media/                # Media files (DOCX, images)
```

## 🚀 Tính năng

- **Intent Classification**: Tự động phân loại câu hỏi (tìm sản phẩm, tra cứu kiến thức)
- **Product Search**: Tìm kiếm sản phẩm thời trang
- **RAG (Retrieval-Augmented Generation)**: Tra cứu kiến thức từ ChromaDB
- **Gemini AI Integration**: Sử dụng Google Gemini 2.0 Flash
- **HuggingFace Embeddings**: Vector embedding cho semantic search
- **CORS Support**: Hỗ trợ frontend (Next.js, React, etc.)

## 📋 Yêu cầu

- Python 3.11+
- Docker & Docker Compose (optional)
- HuggingFace API Token
- Google Gemini API Key

## ⚙️ Cài đặt

### 1. Clone repository

```bash
cd Chatbot_FastAPI
```

### 2. Tạo file .env

```bash
cp .env.example .env
```

Sau đó điền các API keys vào file `.env`:

```env
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxxxxxxx
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxx
BASE_URL=http://localhost:5000
```

### 3. Cài đặt dependencies (không dùng Docker)

```bash
# Tạo virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 4. Build ChromaDB (optional)

Nếu bạn có file DOCX trong `media/`, chạy script để build vector database:

```bash
python ai_powered/build_docx_vector_db.py
```

## 🐳 Chạy với Docker (Khuyến nghị)

### Build và chạy

```bash
# Build image
docker compose build

# Chạy container
docker compose up -d

# Xem logs
docker compose logs -f

# Dừng container
docker compose down
```

### Chạy thủ công với Docker

```bash
# Build image
docker build -t chatbot-fastapi .

# Run container
docker run -d \
  -p 5000:5000 \
  --env-file .env \
  --name chatbot \
  chatbot-fastapi

# View logs
docker logs -f chatbot

# Stop container
docker stop chatbot
docker rm chatbot
```

## 💻 Chạy Local (không Docker)

```bash
# Activate virtual environment
# Windows
venv\Scripts\activate

# Chạy server
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

Server sẽ chạy tại: `http://localhost:5000`

## 📡 API Endpoints

### GET `/`

Health check endpoint

**Response:**

```json
{
  "status": "ok",
  "message": "Fashion Chatbot API is running",
  "version": "1.0.0"
}
```

### POST `/chat`

Main chat endpoint

**Request:**

```json
{
  "prompt": "Tìm áo thun nam",
  "chatInput": [
    { "role": "user", "content": "Xin chào" },
    { "role": "assistant", "content": "Chào bạn!" }
  ]
}
```

**Response:**

```json
{
  "answer": "Dưới đây là các sản phẩm phù hợp...",
  "intent": "search_product"
}
```

## 🔧 Cấu hình

### Environment Variables

| Variable            | Description           | Required                     |
| ------------------- | --------------------- | ---------------------------- |
| `HUGGINGFACE_TOKEN` | HuggingFace API token | ✅ Yes                       |
| `GOOGLE_API_KEY`    | Google Gemini API key | ✅ Yes                       |
| `BASE_URL`          | Backend base URL      | No (default: localhost:5000) |
| `DEBUG`             | Debug mode            | No (default: True)           |

### Modules

#### `converter.py`

- Convert text to vector embeddings using HuggingFace
- Model: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)

#### `gemini.py`

- Intent classification
- Product search integration
- ChromaDB knowledge retrieval
- Gemini AI chat processing

#### `load_docx.py`

- Load and parse DOCX files

#### `build_docx_vector_db.py`

- Build ChromaDB from DOCX files
- Split text into chunks (400 chars, 50 overlap)

## 🧪 Testing

```bash
# Test health endpoint
curl http://localhost:5000/

# Test chat endpoint
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tìm áo thun nam"}'
```

## 🛠️ Development

### Code style

- Đơn giản, dễ hiểu
- Type hints cho functions
- Docstrings cho các function chính
- Error handling đầy đủ

### Tối ưu

- Lazy loading cho AI models
- Cache ChromaDB instance
- Environment variables cho configuration
- Docker multi-stage builds (có thể thêm)

## 📝 Notes

- Project được chuyển đổi từ Django sang FastAPI
- Giữ nguyên chức năng và cấu trúc code
- Tất cả dependencies đã được thêm vào `requirements.txt`
- ChromaDB data được lưu trong `chromadb_data/`
- Media files (DOCX) nên đặt trong `media/`

## 🤝 Contributing

1. Tạo feature branch
2. Commit changes
3. Push và tạo Pull Request

## 📄 License

MIT License
