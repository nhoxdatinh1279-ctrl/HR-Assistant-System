# 🚀 Tóm Tắt Các Kỹ Thuật Sử Dụng Trong Project

## 📋 Tổng Quan Project
**HR Assistant Chatbot** - Ứng dụng AI hỗ trợ nhân sự với RAG (Retrieval-Augmented Generation), đánh giá CV, và chatbot đa ngôn ngữ.

---

## 🏗️ Architecture & Framework

### Backend
- **FastAPI** - Web framework Python hiệu suất cao
- **Uvicorn** - ASGI server cho FastAPI
- **Pydantic** - Data validation và serialization
- **Python-dotenv** - Quản lý environment variables

### Frontend  
- **Next.js 14.2.33** - React framework với SSR
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Icon library
- **Axios** - HTTP client cho API calls

---

## 🤖 AI/ML Technologies

### LLM & Embeddings
- **Azure OpenAI** - GPT models cho language generation
  - Embedding Model: text-embedding-ada-002
  - LLM Model: gpt-35-turbo
  - Fallback: GPT-5-mini (khi Azure không khả dụng)

- **LangChain** - Framework orkestrasi AI
  - `AzureOpenAIEmbeddings` - Tạo embeddings
  - `AzureChatOpenAI` - LLM interface
  - `RecursiveCharacterTextSplitter` - Text chunking
  - Message types: HumanMessage, SystemMessage, AIMessage

### Vector Databases
- **FAISS** (Facebook AI Similarity Search)
  - In-memory vector store cho semantic search
  - `FAISS.from_documents()` - Tạo index
  - Retriever pattern cho context retrieval
  - Hash-based embeddings fallback

### NLP & Document Processing
- **PyPDF2** - PDF extraction
- **python-docx** - DOCX file handling
- **CSV** - FAQ database format

---

## 🧠 Core Features & Techniques

### 1. RAG System (Retrieval-Augmented Generation)
```
User Query → Embeddings → FAISS Search → Retrieve Docs → LLM Context → Response
```
**Công nghệ:**
- Vector embedding cho semantic understanding
- Similarity search để lấy tài liệu liên quan
- Context injection vào LLM prompt
- Source documents attribution

### 2. CV Evaluation Engine
**Kỹ thuật matching:**
- Keyword detection với synonyms
- Multi-word skill matching
- Score calculation:
  - Must-have skills: 15 điểm/cái
  - Nice-to-have skills: 5 điểm/cái
  - Experience: 20 điểm (Senior/Lead)
  - Education: 25 điểm (Master degree)
  - Soft skills: 10 điểm

**Intelligent matching:**
```
"machine learning" → ["ML", "AI", "artificial intelligence", "predictive"]
"llm" → ["LLM", "language model", "GPT", "generative AI", "RAG"]
```

### 3. Multi-Language Support
- **Language Detection** - Tự động nhận dạng từ keywords
- **Response Localization** - Trả lời theo ngôn ngữ yêu cầu
- **Supported Languages:**
  - English (English)
  - Vietnamese (Tiếng Việt)
  
**Implementation:**
```python
if language == "vi":
    # Vietnamese response
else:
    # English response
```

### 4. Fallback Mechanisms
- **SimpleFallbackLLM** - Fallback khi Azure OpenAI lỗi
- **SimpleHashEmbeddings** - Hash-based vectors khi Azure embedding fail
- **In-memory FAISS** - Lưu vector store trong RAM (không cần disk)
- **Graceful degradation** - App hoạt động ở chế độ giới hạn thay vì crash

---

## 📊 Data Processing Pipeline

### FAQ Dataset
- **Source**: `data/hr_faq.csv`
- **Format**: CSV với Question/Answer pairs
- **Processing**:
  1. Load từ CSV
  2. Split thành chunks (500 chars, 100 overlap)
  3. Tạo embeddings cho mỗi chunk
  4. Lưu vào FAISS index

### Document Extraction
- **PDF**: PyPDF2 với base64 encoding/decoding
- **DOCX**: python-docx library
- **Text**: Direct text parsing
- **Encoding**: Base64 cho transmission qua network

---

## 🔌 API Design

