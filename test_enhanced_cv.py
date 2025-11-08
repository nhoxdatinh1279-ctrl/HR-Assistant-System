#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import base64

# David Tran's CV content
cv_content = """David Tran
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

# Encode CV to base64
cv_base64 = base64.b64encode(cv_content.encode('utf-8')).decode('utf-8')

# Create message in frontend format
message = f"Evaluate my CV for AI/ML Engineer | david_cv.txt | {cv_base64}"

# Test the API
def test_cv_evaluation():
    url = "http://localhost:8000/chat"
    headers = {"Content-Type": "application/json"}
    data = {"message": message}
    
    print("🎯 Testing Enhanced CV Evaluation for AI/ML Engineer")
    print(f"📄 CV Length: {len(cv_content)} characters")
    print(f"🔍 Base64 Length: {len(cv_base64)} characters")
    print(f"💬 Message Preview: {message[:100]}...")
    print("\n" + "="*50)
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! CV Evaluation Response:")
            print(f"📊 Score: {result.get('response', 'No response')}")
            
            # Check if skills were detected
            if "No relevant skills found" in str(result):
                print("❌ ERROR: Still showing 'No relevant skills found'")
            elif any(skill in str(result).lower() for skill in ['python', 'machine learning', 'ai', 'tensorflow']):
                print("✅ SKILLS DETECTED: Enhanced matching working!")
            else:
                print("⚠️ WARNING: Unclear if skills detected")
                
        else:
            print(f"❌ HTTP ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")
        print("Make sure backend is running on http://localhost:8000")

if __name__ == "__main__":
    test_cv_evaluation()