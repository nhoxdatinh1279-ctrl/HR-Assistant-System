# Internal HR Assistant - Full Stack RAG Chatbot

A production-ready HR Assistant chatbot web application built with **LangChain + FAISS + Azure OpenAI** on the backend and **React/Next.js** on the frontend. Employees can ask HR questions, retrieve answers from company policies via RAG, and invoke function calls (check leave balance, pay dates, etc.).

## 🎯 Key Features

✅ **Retrieval-Augmented Generation (RAG)**
- Vector embeddings via Azure OpenAI text-embedding-3-small
- FAISS vector database for semantic search
- Retrieves top 3 relevant HR policies for each query

✅ **Function Calling**
- Check employee leave balance
- Get company pay date
- Retrieve department information
- Access general company info

✅ **Modern Web UI**
- Real-time chat with streaming responses
- Display retrieved context documents
- Chat history and clear function
- Responsive design with TailwindCSS
- Loading animations and error handling

✅ **Enterprise-Ready Backend**
- FastAPI REST API with CORS support
- Comprehensive error handling
- Environment variable management
- Modular code structure
- 15 sample HR Q&A pairs included

## 🏗️ Project Structure

```
hr_assistant/
├── backend/
│   ├── app.py                    # FastAPI server with REST endpoints
│   ├── chain_setup.py            # LangChain RAG chain initialization
│   ├── function_tools.py         # Azure function calling tools
│   ├── data/
│   │   └── hr_faq.csv           # 15 HR Q&A pairs
│   ├── embeddings/
│   │   └── faiss_index/         # Local FAISS vector store
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example             # Environment template
│   └── __pycache__/
│
├── frontend/
│   ├── pages/
│   │   ├── index.jsx            # Main chat page
│   │   └── _app.jsx             # Next.js app wrapper
│   ├── components/
│   │   ├── ChatBox.jsx          # Chat message display
│   │   ├── InputBar.jsx         # Message input
│   │   └── Sidebar.jsx          # Context & actions sidebar
│   ├── styles/
│   │   └── globals.css          # TailwindCSS styling
│   ├── package.json             # Node dependencies
│   ├── next.config.js           # Next.js configuration
│   ├── tailwind.config.js       # TailwindCSS configuration
│   ├── postcss.config.js        # PostCSS configuration
│   ├── .env.example             # Environment template
│   └── node_modules/
│
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Azure OpenAI API credentials (API key and endpoint)

### 1. Backend Setup

```bash
cd backend

# Create .env file with your Azure credentials
cp .env.example .env
# Edit .env with your actual credentials:
# - AZURE_OPENAI_EMBEDDING_API_KEY
# - AZURE_OPENAI_EMBEDDING_ENDPOINT
# - AZURE_OPENAI_LLM_API_KEY
# - AZURE_OPENAI_LLM_ENDPOINT

# Install dependencies
pip install -r requirements.txt

# Start the server (API will run on http://localhost:8000)
uvicorn app:app --reload
```

### 2. Frontend Setup

In a new terminal:

```bash
cd frontend

# Create .env.local file
cp .env.example .env.local
# Default is http://localhost:8000 (no changes needed if backend runs locally)

# Install dependencies
npm install

# Start dev server (Frontend will run on http://localhost:3000)
npm run dev
```

### 3. Access the Application

Open your browser and go to:
```
http://localhost:3000
```

## 🤖 Demo Interactions

### Example 1: Check Leave Balance (Function Call)
```
User: How many leave days do I have left?
Bot: [Calls check_leave_balance function]
     Alice has 5 days of annual leave remaining.
```

### Example 2: Company Policy (RAG Retrieval)
```
User: What's the company's remote work policy?
Bot: [Retrieves from FAQ database]
     Employees can work remotely up to 2 days per week...
     
Sources:
✓ Remote Work Policy Document
```

### Example 3: Pay Information (Function Call)
```
User: When will I receive my salary?
Bot: [Calls check_pay_date function]
     Salaries are paid on the 25th of every month. 
     Your next salary will be deposited in 10 days.
```

## 🧠 Technical Architecture

### Backend Flow

```
User Message
    ↓
FastAPI /api/chat endpoint
    ↓
LangChain ConversationalRetrievalChain
    ↓
    ├─→ FAISS Vector Search (retrieve HR policies)
    │   └─→ Top 3 matching FAQs with context
    │
    └─→ Azure OpenAI LLM with Function Calling
        ├─→ Check if function call is needed
        ├─→ If yes: Execute tool (check_leave_balance, etc.)
        └─→ Generate response with context
    ↓
Response (answer + sources + function_calls)
    ↓
