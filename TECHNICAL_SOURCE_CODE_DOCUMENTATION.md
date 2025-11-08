# 📚 Technical Source Code Documentation

## 🎯 Project Overview

**HR Assistant System** is an AI-powered HR chatbot with CV evaluation using:
- **RAG (Retrieval-Augmented Generation)** for intelligent Q&A
- **Azure OpenAI** for natural language processing
- **FAISS** for vector similarity search
- **Multi-language Support** (English/Vietnamese)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                       │
│                    (Next.js React App)                      │
│  - ChatBox Component   - CVUpload Component                 │
│  - Language Toggle     - Message Display                    │
└─────────────────────────┬─────────────────────────────────┘
                          │ HTTP (Axios)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND API LAYER                        │
│                   (FastAPI + Uvicorn)                       │
│  - /chat              - /evaluate-cv                        │
│  - /health            - Request validation                  │
└─────────────────────────┬─────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   RAG System │  │  CV Parser   │  │  Company DB  │
│ - LangChain  │  │ - PyPDF2     │  │ - CSV/Rules  │
│ - FAISS      │  │ - python-docx│  │ - Skill Data │
│ - Embeddings │  │ - Text Parse │  │ - Positions  │
└──────────────┘  └──────────────┘  └──────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│    Azure OpenAI Integration          │
│  - GPT-3.5-turbo (LLM)              │
│  - text-embedding-ada-002 (Embed)   │
│  - Fallback: SimpleFallbackLLM      │
└──────────────────────────────────────┘
```

---

## 📂 Source Code Structure & Purpose

### **1. Backend Core Files**

#### **app.py** (Main API Server)
**Purpose**: FastAPI application with REST endpoints

**Key Functions**:
```python
@app.post("/chat")
async def chat(request: ChatRequest)
    - Receives: user message + language
    - Uses: RAG system to find relevant HR FAQs
    - Returns: AI response + source documents
    - Multi-language: Detects language from keywords

@app.post("/evaluate-cv")
async def evaluate_cv(request: CVRequest)
    - Receives: CV text + position + language
    - Extracts: Skills, experience, education
    - Matches: Against job requirements (50+ keywords)
    - Scores: Excellent(80%), Good(60%), Fair(50%), Not Suitable(<50%)
    - Returns: Detailed evaluation report

@app.get("/health")
async def health_check()
    - Status monitoring
    - Returns: OK if system healthy
```

**Technical Details**:
- **Framework**: FastAPI (async Python web framework)
- **Validation**: Pydantic models for type safety
- **CORS**: Handles cross-origin requests from frontend
- **Logging**: Request/response logging for debugging
- **Error Handling**: Try-catch for fallback mechanisms

---

#### **chain_setup.py** (RAG System)
**Purpose**: Initialize and manage retrieval-augmented generation pipeline

**Key Components**:

```python
class SimpleFallbackLLM:
    - Fallback LLM when Azure OpenAI fails
    - Supports English + Vietnamese responses
    - Keyword-based response generation
    - Multi-language detection:
      * Detects: "tôi", "của tôi", "cái gì" → Vietnamese
      * Detects: "I", "me", "what" → English
    - Sample responses for: salary, leave, benefits, etc.

def initialize_rag_system():
    - Creates FAISS vector index from HR FAQ database
    - Loads embeddings using text-embedding-ada-002
    - Tries: Disk persistence → In-memory (fallback)
    - Handles: FAISS recreation errors gracefully
    - Returns: Ready-to-use RAG chain

class SimpleHashEmbeddings:
    - Fallback embedding when Azure fails
    - Uses: Python's hash() function
    - Creates: Fixed-size vectors from text
    - Deterministic: Same text = same embedding
    - Speed: Very fast (no API calls)
```

**Technical Flow**:
1. **Input**: User question + language
2. **Embedding**: Convert text → vector (768-dim)
3. **Search**: FAISS finds top-5 similar FAQs (similarity search)
4. **Context**: Combines found FAQs into prompt
5. **Generation**: Azure OpenAI generates response using context
6. **Fallback**: If Azure fails → SimpleFallbackLLM (rule-based)

**Key Dependencies**:
- `langchain`: RAG pipeline orchestration
- `faiss-cpu`: Vector similarity search
- `azure-openai`: LLM + embeddings

---

#### **cv_extractor.py** (CV Parser)
**Purpose**: Extract information from CV documents

**Key Functions**:
```python
def extract_text_from_pdf(pdf_path):
    - Uses: PyPDF2 library
    - Process: Extract all text from PDF pages
    - Returns: Complete CV text

