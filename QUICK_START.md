# 🚀 Quick Start Setup Guide

## 5-Minute Setup for HR Assistant Chatbot

### Step 1: Prepare Environment Variables (1 min)

#### Backend Setup
```bash
cd backend
cp .env.example .env
```
Edit `backend/.env` and add your Azure OpenAI credentials:
```env
AZURE_OPENAI_EMBEDDING_API_KEY=your-key-here
AZURE_OPENAI_EMBEDDING_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_LLM_API_KEY=your-key-here
AZURE_OPENAI_LLM_ENDPOINT=https://your-resource.openai.azure.com/
```

#### Frontend Setup (Optional)
```bash
cd frontend
cp .env.example .env.local
# Keep default: NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

### Step 2: Start Backend (2 min)

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app:app --reload
```

**Output should show:**
```
Uvicorn running on http://127.0.0.1:8000
```

Visit http://localhost:8000/docs to see interactive API documentation

---

### Step 3: Start Frontend (2 min)

In a **new terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

**Output should show:**
```
▲ Next.js 14.x.x
- Local: http://localhost:3000
```

---

### Step 4: Open Application (0 min)

Visit: **http://localhost:3000**

You should see:
- Blue header with "Internal HR Assistant"
- Empty chat area
- Input box at bottom
- Sidebar on right with tips

---

## 🎯 Test the Chatbot

Try these queries:

### Test 1: Function Call (Leave Balance)
```
User: Hi, how many leave days do I have left?
Expected: Bot checks leave balance and responds
```

### Test 2: RAG (Company Policy)
```
User: What's the company's remote work policy?
Expected: Bot retrieves HR FAQ and explains policy
```

### Test 3: Pay Information
```
User: When will I get paid?
Expected: Bot provides pay date information
```

---

## 🐛 Troubleshooting

### Backend won't start
**Error:** "ModuleNotFoundError: No module named 'langchain'"
**Solution:** Run `pip install -r requirements.txt` in backend folder

### API key error
**Error:** "AuthenticationError: 401"
**Solution:** Check .env file has correct Azure OpenAI credentials

### Frontend can't connect to API
**Error:** "Network error" or "Failed to connect"
**Solution:** Verify backend is running on http://localhost:8000

### Port already in use
**Error:** "Port 8000/3000 is already in use"
**Solution:** 
- Backend: `uvicorn app:app --port 8001 --reload`
- Frontend: `npm run dev -- -p 3001`

---

## 📊 Project Structure

```
WORKSHOP 4/
├── backend/
│   ├── app.py                    ← FastAPI server
│   ├── chain_setup.py            ← LangChain RAG
│   ├── function_tools.py         ← Azure tools
│   ├── data/hr_faq.csv           ← 15 HR Q&As
│   ├── requirements.txt          ← Python dependencies
│   └── .env.example              ← Config template
│
├── frontend/
│   ├── pages/index.jsx           ← Main chat page
│   ├── components/               ← React components
│   ├── package.json              ← Node dependencies
│   └── .env.example              ← Config template
│
├── README.md                     ← Full documentation
└── PROJECT_STATUS.md             ← Detailed status
```

---

## 🎨 UI Features

- ✅ Real-time chat interface
- ✅ Auto-scrolling messages
- ✅ Loading animations
- ✅ Source document display
- ✅ Clear chat button
- ✅ System status indicators
- ✅ Mobile responsive design

---

## 🧠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + LangChain + FAISS |
| LLM | Azure OpenAI (GPT-4o-mini) |
| Embeddings | Azure OpenAI (text-embedding-3-small) |
| Frontend | Next.js + React + TailwindCSS |

---

## 📚 Next Steps

1. **Customize HR FAQs**
   - Edit `backend/data/hr_faq.csv`
   - Run `/api/init` to rebuild vector store

2. **Add New Tools**
   - Add functions to `backend/function_tools.py`
   - Update `AVAILABLE_TOOLS` list

3. **Customize UI**
   - Edit `frontend/tailwind.config.js` for colors
   - Modify components in `frontend/components/`

4. **Deploy to Production**
   - Use Gunicorn + Nginx for backend
   - Use Vercel for Next.js frontend
   - Set up proper environment variables

---

## ✨ Tips

- Backend API docs: http://localhost:8000/docs
- Press **Shift+Enter** in chat for new line
- Press **Enter** to send message
- Click "Clear Chat History" to start fresh
- Check sidebar for quick tips and status

---

**Happy chatting! 🎉**

For full documentation, see README.md
For detailed status, see PROJECT_STATUS.md
