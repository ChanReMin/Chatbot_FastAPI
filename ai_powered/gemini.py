import os
import requests
import re
from typing import List, Dict, Optional
from .load_docx import load_docx_content
from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings
from ai_powered.converter import text_to_vector

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Đọc nội dung file Word một lần khi khởi động server
try:
    DOCX_KNOWLEDGE = load_docx_content("media/Shop_Information_For_Chatbot.docx")
except Exception as e:
    DOCX_KNOWLEDGE = ""
    print(f"Warning: Could not load DOCX file: {e}")

# Lấy BASE_URL từ biến môi trường
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

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
        prompt: Câu hỏi của người dùng
        chat_input: Lịch sử chat (optional)
    
    Returns:
        Dict chứa output, intent và status
    """
    if not prompt:
        # Hỗ trợ lấy prompt từ chatInput (kiểu mới của frontend)
        history_text = ''
        if isinstance(chat_input, list) and len(chat_input) > 0:
            # Lấy message cuối cùng của user để phân loại intent
            last_user = next((msg for msg in reversed(chat_input) if msg.get('role') == 'user'), None)
            if last_user:
                prompt = last_user.get('content')

            recent_messages = chat_input[-5:]
            # Xây dựng lịch sử hội thoại cho AI
            for msg in recent_messages:
                if msg['role'] == 'user':
                    history_text += f"Người dùng: {msg['content']}\n"
                else:
                    history_text += f"Trợ lý: {msg['content']}\n"
        if not prompt:
            return {'error': 'No prompt provided', 'status': 400}
    else:
        history_text = ''

    # Phân loại intent
    intent = classify_intent(prompt)
    product_list_text = ''
    knowledge_text = ''
    answer = None

    if intent == "search_product":
        # COMMENTED: DB search not ready yet - uncomment when DB is deployed
        # try:
        #     # Call internal FastAPI search endpoint (localhost)
        #     search_url = f'{BASE_URL}/api/fashion/search'
        #     resp = requests.post(search_url, json={'query': prompt}, timeout=10)
        #     if resp.status_code == 200:
        #         products = resp.json()
        #         if products:
        #             product_list_text = '\n'.join([
        #                 f"- {p.get('name', '')}: {p.get('description', '')} (Giá: {p.get('price', 'N/A')}) [Xem thêm](...)" for p in products
        #             ])
        #             product_list_text = f"Dưới đây là các sản phẩm phù hợp:\n{product_list_text}"
        #         else:
        #             product_list_text = "Không tìm thấy sản phẩm phù hợp."
        #     else:
        #         product_list_text = f"Không thể lấy dữ liệu sản phẩm (status {resp.status_code})."
        # except Exception as e:
        #     product_list_text = f"Lỗi khi tìm kiếm sản phẩm: {str(e)}"
        
        # Temporary mock response until DB is ready
        product_list_text = "Chức năng tìm kiếm sản phẩm tạm thời chưa khả dụng. Database đang được triển khai."
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

    # Tìm lại gợi ý sản phẩm gần nhất trong lịch sử chat nếu không có product_list_text mới
    last_product_suggestion = ""
    if not product_list_text and isinstance(chat_input, list):
        for msg in reversed(chat_input):
            if msg.get('role') == 'assistant' and "Dưới đây là các sản phẩm phù hợp" in msg.get('content', ''):
                last_product_suggestion = msg['content']
                break
    if not product_list_text and last_product_suggestion:
        product_list_text = last_product_suggestion

    # ĐẢM BẢO: Nếu product_list_text có giá trị, luôn đưa vào prompt_for_ai
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
        return {'message': 'GEMINI_API_KEY not set in backend environment', 'status': 500}
    
    if genai is None:
        return {'message': 'google-generativeai not installed', 'status': 500}
    
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
            'status': 200
        }
    except Exception as e:
        return {
            'message': str(e),
            'status': 500
        }
