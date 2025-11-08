"""
LangChain setup for RAG (Retrieval-Augmented Generation) with FAISS vector store.
Handles embedding generation, vector store creation, and RAG chain initialization.
"""

import os
import csv
import hashlib
from pathlib import Path
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from function_tools import AVAILABLE_TOOLS


# Configuration
EMBEDDING_MODEL = "text-embedding-3-small"  # Will use env override in function
LLM_MODEL = "GPT-4o-mini"  # Will use env override in function

# Get the directory where this file is located (backend directory)
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_INDEX_PATH = os.path.join(BACKEND_DIR, "embeddings", "faiss_index")
HR_FAQ_PATH = os.path.join(BACKEND_DIR, "data", "hr_faq.csv")

# Load credentials dynamically (not at import time)
def get_credentials():
    """Get credentials from environment variables"""
    return {
        "embedding_api_key": os.getenv("AZURE_OPENAI_EMBEDDING_API_KEY", ""),
        "embedding_endpoint": os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT", ""),
        "embedding_model": os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small"),
        "llm_api_key": os.getenv("AZURE_OPENAI_LLM_API_KEY", ""),
        "llm_endpoint": os.getenv("AZURE_OPENAI_LLM_ENDPOINT", ""),
        "llm_model": os.getenv("AZURE_OPENAI_LLM_DEPLOYMENT", "GPT-4o-mini"),
    }

# Keep old variables for backward compatibility (used before function calls)
EMBEDDING_API_KEY = ""
EMBEDDING_ENDPOINT = ""
LLM_API_KEY = ""
LLM_ENDPOINT = ""


class SimpleHashEmbeddings(Embeddings):
    """Simple fallback embeddings using hash-based vectors"""
    def embed_documents(self, texts):
        """Embed search docs."""
        embeddings = []
        for text in texts:
            # Create a simple 384-dimensional vector based on hash
            hash_obj = hashlib.sha256(text.encode())
            hash_bytes = hash_obj.digest()
            # Convert bytes to 384-dim float vector
            embedding = []
            for i in range(384):
                byte_index = i % 32
                bit_offset = (i // 32) % 8
                byte_val = hash_bytes[byte_index]
                bit_val = (byte_val >> bit_offset) & 1
                # Normalize to [-1, 1] range
                embedding.append(float(bit_val) * 2 - 1)
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text):
        """Embed query text."""
        return self.embed_documents([text])[0]


class SimpleFallbackLLM:
    """Simple fallback LLM when Azure OpenAI is not available"""
    def __init__(self):
        self.responses_en = {
            "leave": "We offer 20 days of paid leave annually for full-time employees. Employees can carry over up to 5 days to the next year. Sick leave is provided separately at 10 days per year.",
            "benefits": "Our benefits package includes health insurance, dental coverage, vision insurance, and a 401(k) plan with a 4% company match.",
            "salary": "Salary reviews are conducted annually in January. Performance bonuses are distributed based on company performance and individual contributions.",
            "remote": "We support flexible work arrangements. Employees can work remotely up to 2 days per week with manager approval.",
            "policy": "Our company policies cover workplace conduct, confidentiality, anti-harassment, and ethics guidelines. Please refer to the employee handbook for details.",
        }
        self.responses_vi = {
            "leave": "Chúng tôi cung cấp 20 ngày nghỉ có lương hàng năm cho nhân viên toàn thời gian. Nhân viên có thể mang 5 ngày còn lại sang năm tiếp theo. Nghỉ ốm được cung cấp riêng biệt với 10 ngày mỗi năm.",
            "benefits": "Gói phúc lợi của chúng tôi bao gồm bảo hiểm y tế, bảo hiểm nha khoa, bảo hiểm thị lực và kế hoạch 401(k) với khoản đóng góp 4% của công ty.",
            "salary": "Xét tăng lương được tiến hành hàng năm vào tháng Giêng. Tiền thưởng hiệu suất được phân phối dựa trên hiệu suất công ty và đóng góp cá nhân.",
            "remote": "Chúng tôi hỗ trợ các sắp xếp công việc linh hoạt. Nhân viên có thể làm việc từ xa tối đa 2 ngày mỗi tuần với sự phê duyệt của quản lý.",
            "policy": "Các chính sách công ty của chúng tôi bao gồm quy tắc ứng xử tại nơi làm việc, bảo mật, chống qu騷rối và các hướng dẫn đạo đức. Vui lòng tham khảo sổ tay nhân viên để biết chi tiết.",
        }
    
    def invoke(self, messages):
        """Generate a simple response based on keywords in the message"""
        from langchain_core.messages import AIMessage
        
        # Combine all message content into one string
        combined_text = ""
        language = "en"
        for msg in messages:
            combined_text += msg.content.lower() + " "
        
        # Detect language from message content
        vi_keywords = ["tiếng việt", "việt", "vi", "vietnam", "hỏi", "về", "là gì", "làm sao", "như thế nào"]
        if any(keyword in combined_text for keyword in vi_keywords):
            language = "vi"
        
        # Select appropriate response dictionary
        responses = self.responses_vi if language == "vi" else self.responses_en
        
        # Find a matching response based on keywords
        best_response = None
        for keyword, response in responses.items():
            if keyword in combined_text:
                best_response = response
                break
        
        # If no keyword match, return a default response
        if not best_response:
            if language == "vi":
                best_response = "Cảm ơn bạn vì câu hỏi. Tôi là một Trợ lý HR dự phòng. Để biết thông tin cụ thể, vui lòng kiểm tra sổ tay nhân viên hoặc liên hệ với phòng HR trực tiếp."
            else:
                best_response = "Thank you for your question. I'm a fallback HR Assistant. For specific information, please check the employee handbook or contact HR directly."
        
        return AIMessage(content=best_response)


