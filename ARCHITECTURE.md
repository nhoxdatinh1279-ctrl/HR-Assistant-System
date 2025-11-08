# 📊 HR Assistant Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React/Next.js)                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    http://localhost:3000                 │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                  ChatBox Component                       │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │  User Message: "Check my leave balance?"         │   │   │
│  │  │  > Sends to API                                  │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │  Bot Response: "Alice has 5 days left"           │   │   │
│  │  │  > Shows sources & function calls                │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │         InputBar (textarea) + Sidebar (tips)            │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↕ Axios
                     POST /api/chat request
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI/Python)                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         http://localhost:8000 (FastAPI Server)          │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  Endpoints:                                              │   │
│  │  • GET  /api/health         → Status check             │   │
│  │  • POST /api/init           → Init RAG system          │   │
│  │  • POST /api/chat           → Process user message     │   │
│  │  • GET  /api/faq            → FAQ statistics           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │        LangChain RAG Pipeline (chain_setup.py)          │   │
│  │                                                          │   │
│  │  Input: User Message                                    │   │
│  │    ↓                                                     │   │
│  │  1. Vector Search (FAISS)                              │   │
│  │     └─ Retrieve top 3 HR FAQs                          │   │
│  │    ↓                                                     │   │
│  │  2. Azure OpenAI LLM Processing                         │   │
│  │     ├─ Check if function call needed                   │   │
│  │     ├─ Execute tools if needed                         │   │
│  │     └─ Generate response with context                 │   │
│  │    ↓                                                     │   │
│  │  Output: Answer + Sources + Function Calls             │   │
│  └──────────────────────────────────────────────────────────┘   │
│            ↓                          ↓                           │
│  ┌─────────────────────┐   ┌──────────────────────────┐          │
│  │   FAISS Vectordb    │   │  Azure OpenAI Service    │          │
│  ├─────────────────────┤   ├──────────────────────────┤          │
│  │ 15 HR FAQs (indexed)│   │  Models:                 │          │
│  │ - Leave policies    │   │  • text-embedding-3-sm   │          │
│  │ - Work policies     │   │  • GPT-4o-mini           │          │
│  │ - Benefits          │   │  • Function Calling      │          │
│  │ - Pay & Comp        │   └──────────────────────────┘          │
│  └─────────────────────┘                                          │
│            ↑                                                      │
│  ┌─────────────────────────────────────────┐                    │
│  │   Function Tools (function_tools.py)    │                    │
│  ├─────────────────────────────────────────┤                    │
│  │ • check_leave_balance(employee_name)    │                    │
│  │ • check_pay_date()                      │                    │
│  │ • get_employee_department(name)         │                    │
│  │ • check_company_info()                  │                    │
│  │                                         │                    │
│  │ Mock Database:                          │                    │
│  │ • Alice: 5 days, Engineering            │                    │
│  │ • Bob: 10 days, Sales                   │                    │
│  │ • Charlie: 3 days, HR                   │                    │
│  │ • Diana: 8 days, Marketing              │                    │
│  └─────────────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow - Example Conversation

### Scenario: "How many leave days do I have?"

```
┌─ User Types in Chat Box ──────────────────────────────────────┐
│ Message: "How many leave days do I have left?"               │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
                    ┌──────────────────┐
                    │  Axios POST to   │
                    │  /api/chat       │
                    └────────┬─────────┘
                            ↓
        ┌─────────────────────────────────────────┐
        │  FastAPI Receives Request               │
        │  - Message: "How many leave days...?"   │
        │  - Session: default                     │
        └────────────┬────────────────────────────┘
                     ↓
        ┌─────────────────────────────────────────┐
        │  LangChain Chain Processes Query         │
        │                                         │
        │  Step 1: FAISS Vector Search            │
        │  ├─ Embed question: "leave days"        │
        │  ├─ Search vector store                 │
        │  └─ Retrieve FAQ: "How to apply for.."  │
        │                                         │
        │  Step 2: Azure OpenAI Detects Function  │
        │  ├─ Recognizes: need check_leave_bal   │
        │  ├─ Calls: function_tools.py            │
        │  └─ Result: "Alice has 5 days"          │
        │                                         │
        │  Step 3: Generate Response              │
        │  ├─ Combine: FAQ context + function    │
        │  ├─ Write: Final answer                 │
        │  └─ Include: Source documents           │
        └────────────┬────────────────────────────┘
                     ↓
        ┌─────────────────────────────────────────┐
        │  Return Response to Frontend            │
        │  {                                      │
        │    "answer": "Alice has 5 days of..",   │
        │    "source_documents": [{...}],         │
        │    "function_calls": ["check_leave_.."]│
        │  }                                      │
        └────────────┬────────────────────────────┘
                     ↓
        ┌─────────────────────────────────────────┐
        │  Frontend Receives Response             │
        │  ├─ Update messages state               │
        │  ├─ Display bot message                 │
        │  ├─ Show source documents               │
        │  └─ Scroll to latest message            │
        └────────────┬────────────────────────────┘
                     ↓
        ┌─────────────────────────────────────────┐
        │  User Sees Response in ChatBox           │
        │  "Alice has 5 days of annual leave      │
        │   remaining."                           │
        │                                         │
        │  [Show Sources]                         │
        │  FAQ: "How do I apply for annual leave?"│
        └─────────────────────────────────────────┘
```