def extract_text_from_docx(docx_path):
    - Uses: python-docx library
    - Process: Parse Word document structure
    - Returns: Formatted CV text

def parse_cv_text(cv_text):
    - Regex: Extract emails, phone numbers
    - Pattern: Find education section
    - Regex: Extract job titles and skills
    - Returns: Structured CV data (dict)
```

**Supported Formats**:
- PDF (`.pdf`) - PyPDF2
- Word (`.docx`) - python-docx
- Plain Text (`.txt`) - String parsing

---

#### **function_tools.py** (Utility Functions)
**Purpose**: Helper functions for data processing

**Key Functions**:
```python
def skill_matches(required_skills, cv_skills):
    - Matches: CV skills against job requirements
    - Logic: Checks direct match + synonyms + word-level match
    - Example:
      * Required: ["Machine Learning"]
      * CV contains: ["machine", "learning"]
      * Result: Match (word-level matching)
    - Keywords: 50+ synonyms including:
      * AI/ML: "neural", "deep learning", "rag", "llm"
      * Data: "sql", "python", "spark", "hadoop"
      * Web: "react", "node", "rest", "api"
    
def calculate_score(matched_skills, total_required):
    - Formula: (matched / total) * 100
    - Rating:
      * ≥80% → Excellent
      * 60-79% → Good
      * 50-59% → Fair
      * <50% → Not Suitable
    - Flexible: Allows up to 50% missing skills

def get_fallback_response(message, language):
    - Language detection: Analyzes keywords
    - Vietnamese: Returns responses in "vi" format
    - English: Returns responses in "en" format
    - Fallback: When no exact match found
```

---

#### **company_data.py** (Business Logic)
**Purpose**: Company information and job positions

**Data Includes**:
```python
JOB_POSITIONS = {
    "Data Scientist": {
        "required_skills": ["Python", "Machine Learning", "Statistics", ...],
        "nice_to_have": ["Deep Learning", "NLP", ...],
        "salary_range": "50-100k",
        "experience": "3+ years"
    },
    "Backend Developer": {...},
    "Frontend Developer": {...},
    ...
}

COMPANY_INFO = {
    "name": "Your Company",
    "mission": "...",
    "hr_policies": {...}
}
```

**Used By**:
- CV evaluation (skill matching)
- HR FAQ responses (policy questions)

---

### **2. Frontend Components (React/Next.js)**

#### **pages/index.jsx** (Main Page)
**Purpose**: Main application entry point

```jsx
export default function Home() {
    - State Management: useState for language, messages
    - Layout: Sidebar + ChatBox + CVUpload (grid layout)
    - Language Toggle: Switch EN/VI
    - Message History: Stores all messages
    - Error Handling: Try-catch for API calls
}
```

---

#### **components/ChatBox.jsx** (Chat Display)
**Purpose**: Display chat messages and responses

**Key Features**:
```jsx
Props:
  - messages: Array of chat messages
  - language: "en" or "vi"
  - loading: Boolean for loading state

Features:
  - Auto-scroll: New messages scroll into view
  - Markdown: Renders API responses with formatting
  - Timestamps: Shows when message was sent
  - Source Citations: Displays FAQ sources (if available)
  - Language-specific: Formats text based on language
```

---

#### **components/InputBar.jsx** (Message Input)
**Purpose**: Handle user input and message submission

```jsx
Features:
  - Text Input: Multi-line message input
  - Send Button: Submits message to backend API
  - Loading State: Disables input while processing
  - Error Display: Shows API errors to user
  - Keyboard: Enter to send (Shift+Enter for newline)
