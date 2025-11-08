"""
FastAPI backend for the HR Assistant Chatbot.
Provides REST API endpoints for chat and initialization.
"""

import os
import json
import base64
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

# Import RAG components
from chain_setup import initialize_rag_system, create_or_load_faiss_index, setup_rag_chain

# Import CV extractor
from cv_extractor import extract_cv_content, parse_cv_for_skills

# Initialize FastAPI app
app = FastAPI(
    title="Internal HR Assistant API",
    description="RAG-based HR Assistant with function calling",
    version="1.0.0"
)

# Add CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for RAG system
rag_system = None
vector_store = None
llm = None
retriever = None


# Pydantic models for request/response
class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    session_id: str = "default"
    language: str = "en"  # 'en' for English, 'vi' for Vietnamese


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    answer: str
    source_documents: list[dict] = []
    function_calls: list[str] = []


class InitResponse(BaseModel):
    """Response model for init endpoint"""
    status: str
    message: str


@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on app startup"""
    global vector_store, llm, retriever
    
    try:
        print("[STARTUP] Starting up HR Assistant API...")
        print("[STARTUP] Initializing RAG system...")
        vector_store, (llm, retriever) = initialize_rag_system()
        print("[OK] RAG system initialized successfully!")
    except Exception as e:
        print(f"[WARNING] Could not initialize RAG system: {e}")
        print("[WARNING] The API will start but RAG functionality may be limited")
        print("[WARNING] Please ensure Azure OpenAI credentials are properly configured")
        # Don't re-raise the exception - let the app start anyway
        vector_store = None
        llm = None
        retriever = None


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Internal HR Assistant API",
        "rag_ready": vector_store is not None and llm is not None and retriever is not None
    }


@app.post("/api/init")
async def init_system() -> InitResponse:
    """
    Initialize or reinitialize the RAG system.
    Recreates FAISS index and retrieval chain.
    """
    global vector_store, llm, retriever
    
    try:
        print("Reinitializing RAG system...")
        vector_store, (llm, retriever) = initialize_rag_system()
        
        return InitResponse(
            status="success",
            message="RAG system initialized successfully. Ready to answer HR questions!"
        )
    except Exception as e:
        error_msg = f"Error initializing RAG system: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)


# FAQ translations dictionary
FAQ_TRANSLATIONS = {
    "How do I apply for annual leave?": "Làm cách nào để tôi xin nghỉ phép hằng năm?",
    "What is the company's remote work policy?": "Chính sách làm việc từ xa của công ty là gì?",
    "How can I update my payroll bank account?": "Làm cách nào để cập nhật tài khoản ngân hàng lương?",
    "What are the working hours?": "Giờ làm việc là gì?",
    "How do I request a sick leave?": "Làm cách nào để xin nghỉ ốm?",
    "What is the company's health insurance coverage?": "Phạm vi bảo hiểm y tế của công ty là gì?",
    "When is the next company holiday?": "Kỳ nghỉ công ty tiếp theo là khi nào?",
    "How do I access my pay stubs?": "Làm cách nào để truy cập bảng lương của tôi?",
    "What is the professional development budget?": "Ngân sách phát triển chuyên nghiệp là gì?",
    "How do I request a transfer to another department?": "Làm cách nào để yêu cầu chuyển đến một phòng ban khác?",
    "What is the overtime policy?": "Chính sách tăng ca là gì?",
    "How do I enroll in the company retirement plan?": "Làm cách nào để tôi đăng ký kế hoạch hưu trí của công ty?",
    "What is the maternity and paternity leave policy?": "Chính sách nghỉ thai sản và nghỉ sinh con là gì?",
    "How do I report a workplace concern or complaint?": "Làm cách nào để báo cáo mối lo ngại hoặc khiếu nại tại nơi làm việc?",
    "What benefits are available to remote employees?": "Các lợi ích nào có sẵn cho nhân viên làm việc từ xa?",
}


def translate_faq_question(question: str, language: str = "en") -> str:
    """Translate FAQ question to target language"""
    if language == "vi":
        return FAQ_TRANSLATIONS.get(question, question)
    return question


def get_fallback_response(message: str, language: str = "en") -> str:
    """
    Generate fallback response based on keywords and language
    """
    question_lower = message.lower()
    
    # Define responses in both languages
    responses = {
        "en": {
            "leave": "You can apply for annual leave via the company HR portal. Submit your request at least 2 weeks in advance. Your manager must approve before submission to payroll. For sick leave, report to your manager as soon as possible.",
            "benefits": "All employees are covered under the company health insurance plan. Coverage includes medical, dental, and vision. Dependents can be added during open enrollment. Remote employees receive the same benefits as office employees.",
            "salary": "Pay stubs are available in the HRIS portal under Payroll > Pay Stubs. You can download PDF copies for your records. To update your payroll bank account, submit your request via HRIS > Payroll section.",
            "remote": "Employees may work remotely up to 2 days per week. Remote days must be approved by your manager and cannot be consecutive without special approval. Remote employees receive the same benefits as office employees.",
            "retirement": "Retirement plan enrollment happens during onboarding. The company matches 50% of employee contributions up to 6% of salary. Contact HR for more details.",
            "maternity": "Eligible employees receive 12 weeks of paid maternity leave and 4 weeks of paid paternity leave. Contact HR for specific eligibility requirements.",
            "holiday": "Company holidays include New Year, Independence Day, Thanksgiving, and Christmas. See the HR portal for the complete holiday calendar.",
            "training": "Each employee receives $2,000 annually for training and professional development. Submit requests via the Learning Portal for approval.",
            "transfer": "Contact HR to discuss transfer opportunities. You must complete at least 1 year in your current role before requesting a transfer.",
            "overtime": "Overtime is compensated at 1.5x your regular rate. All overtime must be pre-approved by your manager and documented in the HR system.",
            "complaint": "Use the anonymous HR Hotline or submit a formal complaint via the HR portal. All complaints are handled confidentially and investigated promptly.",
            "hours": "Standard working hours are 9 AM to 5 PM, Monday to Friday. Flexible arrangements are available upon manager approval.",
            "default": "Hello! I'm the HR Assistant here to help answer your questions about company policies, benefits, leave, payroll, and more. I have access to our HR FAQ database with information about annual leave, remote work policy, health insurance, retirement plans, professional development, and many other HR topics. What would you like to know?"
        },
        "vi": {
            "leave": "Bạn có thể nộp đơn xin nghỉ phép thường niên thông qua cổng HR của công ty. Gửi yêu cầu của bạn ít nhất 2 tuần trước. Quản lý của bạn phải phê duyệt trước khi gửi đến bộ phận lương. Đối với nghỉ ốm, hãy báo cáo với quản lý càng sớm càng tốt.",
            "benefits": "Tất cả nhân viên đều được bảo hiểm y tế của công ty. Bảo hiểm bao gồm y tế, nha khoa và mắt. Người phụ thuộc có thể được thêm vào trong thời gian đăng ký mở. Nhân viên làm việc từ xa nhận cùng phúc lợi như nhân viên tại văn phòng.",
            "salary": "Bảng lương có sẵn trong cổng HRIS tại Payroll > Pay Stubs. Bạn có thể tải xuống bản PDF để lưu trữ. Để cập nhật tài khoản ngân hàng lương, gửi yêu cầu qua phần HRIS > Payroll.",
            "remote": "Nhân viên có thể làm việc từ xa tối đa 2 ngày mỗi tuần. Các ngày làm việc từ xa phải được quản lý phê duyệt và không được liên tiếp trừ khi có phê duyệt đặc biệt. Nhân viên làm việc từ xa nhận cùng phúc lợi như nhân viên tại văn phòng.",
            "retirement": "Đăng ký kế hoạch hưu trí diễn ra trong quá trình nhập môn. Công ty đóng góp 50% số tiền nhân viên đóng góp lên đến 6% lương. Liên hệ HR để biết thêm chi tiết.",
            "maternity": "Nhân viên đủ điều kiện nhận 12 tuần nghỉ thai sản có lương và 4 tuần nghỉ sinh con có lương. Liên hệ HR để biết yêu cầu điều kiện cụ thể.",
            "holiday": "Các ngày lễ của công ty bao gồm Tết Dương lịch, Ngày Độc lập, Lễ Tạ ơn và Giáng sinh. Xem cổng HR để biết lịch nghỉ lễ đầy đủ.",
            "training": "Mỗi nhân viên nhận $2,000 hàng năm cho đào tạo và phát triển chuyên môn. Gửi yêu cầu qua Cổng Học tập để được phê duyệt.",
            "transfer": "Liên hệ HR để thảo luận về cơ hội chuyển bộ phận. Bạn phải hoàn thành ít nhất 1 năm ở vị trí hiện tại trước khi yêu cầu chuyển.",
            "overtime": "Làm thêm giờ được trả 1.5 lần mức lương thường. Tất cả làm thêm giờ phải được quản lý phê duyệt trước và ghi lại trong hệ thống HR.",
            "complaint": "Sử dụng đường dây HR ẩn danh hoặc gửi khiếu nại chính thức qua cổng HR. Tất cả khiếu nại được xử lý bảo mật và điều tra kịp thời.",
            "hours": "Giờ làm việc tiêu chuẩn là 9 AM đến 5 PM, Thứ Hai đến Thứ Sáu. Có thể sắp xếp linh hoạt với sự phê duyệt của quản lý.",
            "default": "Xin chào! Tôi là Trợ lý HR ở đây để giúp trả lời các câu hỏi của bạn về chính sách công ty, phúc lợi, nghỉ phép, lương bổng và nhiều hơn nữa. Tôi có quyền truy cập vào cơ sở dữ liệu FAQ HR với thông tin về nghỉ phép thường niên, chính sách làm việc từ xa, bảo hiểm y tế, kế hoạch hưu trí, phát triển chuyên môn và nhiều chủ đề HR khác. Bạn muốn biết điều gì?"
        }
    }
    
    lang_responses = responses.get(language, responses["en"])
    
    # Keywords for Vietnamese
    if language == "vi":
        vietnamese_keywords = {
            "nghỉ": "leave", "phép": "leave", "absent": "leave", "sick": "leave",
            "phúc lợi": "benefits", "bảo hiểm": "benefits", "y tế": "benefits",
            "lương": "salary", "tiền": "salary", "payroll": "salary", "salary": "salary",
            "từ xa": "remote", "wfh": "remote", "remote": "remote", "home": "remote",
            "hưu trí": "retirement", "401k": "retirement", "pension": "retirement",
            "thai sản": "maternity", "sinh con": "maternity", "con": "maternity",
            "lễ": "holiday", "nghỉ lễ": "holiday", "holiday": "holiday",
            "đào tạo": "training", "học": "training", "training": "training",
            "chuyển": "transfer", "bộ phận": "transfer", "department": "transfer",
            "tăng ca": "overtime", "overtime": "overtime",
            "khiếu nại": "complaint", "vấn đề": "complaint", "complaint": "complaint",
            "giờ": "hours", "time": "hours", "schedule": "hours"
        }
        
        for vn_keyword, en_category in vietnamese_keywords.items():
            if vn_keyword in question_lower:
                return responses[language].get(en_category, responses[language]["default"])
    
    # English keywords
    keywords_mapping = {
        ("leave", "vacation", "time off", "absent", "sick"): "leave",
        ("benefit", "insurance", "health"): "benefits", 
        ("salary", "pay", "payroll", "wage"): "salary",
        ("remote", "work from home", "wfh"): "remote",
        ("retirement", "401k", "pension"): "retirement",
        ("maternity", "paternity", "baby"): "maternity",
        ("holiday", "vacation"): "holiday",
        ("training", "development", "course", "learning"): "training",
        ("transfer", "department"): "transfer",
        ("overtime",): "overtime",
        ("complaint", "concern", "issue", "problem"): "complaint",
        ("hour", "schedule", "time"): "hours"
    }
    
    for keywords, category in keywords_mapping.items():
        if any(keyword in question_lower for keyword in keywords):
            return responses[language].get(category, responses[language]["default"])
    
    return responses[language]["default"]


@app.post("/api/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint.
    Processes user message through RAG and returns response with context.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )
    
    # Check for CV-related keywords to provide special handling
    cv_check_keywords = ["cv", "resume", "evaluate", "check", "score", "assess", "đánh giá", "kiểm tra"]
    cv_eval_keywords = ["evaluate", "score", "assess", "đánh giá"]
    message_lower = request.message.lower()
    is_cv_check_request = any(keyword in message_lower for keyword in cv_check_keywords)
    is_cv_eval_request = any(keyword in message_lower for keyword in cv_eval_keywords)
    
    print(f"[DEBUG] Message: '{request.message[:100]}...'")
    print(f"[DEBUG] Is CV check request: {is_cv_check_request}")
    print(f"[DEBUG] Is CV eval request: {is_cv_eval_request}")
    
    # If user is asking to evaluate CV (without providing actual CV content yet)
    if is_cv_check_request:
        # Check if this is just asking for evaluation options, not providing actual CV
        cv_content_keywords = ["experience", "skill", "education", "bachelor", "master", "project", "responsibility"]
        actual_cv_content = sum(1 for kw in cv_content_keywords if kw in message_lower) >= 2
        
        # If user sent "Evaluate my CV for positions: <content>", treat it as evaluation request
        if is_cv_eval_request and "evaluate" in message_lower:
            print(f"[DEBUG] Treating as CV evaluation request")
            actual_cv_content = True
        
        print(f"[DEBUG] Actual CV content: {actual_cv_content}")
        
        if not actual_cv_content:
            print(f"[DEBUG] Returning position list")
            # Just asking about CV evaluation - show position list
            if request.language == "vi":
                cv_response = {
                    "answer": (
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        "📋 DANH SÁCH CÁC VỊ TRÍ TUYỂN DỤNG\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        "Xin chào! Tôi có thể giúp đánh giá CV của bạn.\n"
                        "Vui lòng chọn vị trí tuyển dụng bên dưới:\n\n"
                        "🐍 1. Python Developer\n"
                        "☕ 2. Java Developer\n"
                        "🤖 3. AI/ML Engineer\n"
                        "🎨 4. Frontend Developer\n"
                        "🔧 5. DevOps Engineer\n"
                        "🚀 6. Full Stack Developer\n"
                        "📊 7. Data Engineer\n"
                        "✅ 8. QA Engineer\n\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        "📤 Hãy tải lên CV của bạn để bắt đầu đánh giá!"
                    ),
                    "source_documents": [],
                    "function_calls": []
                }
            else:
                cv_response = {
                    "answer": (
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        "📋 AVAILABLE POSITIONS FOR EVALUATION\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        "Hello! I can help evaluate your CV.\n"
                        "Please select a position below:\n\n"
                        "🐍 1. Python Developer\n"
                        "☕ 2. Java Developer\n"
                        "🤖 3. AI/ML Engineer\n"
                        "🎨 4. Frontend Developer\n"
                        "🔧 5. DevOps Engineer\n"
                        "🚀 6. Full Stack Developer\n"
                        "📊 7. Data Engineer\n"
                        "✅ 8. QA Engineer\n\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        "📤 Upload your CV to start evaluation!"
                    ),
                    "source_documents": [],
                    "function_calls": []
                }
            return ChatResponse(**cv_response)
    
    # Check if message contains CV content (has experience/skills/education keywords)
    cv_content_keywords = ["experience", "skill", "education", "bachelor", "master", "python", "java", "javascript", 
                           "developer", "engineer", "project", "responsibility", "achievement"]
    has_cv_content = sum(1 for kw in cv_content_keywords if kw in message_lower) >= 3
    
    # Special case: if message starts with "Evaluate my CV", extract position and evaluate
    if message_lower.startswith("evaluate my cv"):
        print(f"[DEBUG] Detected CV evaluation request")
        
        # Extract CV file info from message
        # Message format: "Evaluate my CV for [position]. File: [filename]. CV: [base64_content]"
        cv_file_content = ""
        cv_file_type = "txt"
        cv_content_for_eval = message_lower  # Initialize with fallback
        
        # Try to extract file type and base64 content from message
        if "|" in request.message:
            parts = request.message.split("|")
            if len(parts) >= 3:
                # Format: "position | filename | base64_content"
                cv_file_name = parts[1].strip()
                cv_file_content = parts[2].strip()
                
                # Detect file type from filename
                if cv_file_name.lower().endswith('.pdf'):
                    cv_file_type = 'pdf'
                elif cv_file_name.lower().endswith('.docx'):
                    cv_file_type = 'docx'
                elif cv_file_name.lower().endswith('.doc'):
                    cv_file_type = 'doc'
                else:
                    cv_file_type = 'txt'
                
                print(f"[DEBUG] Extracted file: {cv_file_name}, type: {cv_file_type}")
                
                # Extract text from file
                if cv_file_content:
                    try:
                        extracted_cv_text = extract_cv_content(cv_file_content, cv_file_type)
                        if extracted_cv_text:
                            cv_content_for_eval = extracted_cv_text
                            print(f"[OK] Successfully extracted CV text ({len(extracted_cv_text)} chars)")
                        else:
                            cv_content_for_eval = message_lower
                            print(f"[WARNING] Could not extract text, falling back to message")
                    except Exception as e:
                        print(f"[ERROR] CV extraction failed: {str(e)}")
                        cv_content_for_eval = message_lower
                else:
                    cv_content_for_eval = message_lower
        else:
            # Fallback: use message content directly
            cv_content_for_eval = message_lower
        
        # Position mapping with exact keywords
        positions_dict = {
            "python developer": "python_developer",
            "java developer": "java_developer",
            "ai/ml engineer": "ai_ml_engineer",
            "ai/ml": "ai_ml_engineer",
            "machine learning": "ai_ml_engineer",
            "frontend developer": "frontend_developer",
            "backend developer": "python_developer",
            "devops engineer": "devops_engineer",
            "full stack developer": "full_stack_developer",
            "data engineer": "data_engineer",
            "qa engineer": "qa_engineer",
            # Also try lowercase without "developer" suffix
            "python": "python_developer",
            "java": "java_developer",
            "frontend": "frontend_developer",
            "backend": "python_developer",
            "devops": "devops_engineer",
            "full stack": "full_stack_developer",
            "data": "data_engineer",
            "qa": "qa_engineer",
            "ai": "ai_ml_engineer",
            "ml": "ai_ml_engineer"
        }
        
        # Find position name in message (try longer matches first)
        position_key = None
        for pos_str, pos_key in sorted(positions_dict.items(), key=lambda x: len(x[0]), reverse=True):
            if pos_str in message_lower:
                position_key = pos_key
                print(f"[DEBUG] Matched position keyword: {pos_str}")
                break
        
        # If no position found, default to python developer
        if not position_key:
            position_key = "python_developer"
            print(f"[DEBUG] No position matched, using default: python_developer")
        
        from company_data import JOB_POSITIONS
        position = JOB_POSITIONS[position_key]
        print(f"[DEBUG] Evaluating for position: {position['name']}")
        
        cv_lower = cv_content_for_eval.lower()
        must_have_score = 0
        found_skills = []
        missing_must_haves = []
        
        # Enhanced skill matching function
        def skill_matches(skill_name, cv_text):
            skill_lower = skill_name.lower()
            cv_text_lower = cv_text.lower()
            
            # Direct match
            if skill_lower in cv_text_lower:
                return True
            
            # Check for partial word matches (more flexible)
            import re
            
            # Split skill into words and check if all words are present
            skill_words = re.findall(r'\w+', skill_lower)
            if len(skill_words) > 1:
                # For multi-word skills, check if all words appear somewhere in CV
                if all(word in cv_text_lower for word in skill_words):
                    return True
            
            # Check for common synonyms and variations
            synonyms = {
                "python": ["python", "py", "pyton"],
                "machine learning": ["machine learning", "ml", "artificial intelligence", "ai", "ai engineer", "machine", "learning", "predictive"],
                "ai": ["ai", "artificial intelligence", "machine learning", "ml", "ai engineer", "agi"],
                "data analysis": ["data analysis", "data analytics", "analytics", "data science", "analysis"],
                "tensorflow": ["tensorflow", "tf"],
                "pytorch": ["pytorch", "torch"],
                "nlp": ["nlp", "natural language processing", "language model", "text processing", "language models", "genai", "generative ai"],
                "computer vision": ["computer vision", "cv", "image processing", "vision"],
                "deep learning": ["deep learning", "neural network", "nn", "deep", "cnn", "rnn"],
                "langchain": ["langchain", "lang chain"],
                "llm": ["llm", "large language model", "language model", "gpt", "chatbot", "llms", "generative", "rag"],
                "faiss": ["faiss", "vector search", "similarity search", "vector database", "vector"],
                "hugging face": ["hugging face", "transformers", "hf"],
                "openai": ["openai", "gpt", "chatgpt"],
                "aws": ["aws", "amazon web services", "cloud", "sagemaker"],
                "azure": ["azure", "microsoft cloud"],
                "gcp": ["gcp", "google cloud", "google cloud platform"],
                "docker": ["docker", "containerization"],
                "kubernetes": ["kubernetes", "k8s"],
                "fastapi": ["fastapi", "api development"],
                "sql": ["sql", "database", "postgresql", "mysql"],
                "git": ["git", "version control", "github"],
                "deployment": ["deployment", "production", "devops", "ci/cd"],
                "leadership": ["leadership", "lead", "mentor", "team lead"],
                "communication": ["communication", "presentation", "collaboration"],
                "testing": ["testing", "qa", "unit test", "automation"]
            }
            
            # Check synonyms
            if skill_lower in synonyms:
                for synonym in synonyms[skill_lower]:
                    if synonym in cv_text_lower:
                        return True
            
            return False
        
        # Check must-have skills with enhanced matching
        for skill in position["must_have"]:
            if skill_matches(skill, cv_lower):
                must_have_score += 15
                found_skills.append(skill)
            else:
                missing_must_haves.append(skill)
        
        # Check nice-to-have skills
        nice_to_have_score = 0
        for skill in position["nice_to_have"]:
            if skill_matches(skill, cv_lower):
                nice_to_have_score += 5
                found_skills.append(skill)
        
        # Experience score
        experience_score = 5
        if "senior" in cv_lower or "lead" in cv_lower:
            experience_score = 20
        elif any(f"{i}+ years" in cv_lower or f"{i} years" in cv_lower for i in range(3, 10)):
            experience_score = 15
        
        # Education score
        education_score = 0
        if "bachelor" in cv_lower or "b.s." in cv_lower:
            education_score = 15
        if "master" in cv_lower or "m.s." in cv_lower:
            education_score = 10
        if "certification" in cv_lower:
            education_score += 5
        education_score = min(education_score, 25)
        
        # Soft skills
        soft_skills_score = min(sum(3 for s in ["communication", "leadership", "teamwork"] if s in cv_lower), 20)
        
        total_score = min(must_have_score + nice_to_have_score + experience_score + education_score + soft_skills_score, 100)
        
        # Determine rating - more flexible scoring
        missing_count = len(missing_must_haves)
        if missing_count > len(position['must_have']) * 0.5:
            # Missing more than 50% of must-haves
            rating = "Not Suitable"
        elif total_score >= 85:
            rating = "Excellent - Highly Recommended"
        elif total_score >= 75:
            rating = "Very Good - Recommended"
        elif total_score >= 60:
            rating = "Good - Consider for Interview"
        else:
            rating = "Below Threshold"
        
        # Analyze language skills
        language_skills = []
        language_keywords = {
            "english": ["english", "toefl", "ielts", "esl"],
            "chinese": ["chinese", "mandarin", "hsk"],
            "japanese": ["japanese", "jlpt"],
            "german": ["german", "goethe"],
            "french": ["french"],
            "spanish": ["spanish"],
            "vietnamese": ["vietnamese"]
        }
        
        for lang, keywords in language_keywords.items():
            if any(kw in cv_lower for kw in keywords):
                language_skills.append(lang.capitalize())
        
        # Analyze general strengths and improvement areas
        strengths = []
        improvements = []
        
        if must_have_score >= 15:
            strengths.append("Strong core technical skills")
        if experience_score >= 15:
            strengths.append("Good experience level")
        if education_score >= 15:
            strengths.append("Strong educational background")
        if soft_skills_score >= 10:
            strengths.append("Good soft skills demonstrated")
        
        if len(missing_must_haves) > 0:
            improvements.append(f"Missing key skills: {', '.join(missing_must_haves)}")
        if experience_score < 10:
            improvements.append("Need more years of experience")
        if education_score < 10:
            improvements.append("Consider formal certifications or degrees")
        if nice_to_have_score < 10:
            improvements.append("Develop additional technical skills")
        
        if request.language == "vi":
            # Calculate detail breakdown
            detail_breakdown = (
                f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📋 PHÂN TÍCH CHI TIẾT CV\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📌 TÓM TẮT CV VÀ KỸ NĂNG HIỆN CÓ:\n"
                f"   • Vị trí ứng tuyển: {position['name_vi']}\n"
                f"   • Tổng kỹ năng tìm thấy: {len(found_skills)} kỹ năng\n"
                f"   • Kỹ năng bắt buộc: {len(position['must_have'])} (Đã có: {must_have_score//15}/{len(position['must_have'])})\n"
                f"   • Kỹ năng khác: {len(position['nice_to_have'])} kỹ năng\n\n"
                f"🌍 ĐÁNH GIÁ KỸ NĂNG NGOẠI NGỮ:\n"
                f"   • Ngoại ngữ phát hiện: {', '.join(language_skills) if language_skills else '   Không phát hiện'}\n"
                f"   • Khuyến nghị: {('Tốt, có sự đa dạng ngoại ngữ' if len(language_skills) >= 1 else 'Nên cải thiện hoặc thêm chứng chỉ ngoại ngữ')}\n\n"
                f"💪 ĐIỂM MẠNH:\n"
            )
            for i, strength in enumerate(strengths, 1):
                detail_breakdown += f"   {i}. {strength}\n"
            if not strengths:
                detail_breakdown += "   Chưa phát hiện điểm mạnh nổi bật\n"
            
            detail_breakdown += f"\n⚠️ CẦN CẢI THIỆN:\n"
            for i, improvement in enumerate(improvements, 1):
                detail_breakdown += f"   {i}. {improvement}\n"
            if not improvements:
                detail_breakdown += "   Không có lĩnh vực cần cải thiện\n"
            
            detail_breakdown += (
                f"\n📊 CHI TIẾT ĐIỂM TỪNG TIÊU CHÍ:\n"
                f"   ┌─ Kỹ năng bắt buộc (Must-have skills)......: {must_have_score}/30 điểm\n"
                f"   ├─ Kỹ năng ngoài tùy chọn (Nice-to-have)....: {nice_to_have_score}/25 điểm\n"
                f"   ├─ Kinh nghiệm làm việc...................: {experience_score}/20 điểm\n"
                f"   ├─ Bằng cấp và chứng chỉ..................: {education_score}/15 điểm\n"
                f"   ├─ Kỹ năng mềm (Soft skills).............: {soft_skills_score}/10 điểm\n"
                f"   └─ TỔNG ĐIỂM..............................: {total_score}/100 điểm\n\n"
            )
            
            cv_eval_answer = (
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 KẾT QUẢ ĐÁNH GIÁ CV CHI TIẾT\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Vị trí: {position['name_vi']}\n"
                f"{'='*50}\n\n"
                f"📈 ĐIỂM TỔNG HỢP:\n"
                f"   Tổng điểm: {total_score}/100\n"
                f"   Tỷ lệ: {(total_score//20)*'█'}{'░'*(5-total_score//20)} ({total_score}%)\n"
                f"   Xếp hạng: {rating}\n\n"
                f"✅ KỸ NĂNG TÌM THẤY ({len(found_skills)} kỹ năng):\n"
                f"   {', '.join(found_skills) if found_skills else '   Không tìm thấy kỹ năng nào'}\n\n"
                f"⚠️ KỸ NĂNG BẮT BUỘC THIẾU ({len(missing_must_haves)}):\n"
                f"   {', '.join(missing_must_haves) if missing_must_haves else '   Không thiếu kỹ năng nào'}\n"
                f"{detail_breakdown}"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 NHẬN XÉT CHUNG:\n"
                f"   {('✨ Ứng viên xuất sắc! Rất phù hợp với vị trí này. Đủ năng lực, kinh nghiệm và tất cả kỹ năng bắt buộc.' if total_score >= 80 else '✓ Ứng viên khá phù hợp. Có đủ kỹ năng cơ bản, nên cải thiện thêm một vài kỹ năng.' if total_score >= 60 else '→ Cần cải thiện nhiều kỹ năng trước khi ứng tuyển vị trí này.')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
        else:
            # Calculate detail breakdown in English
            detail_breakdown = (
                f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📋 DETAILED CV ANALYSIS\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📌 CV SUMMARY & CURRENT SKILLS:\n"
                f"   • Target Position: {position['name']}\n"
                f"   • Total Skills Found: {len(found_skills)} skills\n"
                f"   • Required Skills: {len(position['must_have'])} (Have: {must_have_score//15}/{len(position['must_have'])})\n"
                f"   • Additional Skills: {len(position['nice_to_have'])} skills\n\n"
                f"🌍 LANGUAGE SKILLS EVALUATION:\n"
                f"   • Languages Detected: {', '.join(language_skills) if language_skills else 'None detected'}\n"
                f"   • Recommendation: {('Good diversity in languages' if len(language_skills) >= 1 else 'Consider adding language certifications')}\n\n"
                f"💪 STRENGTHS:\n"
            )
            for i, strength in enumerate(strengths, 1):
                detail_breakdown += f"   {i}. {strength}\n"
            if not strengths:
                detail_breakdown += "   No major strengths identified\n"
            
            detail_breakdown += f"\n⚠️ AREAS FOR IMPROVEMENT:\n"
            for i, improvement in enumerate(improvements, 1):
                detail_breakdown += f"   {i}. {improvement}\n"
            if not improvements:
                detail_breakdown += "   No areas need improvement\n"
            
            detail_breakdown += (
                f"\n📊 SCORE BREAKDOWN BY CRITERIA:\n"
                f"   ┌─ Must-have Skills.........................: {must_have_score}/30 points\n"
                f"   ├─ Nice-to-have Skills.....................: {nice_to_have_score}/25 points\n"
                f"   ├─ Work Experience.........................: {experience_score}/20 points\n"
                f"   ├─ Education & Certifications..............: {education_score}/15 points\n"
                f"   ├─ Soft Skills.............................: {soft_skills_score}/10 points\n"
                f"   └─ TOTAL SCORE..............................: {total_score}/100 points\n\n"
            )
            
            # Create clean, well-formatted CV evaluation response
            cv_eval_answer = (
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 DETAILED CV EVALUATION RESULT\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🎯 Position: {position['name']}\n"
                f"{'='*80}\n\n"
                f"📈 OVERALL SCORE:\n"
                f"   🏆 Total Points: {total_score}/100\n"
                f"   📊 Progress: {(total_score//20)*'█'}{'░'*(5-total_score//20)} ({total_score}%)\n"
                f"   ⭐ Rating: {rating}\n\n"
                f"✅ SKILLS FOUND ({len(found_skills)} skills):\n"
                f"   {', '.join(found_skills) if found_skills else '   ❌ No relevant skills found'}\n\n"
                f"⚠️ REQUIRED SKILLS MISSING ({len(missing_must_haves)} skills):\n"
                f"   {', '.join(missing_must_haves) if missing_must_haves else '   ✅ All required skills present'}\n"
                f"{detail_breakdown}"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 RECOMMENDATION:\n"
                f"   {('🌟 Excellent candidate! Perfect fit for this position with all required skills and experience.' if total_score >= 80 else '👍 Good candidate. Has core skills, consider improving additional technical skills.' if total_score >= 60 else '📚 Need significant skill development before applying for this position.')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
        
        return ChatResponse(
            answer=cv_eval_answer,
            source_documents=[
                {
                    "content": f"Position: {position['name']}, Required Skills: {', '.join(position['must_have'])}, Nice to Have: {', '.join(position['nice_to_have'])}",
                    "source": "CV Evaluation System",
                    "question": f"Evaluation for {position['name']}"
                }
            ],
            function_calls=[]
        )
    
    # If user is providing CV content and mentions a position
    if has_cv_content:
        # Extract position from message if mentioned
        positions = ["python", "java", "ai", "ml", "frontend", "backend", "devops", "full stack", "data", "qa"]
        position_mentioned = next((p for p in positions if p in message_lower), None)
        
        if position_mentioned:
            # Try to evaluate CV
            position_key = {
                "python": "python_developer",
                "java": "java_developer",
                "ai": "ai_ml_engineer",
                "ml": "ai_ml_engineer",
                "frontend": "frontend_developer",
                "backend": "python_developer",  # default backend
                "devops": "devops_engineer",
                "full stack": "full_stack_developer",
                "data": "data_engineer",
                "qa": "qa_engineer"
            }.get(position_mentioned, "python_developer")
            
            from company_data import JOB_POSITIONS
            position = JOB_POSITIONS[position_key]
            
            cv_lower = message_lower
            must_have_score = 0
            found_skills = []
            missing_must_haves = []
            
            # Enhanced skill matching function
            def skill_matches(skill_name, cv_text):
                skill_lower = skill_name.lower()
                cv_text_lower = cv_text.lower()
                
                # Direct match
                if skill_lower in cv_text_lower:
                    return True
                
                # Check for common synonyms and variations
                synonyms = {
                    "python": ["python", "py", "pyton"],
                    "machine learning": ["machine learning", "ml", "artificial intelligence", "ai", "ai engineer", "machine", "learning", "predictive"],
                    "ai": ["ai", "artificial intelligence", "machine learning", "ml", "ai engineer", "agi"],
                    "data analysis": ["data analysis", "data analytics", "analytics", "data science"],
                    "tensorflow": ["tensorflow", "tf"],
                    "pytorch": ["pytorch", "torch"],
                    "nlp": ["nlp", "natural language processing", "language model", "text processing", "genai", "generative ai"],
                    "computer vision": ["computer vision", "cv", "image processing", "vision"],
                    "deep learning": ["deep learning", "neural network", "nn", "cnn", "rnn"],
                    "langchain": ["langchain", "lang chain"],
                    "llm": ["llm", "large language model", "language model", "gpt", "chatbot", "generative", "rag"],
                    "faiss": ["faiss", "vector search", "similarity search", "vector database"],
                    "docker": ["docker", "containerization"],
                    "kubernetes": ["kubernetes", "k8s"],
                    "fastapi": ["fastapi", "api development"],
                    "deployment": ["deployment", "production", "devops"]
                }
                
                # Check synonyms
                if skill_lower in synonyms:
                    for synonym in synonyms[skill_lower]:
                        if synonym in cv_text_lower:
                            return True
                
                return False
            
            # Check must-have skills with enhanced matching
            for skill in position["must_have"]:
                if skill_matches(skill, cv_lower):
                    must_have_score += 15
                    found_skills.append(skill)
                else:
                    missing_must_haves.append(skill)
            
            # Check nice-to-have skills
            nice_to_have_score = 0
            for skill in position["nice_to_have"]:
                if skill_matches(skill, cv_lower):
                    nice_to_have_score += 5
                    found_skills.append(skill)
            
            # Experience score
            experience_score = 5
            if "senior" in cv_lower or "lead" in cv_lower:
                experience_score = 20
            elif any(f"{i}+ years" in cv_lower or f"{i} years" in cv_lower for i in range(3, 10)):
                experience_score = 15
            
            # Education score
            education_score = 0
            if "bachelor" in cv_lower or "b.s." in cv_lower:
                education_score = 15
            if "master" in cv_lower or "m.s." in cv_lower:
                education_score = 10
            if "certification" in cv_lower:
                education_score += 5
            education_score = min(education_score, 25)
            
            # Soft skills
            soft_skills_score = min(sum(3 for s in ["communication", "leadership", "teamwork"] if s in cv_lower), 20)
            
            total_score = min(must_have_score + nice_to_have_score + experience_score + education_score + soft_skills_score, 100)
            
            # Determine rating - more flexible scoring
            missing_count = len(missing_must_haves)
            if missing_count > len(position['must_have']) * 0.5:
                # Missing more than 50% of must-haves
                rating = "Not Suitable"
            elif total_score >= 85:
                rating = "Excellent - Highly Recommended"
            elif total_score >= 75:
                rating = "Very Good - Recommended"
            elif total_score >= 60:
                rating = "Good - Consider for Interview"
            else:
                rating = "Below Threshold"
            
            # Analyze language skills
            language_skills = []
            language_keywords = {
                "english": ["english", "toefl", "ielts", "esl"],
                "chinese": ["chinese", "mandarin", "hsk"],
                "japanese": ["japanese", "jlpt"],
                "german": ["german", "goethe"],
                "french": ["french"],
                "spanish": ["spanish"],
                "vietnamese": ["vietnamese"]
            }
            
            for lang, keywords in language_keywords.items():
                if any(kw in cv_lower for kw in keywords):
                    language_skills.append(lang.capitalize())
            
            # Analyze general strengths and improvement areas
            strengths = []
            improvements = []
            
            if must_have_score >= 15:
                strengths.append("Strong core technical skills")
            if experience_score >= 15:
                strengths.append("Good experience level")
            if education_score >= 15:
                strengths.append("Strong educational background")
            if soft_skills_score >= 10:
                strengths.append("Good soft skills demonstrated")
            
            if len(missing_must_haves) > 0:
                improvements.append(f"Missing key skills: {', '.join(missing_must_haves)}")
            if experience_score < 10:
                improvements.append("Need more years of experience")
            if education_score < 10:
                improvements.append("Consider formal certifications or degrees")
            if nice_to_have_score < 10:
                improvements.append("Develop additional technical skills")
            
            if request.language == "vi":
                # Calculate detail breakdown
                detail_breakdown = (
                    f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📋 PHÂN TÍCH CHI TIẾT CV\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📌 TÓM TẮT CV VÀ KỸ NĂNG HIỆN CÓ:\n"
                    f"   • Vị trí ứng tuyển: {position['name_vi']}\n"
                    f"   • Tổng kỹ năng tìm thấy: {len(found_skills)} kỹ năng\n"
                    f"   • Kỹ năng bắt buộc: {len(position['must_have'])} (Đã có: {must_have_score//15}/{len(position['must_have'])})\n"
                    f"   • Kỹ năng khác: {len(position['nice_to_have'])} kỹ năng\n\n"
                    f"🌍 ĐÁNH GIÁ KỸ NĂNG NGOẠI NGỮ:\n"
                    f"   • Ngoại ngữ phát hiện: {', '.join(language_skills) if language_skills else '   Không phát hiện'}\n"
                    f"   • Khuyến nghị: {('Tốt, có sự đa dạng ngoại ngữ' if len(language_skills) >= 1 else 'Nên cải thiện hoặc thêm chứng chỉ ngoại ngữ')}\n\n"
                    f"💪 ĐIỂM MẠNH:\n"
                )
                for i, strength in enumerate(strengths, 1):
                    detail_breakdown += f"   {i}. {strength}\n"
                if not strengths:
                    detail_breakdown += "   Chưa phát hiện điểm mạnh nổi bật\n"
                
                detail_breakdown += f"\n⚠️ CẦN CẢI THIỆN:\n"
                for i, improvement in enumerate(improvements, 1):
                    detail_breakdown += f"   {i}. {improvement}\n"
                if not improvements:
                    detail_breakdown += "   Không có lĩnh vực cần cải thiện\n"
                
                detail_breakdown += (
                    f"\n📊 CHI TIẾT ĐIỂM TỪNG TIÊU CHÍ:\n"
                    f"   ┌─ Kỹ năng bắt buộc (Must-have skills)......: {must_have_score}/30 điểm\n"
                    f"   ├─ Kỹ năng ngoài tùy chọn (Nice-to-have)....: {nice_to_have_score}/25 điểm\n"
                    f"   ├─ Kinh nghiệm làm việc...................: {experience_score}/20 điểm\n"
                    f"   ├─ Bằng cấp và chứng chỉ..................: {education_score}/15 điểm\n"
                    f"   ├─ Kỹ năng mềm (Soft skills).............: {soft_skills_score}/10 điểm\n"
                    f"   └─ TỔNG ĐIỂM..............................: {total_score}/100 điểm\n\n"
                )
                
                cv_eval_answer = (
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 KẾT QUẢ ĐÁNH GIÁ CV CHI TIẾT\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Vị trí: {position['name_vi']}\n"
                    f"{'='*50}\n\n"
                    f"📈 ĐIỂM TỔNG HỢP:\n"
                    f"   Tổng điểm: {total_score}/100\n"
                    f"   Tỷ lệ: {(total_score//20)*'█'}{'░'*(5-total_score//20)} ({total_score}%)\n"
                    f"   Xếp hạng: {rating}\n\n"
                    f"✅ KỸ NĂNG TÌM THẤY ({len(found_skills)} kỹ năng):\n"
                    f"   {', '.join(found_skills) if found_skills else '   Không tìm thấy kỹ năng nào'}\n\n"
                    f"⚠️ KỸ NĂNG BẮT BUỘC THIẾU ({len(missing_must_haves)}):\n"
                    f"   {', '.join(missing_must_haves) if missing_must_haves else '   Không thiếu kỹ năng nào'}\n"
                    f"{detail_breakdown}"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"💡 NHẬN XÉT CHUNG:\n"
                    f"   {('✨ Ứng viên xuất sắc! Rất phù hợp với vị trí này. Đủ năng lực, kinh nghiệm và tất cả kỹ năng bắt buộc.' if total_score >= 80 else '✓ Ứng viên khá phù hợp. Có đủ kỹ năng cơ bản, nên cải thiện thêm một vài kỹ năng.' if total_score >= 60 else '→ Cần cải thiện nhiều kỹ năng trước khi ứng tuyển vị trí này.')}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                )
            else:
                # Calculate detail breakdown in English
                detail_breakdown = (
                    f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📋 DETAILED CV ANALYSIS\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📌 CV SUMMARY & CURRENT SKILLS:\n"
                    f"   • Target Position: {position['name']}\n"
                    f"   • Total Skills Found: {len(found_skills)} skills\n"
                    f"   • Required Skills: {len(position['must_have'])} (Have: {must_have_score//15}/{len(position['must_have'])})\n"
                    f"   • Additional Skills: {len(position['nice_to_have'])} skills\n\n"
                    f"🌍 LANGUAGE SKILLS EVALUATION:\n"
                    f"   • Languages Detected: {', '.join(language_skills) if language_skills else 'None detected'}\n"
                    f"   • Recommendation: {('Good diversity in languages' if len(language_skills) >= 1 else 'Consider adding language certifications')}\n\n"
                    f"💪 STRENGTHS:\n"
                )
                for i, strength in enumerate(strengths, 1):
                    detail_breakdown += f"   {i}. {strength}\n"
                if not strengths:
                    detail_breakdown += "   No major strengths identified\n"
                
                detail_breakdown += f"\n⚠️ AREAS FOR IMPROVEMENT:\n"
                for i, improvement in enumerate(improvements, 1):
                    detail_breakdown += f"   {i}. {improvement}\n"
                if not improvements:
                    detail_breakdown += "   No areas need improvement\n"
                
                detail_breakdown += (
                    f"\n📊 SCORE BREAKDOWN BY CRITERIA:\n"
                    f"   ┌─ Must-have Skills.........................: {must_have_score}/30 points\n"
                    f"   ├─ Nice-to-have Skills.....................: {nice_to_have_score}/25 points\n"
                    f"   ├─ Work Experience.........................: {experience_score}/20 points\n"
                    f"   ├─ Education & Certifications..............: {education_score}/15 points\n"
                    f"   ├─ Soft Skills.............................: {soft_skills_score}/10 points\n"
                    f"   └─ TOTAL SCORE..............................: {total_score}/100 points\n\n"
                )
                
                # Create clean, well-formatted CV evaluation response
                cv_eval_answer = (
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 DETAILED CV EVALUATION RESULT\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"🎯 Position: {position['name']}\n"
                    f"{'='*80}\n\n"
                    f"📈 OVERALL SCORE:\n"
                    f"   🏆 Total Points: {total_score}/100\n"
                    f"   📊 Progress: {(total_score//20)*'█'}{'░'*(5-total_score//20)} ({total_score}%)\n"
                    f"   ⭐ Rating: {rating}\n\n"
                    f"✅ SKILLS FOUND ({len(found_skills)} skills):\n"
                    f"   {', '.join(found_skills) if found_skills else '   ❌ No relevant skills found'}\n\n"
                    f"⚠️ REQUIRED SKILLS MISSING ({len(missing_must_haves)} skills):\n"
                    f"   {', '.join(missing_must_haves) if missing_must_haves else '   ✅ All required skills present'}\n"
                    f"{detail_breakdown}"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"💡 RECOMMENDATION:\n"
                    f"   {('🌟 Excellent candidate! Perfect fit for this position with all required skills and experience.' if total_score >= 80 else '👍 Good candidate. Has core skills, consider improving additional technical skills.' if total_score >= 60 else '📚 Need significant skill development before applying for this position.')}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                )
            
            return ChatResponse(
                answer=cv_eval_answer,
                source_documents=[
                    {
                        "content": f"Position: {position['name']}, Required Skills: {', '.join(position['must_have'])}, Nice to Have: {', '.join(position['nice_to_have'])}",
                        "source": "CV Evaluation System",
                        "question": f"Evaluation for {position['name']}"
                    }
                ],
                function_calls=[]
            )
    
    # If RAG system is not initialized, provide a helpful response
    if not llm or not retriever:
        demo_response = (
            "Welcome to the Internal HR Assistant! "
            "I'm currently in demo mode because the Azure OpenAI credentials are not yet configured. "
            "Please ensure your .env file has valid AZURE_OPENAI_* credentials and restart the server. "
            "In demo mode, I can acknowledge your question: '" + request.message[:50] + "...' "
            "but cannot provide actual HR information yet. "
            "Restart the server once credentials are configured."
        )
        return ChatResponse(
            answer=demo_response,
            source_documents=[
                {
                    "content": "Demo mode - RAG system not initialized",
                    "source": "system",
                    "question": "Configuration Status"
                }
            ],
            function_calls=[]
        )
    
    try:
        print(f"\n[CHAT] Processing message: '{request.message[:50]}...'")
        print(f"[CHAT] Language: {request.language}")
        
        # Get relevant documents from vector store
        # Use invoke() instead of get_relevant_documents() for newer LangChain versions
        print("[1] Retrieving relevant documents...")
        relevant_docs = retriever.invoke(request.message)
        print(f"[OK] Found {len(relevant_docs)} documents")
        
        # Format context from documents
        print("[2] Formatting context...")
        context_str = "\n\n".join([
            f"From FAQ: {doc.metadata.get('question', 'Unknown')}\n{doc.page_content[:300]}"
            for doc in relevant_docs[:3]
        ])
        print(f"[OK] Context formatted ({len(context_str)} chars)")
        
        # Create prompt for LLM with language support
        if request.language == 'vi':
            system_prompt = (
                "Bạn là một Trợ lý HR hữu ích của công ty Galacy Software. "
                "Trả lời các câu hỏi về chính sách công ty, phúc lợi, quy trình và tuyển dụng. "
                "Khi người dùng hỏi về đánh giá CV, gợi ý vị trí tuyển dụng, hoặc upload CV, "
                "bạn nên gọi function get_job_positions để lấy danh sách vị trí, "
                "rồi gọi function evaluate_cv_for_position để chấm điểm CV cho vị trí đó. "
                "Hãy trả lời ngắn gọn, thân thiện bằng tiếng Việt."
            )
            user_prompt = f"""Dựa trên thông tin HR sau, trả lời câu hỏi của người dùng bằng tiếng Việt:

Ngữ cảnh:
{context_str}

Câu hỏi: {request.message}

Trả lời:"""
        else:
            system_prompt = (
                "You are a helpful HR Assistant for Galacy Software. "
                "Answer questions about company policies, benefits, procedures, and recruitment. "
                "When users ask about CV evaluation, job positions, or CV upload, "
                "you should call get_job_positions function to list available positions, "
                "then call evaluate_cv_for_position function to score the CV for that position. "
                "Be concise and friendly."
            )
            user_prompt = f"""Based on the following HR information, answer the user's question:

Context:
{context_str}

User Question: {request.message}

Answer:"""
        
        # Get response from LLM
        print("[3] Calling LLM...")
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = llm.invoke(messages)
            answer = response.content
        except Exception as llm_error:
            print(f"[WARNING] LLM failed ({str(llm_error)[:50]}...), using fallback response")
            # Use the retrieved documents to provide a better fallback response
            answer = get_fallback_response(request.message, request.language)
            # Also ensure we return formatted sources from retrieval
            formatted_sources = []
            for doc in relevant_docs[:3]:
                translated_question = translate_faq_question(
                    doc.metadata.get("question", ""),
                    request.language
                )
                formatted_sources.append({
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "source": doc.metadata.get("source", "Unknown"),
                    "question": translated_question
                })
            print(f"[OK] Fallback response provided with {len(formatted_sources)} sources")
            print("[SUCCESS] Chat message processed with fallback\n")
            return ChatResponse(
                answer=answer,
                source_documents=formatted_sources,
                function_calls=[]
            )
        
        print(f"[OK] Response received ({len(answer)} chars)")
        
        # Format source documents
        print("[4] Formatting sources...")
        formatted_sources = []
        for doc in relevant_docs[:3]:
            translated_question = translate_faq_question(
                doc.metadata.get("question", ""),
                request.language
            )
            formatted_sources.append({
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "source": doc.metadata.get("source", "Unknown"),
                "question": translated_question
            })
        print(f"[OK] {len(formatted_sources)} sources formatted")
        
        print("[SUCCESS] Chat message processed successfully\n")
        
        return ChatResponse(
            answer=answer,
            source_documents=formatted_sources,
            function_calls=[]
        )
    
    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        print(f"\n[ERROR] {error_msg}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/faq")
async def get_faq_count():
    """
    Get statistics about the FAQ database.
    """
    try:
        import csv
        faq_count = 0
        with open("data/hr_faq.csv", 'r', encoding='utf-8') as f:
            faq_count = sum(1 for _ in csv.DictReader(f))
        
        return {
            "total_faqs": faq_count,
            "vector_store_ready": vector_store is not None
        }
    except Exception as e:
        return {
            "error": str(e),
            "total_faqs": 0
        }


# Root endpoint
class CVRequest(BaseModel):
    """Request model for CV evaluation endpoint"""
    cv_text: str


@app.post("/api/evaluate-cv")
async def evaluate_cv_endpoint(request: CVRequest):
    """
    Test endpoint to directly evaluate a CV using the evaluation function.
    """
    try:
        # Import the function and call it directly (not as a tool)
        from function_tools import _evaluate_cv_logic
        
        # Call the CV evaluation logic directly
        result = _evaluate_cv_logic(request.cv_text)
        
        # Parse the JSON result
        import json
        evaluation = json.loads(result)
        
        return {
            "status": "success",
            "evaluation": evaluation
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating CV: {str(e)}")


@app.get("/api/job-positions")
async def get_job_positions_endpoint():
    """Get all available job positions"""
    from company_data import JOB_POSITIONS
    
    positions = {}
    for key, position in JOB_POSITIONS.items():
        positions[key] = {
            "name": position["name"],
            "name_vi": position["name_vi"],
            "description": position["description"],
            "must_have_skills": position["must_have"],
            "nice_to_have_skills": position["nice_to_have"],
            "min_experience": f"{position['experience_min']}+ years"
        }
    
    return {"positions": positions}


@app.post("/api/evaluate-cv-for-position")
async def evaluate_cv_for_position_endpoint(request: CVRequest):
    """
    Evaluate CV for a specific position.
    """
    position_key = request.cv_text.split("|")[0].strip() if "|" in request.cv_text else "python_developer"
    cv_text = request.cv_text.split("|")[1].strip() if "|" in request.cv_text else request.cv_text
    
    from company_data import JOB_POSITIONS, SKILL_SCORES
    import json
    
    if position_key not in JOB_POSITIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid position: {position_key}. Available: {list(JOB_POSITIONS.keys())}"
        )
    
    position = JOB_POSITIONS[position_key]
    cv_lower = cv_text.lower()
    
    # Score calculation
    must_have_score = 0
    nice_to_have_score = 0
    found_skills = []
    missing_must_haves = []
    
    # Check must-have skills
    for skill in position["must_have"]:
        if skill.lower() in cv_lower:
            must_have_score += 15
            found_skills.append(skill)
        else:
            missing_must_haves.append(skill)
    
    # Check nice-to-have skills
    for skill in position["nice_to_have"]:
        if skill.lower() in cv_lower:
            nice_to_have_score += 5
            found_skills.append(skill)
    
    # Experience score
    experience_score = 5
    if "senior" in cv_lower or "lead" in cv_lower:
        experience_score = 20
    elif any(f"{i}+ years" in cv_lower or f"{i} years" in cv_lower for i in range(3, 10)):
        experience_score = 15
    
    # Education score
    education_score = 0
    if "bachelor" in cv_lower or "b.s." in cv_lower:
        education_score = 15
    if "master" in cv_lower or "m.s." in cv_lower:
        education_score = 10
    if "certification" in cv_lower or "certified" in cv_lower:
        education_score += 5
    education_score = min(education_score, 25)
    
    # Soft skills
    soft_skills_score = 0
    soft_skills = ["communication", "leadership", "teamwork", "problem solving"]
    for skill in soft_skills:
        if skill in cv_lower:
            soft_skills_score += 3
    soft_skills_score = min(soft_skills_score, 20)
    
    # Total score
    total_score = must_have_score + nice_to_have_score + experience_score + education_score + soft_skills_score
    total_score = min(total_score, 100)
    
    # Rating
    if len(missing_must_haves) > 0:
        rating = "Not Suitable"
    elif total_score >= 85:
        rating = "Excellent"
    elif total_score >= 75:
        rating = "Very Good"
    elif total_score >= 60:
        rating = "Good"
    elif total_score >= 50:
        rating = "Acceptable"
    else:
        rating = "Below Threshold"
    
    return {
        "position": position["name"],
        "score": total_score,
        "rating": rating,
        "found_skills": list(set(found_skills)),
        "missing_required_skills": missing_must_haves,
        "recommendations": ["Improve missing skills" if missing_must_haves else "Good match!"]
    }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Internal HR Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /api/health",
            "chat": "POST /api/chat",
            "faq": "GET /api/faq",
            "evaluate-cv": "POST /api/evaluate-cv",
            "job-positions": "GET /api/job-positions",
            "evaluate-cv-for-position": "POST /api/evaluate-cv-for-position"
        },
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