---

## Component Hierarchy

```
App (pages/index.jsx)
│
├─ Header
│  └─ "Internal HR Assistant"
│
├─ ChatBox (components/ChatBox.jsx)
│  ├─ Empty State (initial)
│  ├─ Message List
│  │  ├─ User Messages
│  │  │  ├─ Avatar (blue, user icon)
│  │  │  └─ Content (right-aligned)
│  │  │
│  │  └─ Bot Messages
│  │     ├─ Avatar (green, bot icon)
│  │     ├─ Content (left-aligned)
│  │     └─ Sources (FAQ snippets)
│  │
│  └─ Loading State (animated dots)
│
├─ InputBar (components/InputBar.jsx)
│  ├─ Textarea
│  ├─ Send Button
│  └─ Help Text
│
└─ Sidebar (components/Sidebar.jsx)
   ├─ System Status
   │  ├─ API Connected
   │  └─ Vector DB Ready
   ├─ Quick Actions
   │  ├─ Common Questions
   │  └─ Company Policies
   ├─ Tips
   │  ├─ Ask about leave
   │  ├─ Query pay dates
   │  ├─ Ask policies
   │  └─ Get HR contact
   └─ Clear Chat Button
```

---

## File Dependencies

```
Frontend:
  index.jsx (pages)
    ├─ ChatBox.jsx (components)
    ├─ InputBar.jsx (components)
    ├─ Sidebar.jsx (components)
    ├─ axios (HTTP client)
    └─ globals.css (styling)

Backend:
  app.py (FastAPI server)
    ├─ chain_setup.py (RAG setup)
    │  ├─ function_tools.py (tools)
    │  ├─ data/hr_faq.csv (FAQ data)
    │  └─ embeddings/faiss_index/ (vector store)
    └─ .env (configuration)

Configuration:
  frontend/.env.local → NEXT_PUBLIC_API_URL
  backend/.env → Azure OpenAI credentials
```

---

## State Management (Frontend)

```
Home Component State:

messages: [
  {
    role: 'user',
    content: 'How many leave days?'
  },
  {
    role: 'bot',
    content: 'Alice has 5 days...',
    sources: [
      {
        content: 'Leave policy excerpt...',
        question: 'How do I apply..?',
        source: 'HR FAQ'
      }
    ]
  }
]

isLoading: boolean (true while awaiting response)
error: string | null (error message if any)
```

---

## Request/Response Flow

```
Frontend Request:
POST /api/chat
{
  "message": "How many leave days do I have left?",
  "session_id": "default"
}

Backend Processing:
1. Receive message
2. Generate embedding
3. Search FAISS (top 3 results)
4. Call LLM with context
5. LLM detects function call need
6. Execute check_leave_balance()
7. Generate final response
8. Format with sources

Frontend Response:
{
  "answer": "Alice has 5 days of annual leave remaining.",
  "source_documents": [
    {
      "content": "You can apply for annual leave via HR portal...",
      "source": "HR FAQ",
      "question": "How do I apply for annual leave?"
    }
  ],
  "function_calls": ["check_leave_balance"]
}

Frontend Display:
1. Parse response
2. Add bot message to chat
3. Display sources dropdown
4. Show loading state ends
5. Auto-scroll to new message
```

---

## Technology Integration Points

```
Azure OpenAI
     ↑
     │ API calls
     ↓
LangChain
  ├─ Uses embeddings from Azure
  ├─ Uses LLM from Azure
  ├─ Manages conversation
  └─ Orchestrates RAG
     ↑
     │
  FAISS
  └─ Vector search for FAQ retrieval
     ↑
     │
Function Tools
  ├─ check_leave_balance
  ├─ check_pay_date
  ├─ get_employee_department
  └─ check_company_info
     ↑
     │
  FastAPI
  ├─ REST endpoints
  ├─ Request/response handling
  └─ CORS support
     ↑
     │
  Next.js/React
  ├─ User interface
  ├─ State management
  └─ Axios client
     ↑
     │
  TailwindCSS
  └─ Styling & responsive design
```

---

## Deployment Architecture (Optional)

```
Production Setup:

Internet
    ↓
┌──────────────────┐
│ Vercel/Netlify   │  Frontend
│ (Next.js)        │
└────────┬─────────┘
         │
         │ HTTPS
         ↓
┌──────────────────────────┐
│ Azure Container Registry │
│ (Docker image)           │
└────────┬─────────────────┘
         │
         ↓
┌──────────────────────────────┐
│ Azure App Service / AKS      │  Backend
│ (FastAPI + Gunicorn)         │
└────────┬─────────────────────┘
         │
         ├─→ Azure OpenAI (API)
         ├─→ Azure Blob Storage (FAISS index)
         └─→ Azure Application Insights (Logging)
```

---

**Architecture is production-ready and scalable! 🚀**
