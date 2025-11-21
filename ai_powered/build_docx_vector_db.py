import os
from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from ai_powered.converter import text_to_vector

# Custom embedding class cho LangChain sử dụng HuggingFace API
from langchain_core.embeddings import Embeddings

class HFHubAPIEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [text_to_vector(text) for text in texts]
    def embed_query(self, text):
        return text_to_vector(text)

# Đường dẫn file docx và nơi lưu vector db
DOCX_PATH = os.path.join('media', 'Shop_Information_For_Chatbot.docx')
CHROMA_PATH = os.path.join('chromadb_data')

# Hàm build vector db sử dụng langchain

def main():
    print('Đang đọc file docx...')
    loader = Docx2txtLoader(DOCX_PATH)
    documents = loader.load()
    print('Đang chia nhỏ nội dung...')
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)
    print(f'Tổng số đoạn: {len(docs)}')

    print('Đang tạo embedding và lưu vào ChromaDB...')
    embeddings = HFHubAPIEmbeddings()
    db = Chroma.from_documents(
        docs,
        embeddings,
        persist_directory=CHROMA_PATH,
        collection_name="shop_docx"
    )
    # Kiểm tra số lượng bản ghi sau khi build
    print('Số lượng đoạn đã lưu vào collection:', db._collection.count())
    # In ra một số đoạn đầu để kiểm tra
    all_docs = db.similarity_search("", k=5)
    for idx, doc in enumerate(all_docs):
        print(f"Đoạn {idx+1}: {doc.page_content}")
        print("-" * 40)
    print('Hoàn thành build vector database cho docx!')

if __name__ == '__main__':
    main()
