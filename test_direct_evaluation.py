#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the enhanced CV evaluation logic directly without running the server
"""

import sys
import os

# Add the backend path to sys.path
backend_path = r"c:\Code\AI\Learn AI\WORKSHOP 4\backend"
sys.path.insert(0, backend_path)

# Import our evaluation functions
from company_data import JOB_POSITIONS

def enhanced_skill_matches(skill_name, cv_text):
    """Enhanced skill matching function (copy from app.py)"""
    import re
    skill_lower = skill_name.lower()
    cv_text_lower = cv_text.lower()
    
    # Direct match
    if skill_lower in cv_text_lower:
        return True
    
    # Check for partial word matches (more flexible)
    skill_words = re.findall(r'\w+', skill_lower)
    if len(skill_words) > 1:
        # For multi-word skills, check if all words are present
        if all(word in cv_text_lower for word in skill_words):
            return True
    
    # Check for common synonyms and variations
    synonyms = {
        "python": ["python", "py"],
        "machine learning": ["machine learning", "ml", "artificial intelligence", "ai", "ai engineer", "machine", "learning"],
        "ai": ["ai", "artificial intelligence", "machine learning", "ml", "ai engineer"],
        "data analysis": ["data analysis", "data analytics", "analytics", "data science", "analysis"],
        "tensorflow": ["tensorflow", "tf"],
        "pytorch": ["pytorch", "torch"],
        "nlp": ["nlp", "natural language processing", "language model", "text processing", "language models"],
        "computer vision": ["computer vision", "cv", "image processing", "vision"],
        "deep learning": ["deep learning", "neural network", "nn", "deep"],
        "langchain": ["langchain", "lang chain"],
        "llm": ["llm", "large language model", "language model", "gpt", "chatbot", "llms"],
        "faiss": ["faiss", "vector search", "similarity search", "vector database", "vector"],
    }
    
    # Check synonyms
    if skill_lower in synonyms:
        for synonym in synonyms[skill_lower]:
            if synonym in cv_text_lower:
                return True
    
    return False

def evaluate_cv_enhanced(cv_text, position_name):
    """Enhanced CV evaluation logic"""
    
    # Get position details
    position = JOB_POSITIONS.get(position_name)
    if not position:
        return f"Position '{position_name}' not found"
    
    # Skills scoring
    must_have_skills = position["must_have_skills"]
    nice_to_have_skills = position["nice_to_have_skills"]
    
    found_must_have = []
    found_nice_to_have = []
    
    for skill in must_have_skills:
        if enhanced_skill_matches(skill, cv_text):
            found_must_have.append(skill)
    
    for skill in nice_to_have_skills:
        if enhanced_skill_matches(skill, cv_text):
            found_nice_to_have.append(skill)
    
    # Calculate scores
    must_have_score = (len(found_must_have) / len(must_have_skills)) * 40
    nice_to_have_score = (len(found_nice_to_have) / len(nice_to_have_skills)) * 20
    
    # Experience scoring (simple keyword check)
    cv_lower = cv_text.lower()
    experience_score = 0
    if any(exp in cv_lower for exp in ["senior", "lead", "principal", "head", "manager"]):
        experience_score += 10
    if any(exp in cv_lower for exp in ["10+ years", "over 10 years", "more than 10", "10 years"]):
        experience_score += 10
    
    # Education scoring
    education_score = 0
    if any(edu in cv_lower for edu in ["ms", "master", "phd", "doctorate", "stanford", "mit", "berkeley"]):
        education_score += 10
    
    total_score = must_have_score + nice_to_have_score + experience_score + education_score
    
    return {
        "position": position_name,
        "total_score": min(100, round(total_score, 1)),
        "must_have_skills": {
            "required": must_have_skills,
            "found": found_must_have,
            "score": round(must_have_score, 1)
        },
        "nice_to_have_skills": {
            "required": nice_to_have_skills,
            "found": found_nice_to_have,
            "score": round(nice_to_have_score, 1)
        },
        "experience_score": experience_score,
        "education_score": education_score
    }

# David Tran's CV content
david_cv = """David Tran
Senior AI Engineer
Over 10 years of experience in machine learning and deep learning solutions.

EXPERIENCE:
• Senior AI Engineer at TechCorp (2018-present)
• Lead ML Engineer at DataSoft (2015-2018) 
• AI Researcher at Innovation Labs (2012-2015)

SKILLS:
• Programming: Python, R, Java, C++
• AI/ML: TensorFlow, PyTorch, scikit-learn, Keras
• Deep Learning: CNN, RNN, LSTM, Transformers
• MLOps: Docker, Kubernetes, MLflow
• Cloud: AWS, Azure, GCP
• Databases: PostgreSQL, MongoDB
• Tools: Git, Jupyter, VS Code

PROJECTS:
• Built LLMs using LangChain and OpenAI GPT-3.5/4
• Implemented FAISS vector databases for similarity search
• Developed computer vision models for medical imaging
• Created NLP chatbots using Hugging Face transformers

EDUCATION:
• MS Computer Science - Stanford University (2012)
• BS Software Engineering - UC Berkeley (2010)

Languages: English (Native), Vietnamese (Fluent)
"""

def test_enhanced_evaluation():
    print("🎯 Testing Enhanced CV Evaluation Logic")
    print("="*60)
    
    # Test David's CV for AI/ML Engineer position
    result = evaluate_cv_enhanced(david_cv, "AI/ML Engineer")
    
    print(f"👤 Candidate: David Tran (Senior AI Engineer)")
    print(f"📋 Position: {result['position']}")
    print(f"🏆 Total Score: {result['total_score']}/100")
    print()
    
    print("📊 DETAILED BREAKDOWN:")
    print(f"Must-Have Skills ({result['must_have_skills']['score']}/40):")
    print(f"  Required: {result['must_have_skills']['required']}")
    print(f"  Found: {result['must_have_skills']['found']}")
    print()
    
    print(f"Nice-to-Have Skills ({result['nice_to_have_skills']['score']}/20):")
    print(f"  Required: {result['nice_to_have_skills']['required']}")
    print(f"  Found: {result['nice_to_have_skills']['found']}")
    print()
    
    print(f"Experience Score: {result['experience_score']}/20")
    print(f"Education Score: {result['education_score']}/10")
    print()
    
    # Validate expected outcome
    if result['total_score'] >= 70:
        print("✅ SUCCESS: Senior AI Engineer gets appropriate high score!")
    elif result['total_score'] >= 50:
        print("⚠️ WARNING: Score is moderate, might need improvement")
    else:
        print("❌ ERROR: Senior AI Engineer getting too low score")
    
    # Test key skills detection
    print("\n🔍 KEY SKILLS DETECTION TEST:")
    key_skills = ["Python", "Machine Learning", "AI", "Deep Learning", "TensorFlow", "PyTorch", "LangChain", "FAISS"]
    for skill in key_skills:
        detected = enhanced_skill_matches(skill, david_cv)
        status = "✅" if detected else "❌"
        print(f"  {status} {skill}: {detected}")

if __name__ == "__main__":
    test_enhanced_evaluation()