### RESTful Endpoints
```
POST /api/chat                    # Main chat endpoint
GET  /api/health                  # Health check
POST /api/init                    # RAG system initialization
GET  /api/faq                     # FAQ statistics
POST /api/evaluate-cv             # Direct CV evaluation
GET  /api/job-positions           # List job positions
POST /api/evaluate-cv-for-position # Position-specific evaluation
```

### Request/Response Pattern
```python
# Chat Request
{
    "message": "string",
    "session_id": "string",
    "language": "en|vi"
}

# Chat Response
{
    "answer": "string",
    "source_documents": [
        {
            "content": "string",
            "source": "string",
            "question": "string"
        }
    ],
    "function_calls": ["string"]
}
```

---

## 🛡️ Error Handling & Resilience

### Multi-Level Fallbacks
1. **Azure OpenAI** (Primary)
2. **SimpleFallbackLLM** (Secondary)
3. **get_fallback_response()** (Tertiary)

### File Handling
- Try/catch for FAISS save operations
- In-memory index if disk write fails
- Directory creation with error handling

### Request Validation
- Pydantic models for schema validation
- Empty message checks
- Language parameter validation

---

## 🎯 Advanced Techniques

### Semantic Search
- Vector similarity using FAISS
- Context-aware retrieval
- Multi-document ranking

### Prompt Engineering
- System prompts with role definition
- User context injection
- Language-specific instructions

### CV Scoring Algorithm
- Weighted skill matching (15pts, 5pts)
- Flexible requirements (50% threshold)
- Experience level detection
- Education qualification scoring

### Language Model Integration
- Message-based interface
- System + User prompts
- Token efficiency
- Error recovery

---

## 📈 Performance & Optimization

### Caching & Indexing
- FAISS pre-computed index
- Hash-based embeddings for speed
- In-memory storage
- Lazy loading của documents

### Scalability
- Stateless API design
- No session persistence
- Parallel CV processing
- Async-ready FastAPI

---

## 🔐 Security Features

### Input Validation
- Message length checking
- File type validation
- Base64 encoding for file transmission
- Sanitization của keywords

### Data Privacy
- No persistent storage of CV content
- Session-level isolation
- Environment-based secrets
- Error message sanitization

---

## 📦 Dependencies Summary

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Backend** | FastAPI, Uvicorn | Web server |
| **Frontend** | Next.js, Tailwind | UI/UX |
| **AI/ML** | LangChain, Azure OpenAI | Language models |
| **Vector DB** | FAISS | Semantic search |
| **NLP** | PyPDF2, python-docx | Document processing |
| **Data** | Pydantic, python-dotenv | Config & validation |

---

## 🚀 Key Achievements

✅ **RAG System** - Retrieval-Augmented Generation for context-aware responses
✅ **Multi-Language** - English/Vietnamese support with auto-detection
✅ **CV Evaluation** - Intelligent skill matching with 50+ keyword synonyms
✅ **Fallback Mechanisms** - Graceful degradation when services unavailable
✅ **Modern Stack** - FastAPI + Next.js + LangChain
✅ **Scalable Design** - Stateless, async-ready architecture
✅ **Smart Matching** - Semantic understanding beyond keyword matching

---

## 🎓 Learning Outcomes

Dự án này demonstration các kỹ năng:
- **LLM Integration** - Azure OpenAI API usage
- **Vector Databases** - FAISS indexing và retrieval
- **Full Stack Development** - Backend (Python) + Frontend (React)
- **NLP Techniques** - Embedding, semantic search, prompt engineering
- **System Design** - Error handling, fallbacks, resilience
- **Multi-language Support** - Localization at scale
- **RESTful API Design** - Proper endpoint design and validation
- **Modern Web Development** - Next.js, Tailwind, FastAPI

---

## 🔗 Related Technologies

- **Azure Services**: OpenAI API, deployment models
- **Python Ecosystem**: LangChain, FAISS, FastAPI
- **Web Stack**: Next.js, React, Tailwind CSS
- **DevOps**: Environment management, Docker-ready
- **NLP**: Embeddings, semantic similarity, prompt engineering

---

*Tài liệu được tạo: 08/11/2025*