```

---

#### **components/CVUpload.jsx** (CV Upload & Evaluation)
**Purpose**: Upload CV and trigger evaluation

```jsx
Features:
  - File Input: Accepts PDF, DOCX, TXT
  - Position Selection: Dropdown from company_data
  - Language Selection: EN or VI
  - Upload Process:
    1. User selects file
    2. Chooses position
    3. Clicks "Evaluate"
    4. Frontend sends to /evaluate-cv
    5. Shows results: Match %, skills, rating
```

---

#### **components/Sidebar.jsx** (Navigation)
**Purpose**: Language toggle and settings

```jsx
Features:
  - Language Toggle: Switch EN/VI globally
  - Settings: Future enhancements
  - Navigation: Menu structure
```

---

### **3. Data Files**

#### **backend/data/hr_faq.csv**
**Purpose**: HR knowledge base for RAG system

**Format**:
```csv
question,answer
"What is leave policy?","You have 20 days annual leave..."
"How to apply for leave?","Submit request through HR system..."
"Remote work policy?","We allow 2 days/week remote..."
```

**Usage**:
- Loaded into FAISS vector index
- Used for semantic search in chat
- Provides context for LLM responses

---

## 🔧 Technology Deep Dive

### **Backend Technologies**

#### **1. FastAPI**
**What**: Modern Python web framework
**Why**: 
- Fast (ASGI)
- Type hints (automatic validation)
- Auto-generates API docs
- Great for AI/ML

**Usage in Project**:
```python
from fastapi import FastAPI
app = FastAPI()

@app.post("/chat")
async def chat(request: ChatRequest):
    # Request automatically validated against ChatRequest model
    # Response type-checked
    return {"response": "..."}
```

---

#### **2. LangChain**
**What**: Framework for building LLM applications
**Why**: 
- Abstracts LLM complexity
- Built-in RAG support
- Memory management
- Tool integration

**Usage in Project**:
```python
# RAG Pipeline
retriever = vectorstore.as_retriever()
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff"  # Combines docs + question
)

# Process
response = qa_chain.run(query)
```

---

#### **3. FAISS (Facebook AI Similarity Search)**
**What**: Vector similarity search library
**Why**:
- Fast nearest neighbor search
- Supports millions of vectors
- In-memory or disk storage
- Optimized for high dimensions

**Usage in Project**:
```python
from faiss import IndexFlatL2

# Create index
index = faiss.IndexFlatL2(dimension=768)
index.add(embeddings)  # Add 768-dim vectors

# Search
distances, indices = index.search(query_embedding, k=5)
# Returns: 5 most similar FAQs
```

---

#### **4. Azure OpenAI**
**What**: Cloud-hosted OpenAI models
**Why**:
- Managed service (no infrastructure)
- Enterprise security
- Multiple models available
- Pay-as-you-go

**Models Used**:
```
LLM: GPT-3.5-turbo (or GPT-5-mini fallback)
- Input: Chat prompts, FAQ context
- Output: Natural language responses
- Tokens: Limited per request (handled)

Embedding: text-embedding-ada-002
- Input: FAQ questions + user queries
- Output: 768-dimensional vectors
- Used for: Similarity search in FAISS
```

---

#### **5. PyPDF2**
**What**: PDF text extraction
**Why**: Parse CV PDFs

```python
from PyPDF2 import PdfReader

pdf = PdfReader("cv.pdf")
for page in pdf.pages:
    text += page.extract_text()
```

---

#### **6. python-docx**
**What**: Word document parsing
**Why**: Parse CV Word files

```python
from docx import Document

doc = Document("cv.docx")
for para in doc.paragraphs:
    text += para.text
```

---

### **Frontend Technologies**

#### **1. Next.js**
**What**: React framework with SSR/SSG
**Why**:
- File-based routing
- API routes
- Built-in optimization
- Vercel deployment

**Usage in Project**:
```javascript
// pages/index.jsx - Automatically routed to /
// pages/api/proxy.js - Backend proxy (optional)
```

---

#### **2. React Hooks**
**What**: Function-based component state management
**Why**: Simpler than class components

**Usage in Project**:
```javascript
const [messages, setMessages] = useState([]);
const [language, setLanguage] = useState("en");
const [loading, setLoading] = useState(false);