def load_hr_faq_documents() -> list[Document]:
    """
    Load HR FAQ data from CSV and convert to LangChain Documents.
    
    Returns:
        List of Document objects with HR Q&A pairs
    """
    documents = []
    
    if not os.path.exists(HR_FAQ_PATH):
        raise FileNotFoundError(f"HR FAQ file not found: {HR_FAQ_PATH}")
    
    with open(HR_FAQ_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Combine question and answer for better context
            content = f"Question: {row['Question']}\n\nAnswer: {row['Answer']}"
            doc = Document(
                page_content=content,
                metadata={
                    "source": "HR FAQ",
                    "question": row['Question'],
                    "type": "faq"
                }
            )
            documents.append(doc)
    
    return documents


def create_or_load_faiss_index(force_recreate: bool = False) -> FAISS:
    """
    Create a FAISS vector store from HR FAQ documents or load existing index.
    
    Args:
        force_recreate: If True, recreate the index even if it exists
    
    Returns:
        FAISS vector store instance
    """
    # Get credentials dynamically
    creds = get_credentials()
    embedding_api_key = creds["embedding_api_key"]
    embedding_endpoint = creds["embedding_endpoint"]
    embedding_model = creds["embedding_model"]
    
    # Try to use Azure OpenAI embeddings, fall back to simple hash embeddings
    embeddings = None
    
    if embedding_api_key and embedding_endpoint:
        try:
            print("[INFO] Attempting to use Azure OpenAI embeddings...")
            embeddings = AzureOpenAIEmbeddings(
                model=embedding_model,
                api_version="2023-05-15",
                azure_endpoint=embedding_endpoint,
                api_key=embedding_api_key,
            )
            print("[OK] Azure OpenAI embeddings initialized")
        except Exception as e:
            print(f"[WARNING] Azure embeddings failed ({str(e)[:80]}...), falling back to hash-based embeddings")
            embeddings = SimpleHashEmbeddings()
    else:
        print("[WARNING] No Azure embedding credentials found, using hash-based embeddings")
        embeddings = SimpleHashEmbeddings()
    
    # Check if FAISS index already exists
    index_path = Path(FAISS_INDEX_PATH)
    if index_path.exists() and not force_recreate:
        print(f"Loading existing FAISS index from {FAISS_INDEX_PATH}")
        try:
            faiss_store = FAISS.load_local(
                FAISS_INDEX_PATH,
                embeddings,
                allow_dangerous_deserialization=True
            )
            return faiss_store
        except Exception as e:
            print(f"Error loading existing index: {e}. Creating new index...")
    
    # Create new FAISS index
    print("Creating new FAISS index from HR FAQ documents...")
    
    # Load HR FAQ documents
    documents = load_hr_faq_documents()
    print(f"Loaded {len(documents)} HR FAQ documents")
    
    # Split documents into chunks for better retrieval
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    
    # Try to create FAISS vector store with current embeddings
    # If Azure embeddings fail, fall back to simple hash embeddings
    try:
        print("[INFO] Creating FAISS index with current embeddings...")
        faiss_store = FAISS.from_documents(chunks, embeddings)
    except Exception as e:
        print(f"[WARNING] Failed to create embeddings ({str(e)[:80]}...), falling back to hash-based embeddings")
        embeddings = SimpleHashEmbeddings()
        faiss_store = FAISS.from_documents(chunks, embeddings)
    
    # Try to save the index (but don't fail if it doesn't work)
    try:
        os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
        faiss_store.save_local(FAISS_INDEX_PATH)
        print(f"FAISS index saved to {FAISS_INDEX_PATH}")
    except Exception as save_error:
        print(f"[WARNING] Could not save FAISS index to disk ({str(save_error)[:60]}...), using in-memory index only")
    
    return faiss_store


def setup_rag_chain(vector_store: FAISS):
    """
    Set up the LLM with function calling support for RAG.
    
    Args:
        vector_store: FAISS vector store instance
    
    Returns:
        Tuple of (llm, retriever) for use in chat
    """
    # Get credentials dynamically
    creds = get_credentials()
    llm_api_key = creds["llm_api_key"]
    llm_endpoint = creds["llm_endpoint"]
    llm_model = creds["llm_model"]
    
    # Try to use Azure OpenAI, fallback to simple LLM if it fails
    llm = None
    if llm_api_key and llm_endpoint:
        try:
            print("[INFO] Attempting to initialize Azure OpenAI LLM...")
            llm = AzureChatOpenAI(
                model=llm_model,
                temperature=0.7,
                api_version="2023-05-15",
                azure_endpoint=llm_endpoint,
                api_key=llm_api_key,
            )
            print("[OK] Azure OpenAI LLM initialized")
        except Exception as e:
            print(f"[WARNING] Failed to initialize Azure OpenAI LLM: {str(e)[:100]}")
            print("[INFO] Falling back to simple LLM")
            llm = SimpleFallbackLLM()
    else:
        print("[WARNING] Azure OpenAI LLM credentials not found, using fallback LLM")
        llm = SimpleFallbackLLM()
    
    # Set up retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    return llm, retriever


def initialize_rag_system() -> tuple[FAISS, tuple]:
    """
    Complete initialization of the RAG system.
    
    Returns:
        Tuple of (FAISS vector store, (llm, retriever))
    """
    print("Initializing RAG system...")
    
    try:
        # Create or load FAISS index (don't force recreate, use existing if available)
        vector_store = create_or_load_faiss_index(force_recreate=False)
        
        # Set up RAG components
        llm, retriever = setup_rag_chain(vector_store)
        
        print("RAG system initialized successfully!")
        return vector_store, (llm, retriever)
    except Exception as e:
        print(f"[ERROR] Failed to initialize RAG system: {str(e)}")
        print("[INFO] Creating fallback FAISS index with hash embeddings...")
        
        try:
            # Force use of hash embeddings
            embeddings = SimpleHashEmbeddings()
            documents = load_hr_faq_documents()
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=100,
                separators=["\n\n", "\n", " ", ""]
            )
            chunks = text_splitter.split_documents(documents)
            
            vector_store = FAISS.from_documents(chunks, embeddings)
            llm = SimpleFallbackLLM()
            retriever = vector_store.as_retriever(search_kwargs={"k": 3})
            
            print("[OK] Fallback RAG system initialized!")
            return vector_store, (llm, retriever)
        except Exception as fallback_e:
            print(f"[CRITICAL] Fallback RAG initialization failed: {str(fallback_e)}")
            raise
