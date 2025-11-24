from fastapi import FastAPI, HTTPException  # , Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request
from pydantic import BaseModel
from typing import Optional, List, Dict
# from sqlalchemy.orm import Session  # COMMENTED: DB not deployed yet

from ai_powered.gemini import process_gemini_chat
# from routers import search  # COMMENTED: DB search not ready
# from db import get_db, engine  # COMMENTED: DB not deployed yet
# from schemas import HealthCheckResponse  # COMMENTED: DB dependent

app = FastAPI(
    title="Fashion Chatbot API",
    description="AI-powered chatbot for fashion shopping assistance",
    version="1.0.0"
)

# Custom exception handler để trả về format {"message": ...} thay vì {"detail": ...}
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}  # FE mong đợi key 'message'
    )

# Cho phép FE Next.js gọi API (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # production nên chỉnh domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# COMMENTED: DB search not ready yet - uncomment when DB is deployed
# app.include_router(search.router)

class ChatRequest(BaseModel):
    prompt: Optional[str] = None  # Optional vì frontend có thể chỉ gửi chatInput
    chatInput: Optional[List[Dict]] = None
    sessionId: Optional[int] = None  # Frontend gửi thêm sessionId

@app.get("/")
async def root():
    """Root endpoint - basic info"""
    return {
        "status": "ok",
        "message": "Fashion Chatbot API is running",
        "version": "1.0.0",
        "endpoints": {
            "chat": "POST /chat",
            "search": "POST /api/fashion/search",
            "health": "GET /health-check"
        }
    }


@app.get("/health-check")  # , response_model=HealthCheckResponse)
async def health_check():  # db: Session = Depends(get_db)):
    """
    Health check endpoint - verify API status.
    
    COMMENTED: Database connection check disabled until DB is deployed.
    Uncomment db parameter and connection test when ready.
    
    Returns:
        Dict with status, message, version
    """
    # COMMENTED: DB not deployed yet
    # try:
    #     db.execute("SELECT 1")
    #     db_connected = True
    # except Exception as e:
    #     db_connected = False
    
    # return HealthCheckResponse(
    #     status="ok" if db_connected else "degraded",
    #     message="API is running" if db_connected else f"API running but database connection failed",
    #     version="1.0.0",
    #     database_connected=db_connected
    # )
    
    # Temporary response without DB check
    return {
        "status": "ok",
        "message": "API is running (DB not connected)",
        "version": "1.0.0",
        "database_connected": False
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint - xử lý câu hỏi của người dùng với Gemini AI
    
    - **prompt**: Câu hỏi của người dùng (optional nếu có chatInput)
    - **chatInput**: Lịch sử chat (optional)
    - **sessionId**: Session ID từ frontend (optional)
    """
    try:
        # Gọi function xử lý Gemini chat - để gemini.py tự trích xuất prompt
        result = process_gemini_chat(
            prompt=request.prompt,  # Có thể None, gemini.py sẽ xử lý
            chat_input=request.chatInput
        )
        
        # Kiểm tra kết quả - xử lý error
        if 'error' in result:
            raise HTTPException(
                status_code=result.get('status', 500),
                detail=result['error']
            )
        
        # Thành công - trả về output và intent
        return {
            "output": result.get('output', ''),
            "intent": result.get('intent', 'unknown')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
