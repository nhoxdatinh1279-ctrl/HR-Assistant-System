"""
Job positions and skill requirements for CV evaluation
"""

JOB_POSITIONS = {
    "python_developer": {
        "name": "Python Developer",
        "name_vi": "Lập Trình Viên Python",
        "skills": ["Python", "Django", "FastAPI", "Flask", "SQL", "REST API"],
        "must_have": ["Python", "SQL"],
        "nice_to_have": ["Django", "FastAPI", "Docker", "Git"],
        "experience_min": 2,
        "description": "Develop backend services using Python frameworks"
    },
    "java_developer": {
        "name": "Java Developer",
        "name_vi": "Lập Trình Viên Java",
        "skills": ["Java", "Spring", "Spring Boot", "SQL", "Maven", "REST API"],
        "must_have": ["Java", "Spring Boot"],
        "nice_to_have": ["Spring Data", "Docker", "Microservices", "Git"],
        "experience_min": 2,
        "description": "Develop enterprise Java applications"
    },
    "ai_ml_engineer": {
        "name": "AI/ML Engineer",
        "name_vi": "Kỹ Sư AI/Machine Learning",
        "skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "Deep Learning", "Data Analysis", "NLP", "Computer Vision", "LLM", "GPT", "LangChain", "FAISS", "AI", "ML", "Artificial Intelligence"],
        "must_have": ["Python", "Machine Learning", "AI"],
        "nice_to_have": ["TensorFlow", "PyTorch", "NLP", "Computer Vision", "Deep Learning", "LangChain", "FAISS", "LLM", "GPT", "OpenAI", "Transformers", "Hugging Face"],
        "experience_min": 1,
        "description": "Build AI/ML models and solutions"
    },
    "frontend_developer": {
        "name": "Frontend Developer",
        "name_vi": "Lập Trình Viên Frontend",
        "skills": ["JavaScript", "React", "Vue", "CSS", "HTML", "TypeScript"],
        "must_have": ["JavaScript", "React"],
        "nice_to_have": ["TypeScript", "Tailwind CSS", "Next.js", "Redux"],
        "experience_min": 2,
        "description": "Build responsive web interfaces"
    },
    "devops_engineer": {
        "name": "DevOps Engineer",
        "name_vi": "Kỹ Sư DevOps",
        "skills": ["Docker", "Kubernetes", "CI/CD", "Linux", "Git", "AWS"],
        "must_have": ["Docker", "CI/CD", "Linux"],
        "nice_to_have": ["Kubernetes", "AWS", "Terraform", "Jenkins"],
        "experience_min": 2,
        "description": "Manage infrastructure and deployment"
    },
    "full_stack_developer": {
        "name": "Full Stack Developer",
        "name_vi": "Lập Trình Viên Full Stack",
        "skills": ["JavaScript", "React", "Node.js", "SQL", "Docker", "REST API"],
        "must_have": ["JavaScript", "React", "Node.js"],
        "nice_to_have": ["TypeScript", "MongoDB", "Docker", "AWS"],
        "experience_min": 3,
        "description": "Build complete web applications"
    },
    "data_engineer": {
        "name": "Data Engineer",
        "name_vi": "Kỹ Sư Dữ Liệu",
        "skills": ["SQL", "Python", "Spark", "Data Warehouse", "ETL", "Big Data"],
        "must_have": ["SQL", "Python", "ETL"],
        "nice_to_have": ["Spark", "Hadoop", "Data Warehouse", "Airflow"],
        "experience_min": 2,
        "description": "Build data infrastructure and pipelines"
    },
    "qa_engineer": {
        "name": "QA Engineer",
        "name_vi": "Kỹ Sư Kiểm Thử",
        "skills": ["Testing", "Automation", "Selenium", "Python", "API Testing", "SQL"],
        "must_have": ["Testing", "Automation"],
        "nice_to_have": ["Selenium", "Python", "API Testing", "Jenkins"],
        "experience_min": 1,
        "description": "Ensure software quality through testing"
    }
}

# Scoring criteria for each skill
SKILL_SCORES = {
    # Language/Framework skills
    "Python": 10,
    "Java": 10,
    "JavaScript": 10,
    "TypeScript": 8,
    "SQL": 8,
    "Go": 8,
    "C++": 8,
    "Rust": 8,
    
    # Web Frameworks
    "React": 10,
    "Vue": 9,
    "Angular": 9,
    "Django": 10,
    "FastAPI": 10,
    "Spring": 10,
    "Spring Boot": 10,
    "Node.js": 10,
    "Express": 8,
    "Flask": 8,
    
    # DevOps/Infrastructure
    "Docker": 8,
    "Kubernetes": 9,
    "AWS": 8,
    "Azure": 8,
    "GCP": 8,
    "CI/CD": 8,
    "Jenkins": 7,
    "GitHub Actions": 7,
    "Terraform": 7,
    
    # Databases
    "MongoDB": 7,
    "PostgreSQL": 8,
    "MySQL": 8,
    "Redis": 7,
    "Elasticsearch": 7,
    "DynamoDB": 6,
    
    # Data & AI
    "Machine Learning": 10,
    "Deep Learning": 10,
    "TensorFlow": 10,
    "PyTorch": 10,
    "Scikit-learn": 8,
    "Data Analysis": 8,
    "NLP": 9,
    "Computer Vision": 9,
    "Pandas": 8,
    "NumPy": 8,
    "AI": 10,
    "ML": 10,
    "Artificial Intelligence": 10,
    "LLM": 10,
    "Large Language Models": 10,
    "GPT": 9,
    "OpenAI": 9,
    "LangChain": 9,
    "FAISS": 8,
    "Hugging Face": 8,
    "Transformers": 9,
    "RAG": 9,
    "Vector Database": 8,
    "Pinecone": 7,
    "Weaviate": 7,
    "Claude": 8,
    "Gemini": 8,
    "LLaMA": 8,
    
    # Testing
    "Testing": 8,
    "Automation": 8,
    "Selenium": 8,
    "Jest": 7,
    "Pytest": 8,
    "API Testing": 7,
    
    # Tools & Others
    "Git": 8,
    "REST API": 8,
    "GraphQL": 8,
    "Linux": 8,
    "Agile": 6,
    "Scrum": 6,
    "JIRA": 5,
}

# Experience multiplier
EXPERIENCE_MULTIPLIER = {
    "0-1": 0.5,
    "1-2": 1.0,
    "2-3": 1.3,
    "3-5": 1.5,
    "5-7": 1.7,
    "7-10": 1.9,
    "10+": 2.0
}

def get_job_position(position_key):
    """Get job position details"""
    return JOB_POSITIONS.get(position_key, None)

def get_all_positions():
    """Get all available positions"""
    return JOB_POSITIONS

def get_position_names():
    """Get list of position names with Vietnamese names"""
    return {key: f"{val['name']} ({val['name_vi']})" 
            for key, val in JOB_POSITIONS.items()}