useEffect(() => {
    // Chat auto-scroll when messages change
    scrollToBottom();
}, [messages]);
```

---

#### **3. Tailwind CSS**
**What**: Utility-first CSS framework
**Why**: Fast styling without custom CSS

```jsx
<div className="flex gap-4 p-6 bg-gradient-to-r from-blue-500 to-purple-600">
  {/* Flexbox layout, 4px gap, padding, gradient */}
</div>
```

---

#### **4. Axios**
**What**: HTTP client library
**Why**: Simple API calls

```javascript
const response = await axios.post(
    `${API_URL}/chat`,
    { message: "Hello", language: "en" }
);
```

---

## 🔄 Data Flow Examples

### **Example 1: User Asks Question**

```
1. User Types: "What is our leave policy?" (in ChatBox)
   ↓
2. Frontend (InputBar.jsx)
   - Detects language: "policy" → English
   - Calls: POST /chat
   - Sends: { message: "What is...", language: "en" }
   ↓
3. Backend (app.py)
   - Receives ChatRequest
   - Calls: RAG system
   ↓
4. RAG System (chain_setup.py)
   - Converts: "What is..." → embedding (768-dim vector)
   - Searches: FAISS for similar FAQs
   - Finds: Top 5 matching FAQs from database
   - Combines: "Context: [FAQ1] [FAQ2] [FAQ3]
              Question: What is our leave policy?"
   ↓
5. Azure OpenAI (LLM)
   - Receives: Combined prompt
   - Generates: "You have 20 days annual leave..."
   - Returns: Response + source FAQs
   ↓
6. Frontend (ChatBox.jsx)
   - Receives response
   - Displays: AI response + citations
   - User reads: Full answer with sources
```

---

### **Example 2: User Uploads CV**

```
1. User (CVUpload.jsx)
   - Selects: resume.pdf
   - Chooses: "Data Scientist" position
   - Clicks: "Evaluate"
   ↓
2. Frontend
   - Reads: File via FileReader API
   - Sends: POST /evaluate-cv
   - Body: {
       cv_text: "...pdf content...",
       position: "Data Scientist",
       language: "en"
     }
   ↓
3. Backend (app.py)
   - Receives CVRequest
   - Calls: cv_extractor.py
   ↓
4. CV Parser
   - Extracts: Skills, experience, education
   - Returns: ["Python", "Machine Learning", "SQL", ...]
   ↓
5. Skill Matcher (function_tools.py)
   - Gets: Required skills for Data Scientist
   - Compares: CV skills vs Required
   - Matches: 
     * Direct: "Python" in both ✓
     * Synonym: "Deep Learning" matches "neural networks" ✓
     * Word-level: "machine learning" words match ✓
   - Calculates: 8/10 skills matched = 80% (Excellent)
   ↓
6. Backend Response
   - Returns: {
       match_percentage: 80,
       rating: "Excellent",
       matched_skills: [...],
       missing_skills: [...],
       recommendations: "..."
     }
   ↓
7. Frontend
   - Displays: Visual rating + breakdown
   - Shows: Matched/missing skills
   - Shows: Recommendations
```

---

## 🚀 Key Technical Features

### **1. Multi-Language Support**
**Implementation**:
- Language detection: Keyword matching
- Vietnamese keywords: "tôi", "của", "gì"
- English keywords: "I", "me", "what"
- Responses: Stored for each language
- Database: FAQ can have multiple language entries

---

### **2. Fallback Mechanisms (3-Level)**

```
Level 1: Azure OpenAI (Primary)
├─ GPT-3.5-turbo (LLM)
├─ text-embedding-ada-002 (embeddings)
└─ If fails → Level 2

Level 2: SimpleFallbackLLM
├─ Pre-loaded responses
├─ Keyword matching
├─ Language detection
└─ If fails → Level 3

Level 3: Rule-Based Response
├─ Generic message
├─ No personalization
└─ Always works
```

---

### **3. FAISS Vector Search**

```
How it works:
1. FAQ database (1000 questions)
   ↓
2. Each question → embedding (768 dimensions)
   ↓
3. Store in FAISS index (optimized for search)
   ↓
4. User query → embedding
   ↓
5. Find nearest neighbors (cosine similarity)
   ↓
