import os
import requests
import re
from typing import List, Dict, Optional
from .load_docx import load_docx_content
from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings
from ai_powered.converter import text_to_vector
from ai_powered.wine_service import search_wines_service
from db import ReadSessionLocal

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Đọc nội dung file Word một lần khi khởi động server
# try:
#     DOCX_KNOWLEDGE = load_docx_content("media/Shop_Information_For_Chatbot.docx")
# except Exception as e:
#     DOCX_KNOWLEDGE = ""
#     print(f"Warning: Could not load DOCX file: {e}")

def classify_intent(prompt: str) -> str:
    """Phân loại ý định của người dùng"""
    prompt_lower = prompt.lower()
    
    # Intent tìm sản phẩm
    product_keywords = [
    # --- Vietnamese ---
    "tìm", "mua", "sản phẩm", "gợi ý", "giới thiệu", "phù hợp", "đề xuất", "rượu", "vang", "chai", "loại", "xem", "chi tiết", "đỏ", "trắng", "hồng", "sparkling", "champagne", "ngọt", "đậm", "chát",

    # --- English ---
    "find", "buy", "product", "suggest", "recommend", "recommendation", "suitable", "introduce", "wine", "red", "white", "rose", "sparkling", "champagne", "bottle", "type", "view", "detail", "sweet", "dry", "bold", "tannic", "fruity",]
    if any(kw in prompt_lower for kw in product_keywords):
        print(f"[INTENT RULE] User hỏi: {prompt} => search_product")
        return "search_product"
    
    # Intent tra cứu kiến thức (ChromaDB)
    knowledge_keywords = ["chính sách", "đổi trả", "vận chuyển", "khuyến mãi", "liên hệ", "hỗ trợ", "faq", "hướng dẫn", "cửa hàng", "địa chỉ"]
    if any(kw in prompt_lower for kw in knowledge_keywords):
        print(f"[INTENT RULE] User hỏi: {prompt} => search_knowledge")
        return "search_knowledge"
    
    # Fallback: HuggingFace Inference API (cloud)
    api_key = os.getenv("HUGGINGFACE_TOKEN", "")
    if api_key:
        url = "https://api-inference.huggingface.co/models/joeddav/xlm-roberta-large-xnli"
        headers = {"Authorization": f"Bearer {api_key}"}
        candidate_labels = ["search_product", "search_knowledge", "other"]
        payload = {
            "inputs": prompt,
            "parameters": {"candidate_labels": candidate_labels}
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                best_label = result["labels"][0]
                best_score = result["scores"][0]
                print(f"[INTENT HF API] User hỏi: {prompt} => {best_label} (score={best_score:.2f})")
                if best_score > 0.5 and best_label != "other":
                    return best_label
        except Exception as e:
            print(f"[INTENT HF API ERROR] User hỏi: {prompt} => {e}")
    print(f"[INTENT UNKNOWN] User hỏi: {prompt} => unknown")
    return "unknown"

class HFHubAPIEmbeddings(Embeddings):
    """Custom embedding class cho LangChain sử dụng HuggingFace API"""
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [text_to_vector(text) for text in texts]
    
    def embed_query(self, text: str) -> List[float]:
        return text_to_vector(text)


def process_gemini_chat(prompt: str, chat_input: Optional[List[Dict]] = None) -> Dict:
    """Xử lý chat với Gemini AI - FastAPI compatible
    
    Args:
        prompt: Câu hỏi của người dùng (có thể None nếu chỉ có chat_input)
        chat_input: Lịch sử chat dạng [{"role": "user"|"assistant", "content": "..."}]
    
    Returns:
        Dict chứa output, intent và status
    """
    # Validate chat_input format nếu có
    if chat_input is not None:
        if not isinstance(chat_input, list):
            return {'error': 'chat_input must be a list', 'status': 400}
        for msg in chat_input:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                return {'error': 'Invalid chat_input format. Each message must have "role" and "content"', 'status': 400}
    
    # Trích xuất prompt từ chatInput nếu không có
    if not prompt:
        if isinstance(chat_input, list) and len(chat_input) > 0:
            # Lấy message cuối cùng từ user
            last_user = next((msg for msg in reversed(chat_input) if msg.get('role') == 'user'), None)
            if last_user:
                prompt = last_user.get('content')
        
        if not prompt:
            return {'error': 'No prompt provided', 'status': 400}
    
    # LUÔN xây dựng history_text nếu có chat_input (FIX BUG: tránh mất context)
    history_text = ''
    if isinstance(chat_input, list) and len(chat_input) > 0:
        # Lấy 5 tin nhắn gần nhất để tiết kiệm token
        recent_messages = chat_input[-5:]
        for msg in recent_messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            # Sanitize: giới hạn độ dài mỗi message
            content = content[:2000] if content else ''
            
            if role == 'user':
                history_text += f"Người dùng: {content}\n"
            elif role == 'assistant':
                history_text += f"Trợ lý: {content}\n"

    # Phân loại intent
    intent = classify_intent(prompt)
    product_list_text = ''
    knowledge_text = ''
    answer = None
    products_data = []  # Lưu data sản phẩm cho mobile

    if intent == "search_product":
        try:
            # Create database session
            db = ReadSessionLocal()
            try:
                # Call service layer directly (no HTTP overhead)
                products = search_wines_service(prompt, db)
                
                # Lưu products data cho mobile app
                products_data = products if products else []
                
                if products:
                    # Lấy FRONTEND_URL từ .env (mặc định localhost:3000)
                    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
                    
                    # Build compact single-line HTML list
                    product_items = []
                    for p in products:
                        # Format price: remove .0 and add thousand separator
                        price = p.get('price', 0)
                        formatted_price = f"{int(price):,}".replace(',', '.') if price else 'N/A'
                        
                        # Build compact single-line product item (NO <br> tags)
                        item_html = (
                            f"<li style='margin-bottom: 8px;'>"
                            f"<b>{p.get('name', 'Sản phẩm')}</b>: "
                            f"<i style='color: #666;'>{p.get('description', 'Không có mô tả')}</i> - "
                            f"<b style='color: #d32f2f;'>{formatted_price} đ</b> | "
                            f"<a href='{frontend_url}/en/shop/{p.get('id', '')}/{p.get('slug', '')}' target='_blank' rel='noopener noreferrer' style='color: #1976d2; text-decoration: none; font-weight: bold;'>👉 Xem ngay</a>"
                            f"</li>"
                        )
                        product_items.append(item_html)
                    
                    product_list_html = ''.join(product_items)
                    product_list_text = f"Dưới đây là các sản phẩm phù hợp:<ul style='padding-left: 20px; list-style-type: disc;'>{product_list_html}</ul>"
                else:
                    product_list_text = "Không tìm thấy sản phẩm phù hợp."
            finally:
                db.close()
        except Exception as e:
            product_list_text = f"Lỗi khi tìm kiếm sản phẩm: {str(e)}"
    elif intent == "search_knowledge":
        # Tìm kiếm vector trong ChromaDB
        try:
            CHROMA_PATH = "chromadb_data"
            collection_name = "shop_docx"
            embeddings = HFHubAPIEmbeddings()
            db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings, collection_name=collection_name)
            # Truy vấn top 3 đoạn liên quan nhất
            results = db.similarity_search(prompt, k=3)
            if results:
                knowledge_text = "Dưới đây là thông tin liên quan:\n" + "\n\n".join([doc.page_content for doc in results])
            else:
                knowledge_text = "Không tìm thấy thông tin phù hợp trong dữ liệu cửa hàng."
        except Exception as e:
            knowledge_text = f"Lỗi khi tìm kiếm trong database: {str(e)}"
    else:
        answer = "Xin lỗi, tôi chỉ hỗ trợ các câu hỏi liên quan đến rượu vang, tư vấn hương vị hoặc chính sách cửa hàng."

    # Xây dựng prompt cho AI
    fashion_instruction = (
        "Luôn ưu tiên trả lời dựa trên thông tin dưới đây nếu có. "
        "Nếu không có thông tin liên quan, chỉ trả lời các câu hỏi về rượu vang, tư vấn rượu, hương vị và gợi ý sản phẩm phù hợp."
        "Nếu người dùng hỏi 'chatbot là gì' hoặc các câu hỏi tương tự về bản thân bạn, hãy trả lời: "
        "'Tôi là trợ lý AI của WineStore, được thiết kế để hỗ trợ tư vấn lựa chọn rượu vang và các nội dung liên quan đến bán rượu.'"
        "\nNếu có danh sách rượu vang bên dưới, hãy luôn hiển thị lại rõ ràng cho người dùng, không được bỏ qua hoặc trả lời chung chung."
        "\nNếu người dùng trả lời ngắn gọn (ví dụ: 'có', 'chai đầu', 'loại 2', 'xem chi tiết', 'vang đỏ', 'loại trắng'), "
        "hãy dựa vào câu hỏi cuối cùng của bạn trong lịch sử hội thoại để hiểu ý định và trả lời đúng trọng tâm."
    )
    prompt_for_ai = f"{fashion_instruction}\n\n"
    if history_text:
        prompt_for_ai += f"Lịch sử hội thoại:\n{history_text}\n"
    if product_list_text:
        prompt_for_ai += f"{product_list_text}\n\n"
    if knowledge_text:
        prompt_for_ai += f"{knowledge_text}\n\n"
    prompt_for_ai += f"Câu hỏi hiện tại: {prompt}"

    # Gọi Gemini AI
    api_key = os.getenv('GEMINI_API_KEY', '')
    if not api_key:
        return {'error': 'GEMINI_API_KEY not set in backend environment', 'status': 500}
    
    if genai is None:
        return {'error': 'google-generativeai not installed', 'status': 500}
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        response = model.generate_content(prompt_for_ai)
        answer = response.text
        
        # Chuyển markdown link [text](url) thành thẻ <a> nếu AI sinh ra markdown
        answer = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r"<a href='\2' target='_blank' rel='noopener noreferrer'>\1</a>", answer)
        
        return {
            'output': answer,
            'intent': intent,
            'products': products_data,  # Thêm products data cho mobile
            'status': 200
        }
    except Exception as e:
        return {
            'error': f'Gemini API error: {str(e)}',
            'status': 500
        }