Frontend Display
```

### Vector Database (FAISS)
- Stores embeddings of 15 HR FAQ documents
- Uses TF-IDF for semantic similarity
- Loaded into memory for fast retrieval
- Searchable by employee queries

### Function Calling Tools
- `check_leave_balance(employee_name)` - Returns leave days remaining
- `check_pay_date()` - Returns salary payment date
- `get_employee_department(employee_name)` - Returns employee department
- `check_company_info()` - Returns general company details

### Frontend Architecture
- **Pages**: Single-page application with Next.js
- **Components**: ChatBox, InputBar, Sidebar (React)
- **Styling**: TailwindCSS for modern responsive design
- **API Client**: Axios for backend communication
- **State Management**: React hooks (useState, useCallback)

## 📊 API Endpoints

### `/api/health` (GET)
Health check endpoint
```json
{
  "status": "healthy",
  "service": "Internal HR Assistant API",
  "rag_ready": true
}
```

### `/api/init` (POST)
Initialize/reinitialize RAG system
```json
{
  "status": "success",
  "message": "RAG system initialized successfully."
}
```

### `/api/chat` (POST)
Main chat endpoint
```json
Request:
{
  "message": "How many leave days do I have left?"
}

Response:
{
  "answer": "Alice has 5 days of annual leave remaining.",
  "source_documents": [
    {
      "content": "You can apply for annual leave...",
      "source": "HR FAQ",
      "question": "How do I apply for annual leave?"
    }
  ],
  "function_calls": ["check_leave_balance"]
}
```

### `/api/faq` (GET)
Get FAQ statistics
```json
{
  "total_faqs": 15,
  "vector_store_ready": true
}
```

## 🔧 Configuration

### Backend Environment Variables
```env
# Azure OpenAI Embedding
AZURE_OPENAI_EMBEDDING_API_KEY=your-key
AZURE_OPENAI_EMBEDDING_ENDPOINT=https://your-endpoint.openai.azure.com/

# Azure OpenAI LLM
AZURE_OPENAI_LLM_API_KEY=your-key
AZURE_OPENAI_LLM_ENDPOINT=https://your-endpoint.openai.azure.com/

# Server
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

### Frontend Environment Variables
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📦 Dependencies

### Backend
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **langchain** - LLM orchestration
- **langchain-openai** - Azure OpenAI integration
- **faiss-cpu** - Vector database
- **openai** - Azure OpenAI client
- **python-dotenv** - Environment management

### Frontend
- **next.js** - React framework
- **react** - UI library
- **tailwindcss** - CSS framework
- **axios** - HTTP client
- **lucide-react** - Icon library

## 🎨 UI/UX Design

### Color Scheme
- **Primary**: Blue (#3b82f6) - User messages, buttons
- **Secondary**: Dark Blue (#1e40af) - Accents
- **Success**: Green (#10b981) - Status indicators
- **Background**: Light Gray (#f3f4f6)

### Components
- **Chat Bubbles**: Rounded, colored by role (user/bot)
- **Input Area**: Multi-line textarea with send button
- **Sidebar**: System status, quick actions, tips
- **Loading State**: Animated dots
- **Error Handling**: User-friendly error messages

## 📝 Sample HR FAQ Data

The system includes 15 realistic Q&A pairs:
1. Annual leave application process
2. Remote work policy
3. Payroll bank account updates
4. Working hours & flexibility
5. Sick leave reporting
6. Health insurance coverage
7. Company holidays
8. Pay stub access
9. Professional development budget
10. Department transfer process
11. Overtime policy & compensation
12. Retirement plan enrollment
13. Maternity/paternity leave
14. Workplace complaint process
15. Remote employee benefits

## 🚀 Deployment

### Development
```bash
# Backend
cd backend && uvicorn app:app --reload

# Frontend (in new terminal)
cd frontend && npm run dev
```

### Production
```bash
# Backend
cd backend && uvicorn app:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend && npm run build && npm start
```

## 🐛 Troubleshooting

### Backend Issues
- **Import errors**: Ensure all packages are installed: `pip install -r requirements.txt`
- **API key error**: Verify environment variables in `.env` file
- **FAISS index not found**: Run `/api/init` endpoint first
- **Port 8000 in use**: Change port in app.py or kill existing process

### Frontend Issues
- **Cannot connect to API**: Ensure backend is running and `.env.local` has correct API_URL
- **Module not found**: Run `npm install` again
- **Port 3000 in use**: Run on different port: `npm run dev -- -p 3001`

## 📚 Resources

- [LangChain Documentation](https://python.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Next.js Documentation](https://nextjs.org/docs)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)

## 📄 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add more HR FAQ entries
- Improve the RAG pipeline
- Enhance the UI design
- Add new function calling tools
- Optimize performance

## ❓ FAQ

**Q: Can I add custom HR policies?**
A: Yes! Add more rows to `backend/data/hr_faq.csv` and run `/api/init` to rebuild the vector store.

**Q: How do I add new function calling tools?**
A: Add functions to `backend/function_tools.py` with `@tool()` decorator and add them to `AVAILABLE_TOOLS` list.

**Q: Does it support multiple languages?**
A: The current version supports English. You can extend it with translations in frontend/components.

**Q: How is conversation history stored?**
A: Currently stored in memory. For persistence, replace `ConversationBufferMemory` with database-backed memory.

**Q: Can I customize the UI theme?**
A: Yes! Edit `frontend/tailwind.config.js` and `frontend/styles/globals.css` to change colors and styling.

---

**Built with ❤️ for modern HR automation**