6. Return top-5 most relevant FAQs
   
Performance: < 100ms for 1000+ FAQs
```

---

### **4. Skill Matching Algorithm**

```
For each CV skill:
1. Check direct match
   → required_skills.contains(cv_skill)
   
2. Check synonyms (50+ keyword pairs)
   → "machine learning" == "ml"
   → "artificial intelligence" == "ai"
   
3. Check word-level match
   → split by spaces/punctuation
   → match individual words
   
4. Score: matched_count / required_count
   → ≥80% = Excellent
   → 60-79% = Good
   → 50-59% = Fair
   → <50% = Not Suitable
```

---

## 📦 Dependencies Summary

### **Backend (requirements.txt)**
```
fastapi==0.104.1              # Web framework
uvicorn==0.24.0               # ASGI server
langchain==0.0.352            # RAG framework
azure-openai==0.10.0          # Azure OpenAI API
faiss-cpu==1.7.4              # Vector search
pydantic==2.4.2               # Data validation
python-dotenv==1.0.0          # Environment config
pypdf2==3.0.1                 # PDF parsing
python-docx==0.8.11           # Word parsing
```

### **Frontend (package.json)**
```
next: 14.2.33                 # React framework
react: 18.2.0                 # UI library
tailwindcss: 3.4.0            # CSS framework
axios: 1.6.0                  # HTTP client
lucide-react: 0.294.0         # Icons
```

---

## 🔐 Security Considerations

### **1. API Keys**
- **Storage**: `.env` file (never commit)
- **Loading**: `python-dotenv`
- **Environment Variables**: Set in Vercel/Render dashboard

### **2. CORS (Cross-Origin)**
```python
# Backend allows requests from:
allow_origins=[
    "http://localhost:3000",     # Local dev
    "https://*.vercel.app"       # Vercel deploy
]
```

### **3. Input Validation**
```python
# Pydantic models validate input
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    language: str = Field(..., regex="^(en|vi)$")
    
# Automatically rejects invalid input
```

---

## 📊 Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Chat response | 1-3s | Azure + FAISS search |
| CV evaluation | 2-5s | PDF parsing + skill matching |
| FAISS search | <100ms | 1000 FAQs |
| Embedding | 200-500ms | Azure OpenAI API |
| Fallback response | <50ms | In-memory rules |

---

## 🔄 Deployment Architecture

```
┌─────────────────────────────────────────────┐
│         Vercel (Frontend)                   │
│  - Next.js app auto-deploys on git push    │
│  - CDN: Edge caching worldwide              │
│  - Domain: your-project.vercel.app         │
└──────────────┬──────────────────────────────┘
               │ HTTPS
               ▼
┌─────────────────────────────────────────────┐
│    Render.com (Backend)                     │
│  - FastAPI app runs in container            │
│  - Python 3.11 environment                  │
│  - Auto-restart on crash                    │
│  - Domain: your-api.onrender.com           │
└──────────────┬──────────────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Azure OpenAI API    │
    │  - GPT-3.5-turbo    │
    │  - Embeddings       │
    └──────────────────────┘
```

---

## 🎓 Learning Resources

### **Key Concepts**:
1. **RAG**: How to augment LLMs with retrieval
2. **Vector Databases**: Similarity search mechanics
3. **FastAPI**: Building production APIs
4. **React Hooks**: State management patterns
5. **Deployment**: Cloud infrastructure

### **Further Reading**:
- LangChain Docs: https://python.langchain.com
- Azure OpenAI: https://learn.microsoft.com/en-us/azure/ai-services/openai/
- FAISS: https://github.com/facebookresearch/faiss
- Next.js: https://nextjs.org/docs

---

## 📝 Conclusion

This HR Assistant System demonstrates:
- ✅ Modern full-stack development (Next.js + FastAPI)
- ✅ AI/ML integration (Azure OpenAI + FAISS)
- ✅ RAG implementation (question answering)
- ✅ Multi-language support (EN/VI)
- ✅ Robust error handling (3-level fallbacks)
- ✅ Production-ready architecture (Vercel + Render)

All components work together seamlessly to provide an intelligent HR assistant that can answer questions and evaluate CVs!
