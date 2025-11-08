"""
CV Evaluation Demo - Galacy Software AI HR System
Demonstrates the new CV evaluation functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our CV evaluation function
from backend.function_tools import _evaluate_cv_logic
import json

def demo_cv_evaluation():
    print("🎯 Galacy Software AI - CV Evaluation System Demo")
    print("=" * 55)
    print()
    
    # Sample CV for demonstration
    sample_cv = """
    John Smith - Senior Software Engineer
    
    EDUCATION:
    Master of Science in Computer Science, Stanford University (2018)
    Bachelor of Science in Computer Science, MIT (2016)
    
    EXPERIENCE:
    5+ years in software development and AI research
    
    TECHNICAL SKILLS:
    - Programming: Python, JavaScript, Java, C++
    - AI/ML: Machine Learning, Deep Learning, Neural Networks
    - Frameworks: TensorFlow, PyTorch, Keras, scikit-learn
    - NLP: Natural Language Processing, Text Analysis, Sentiment Analysis
    - Tools: LangChain, OpenAI, GPT models, FAISS, Pinecone
    - Cloud: AWS (EC2, S3, Lambda), Google Cloud Platform, Docker, Kubernetes
    - Databases: PostgreSQL, MongoDB, Vector Databases
    
    PROJECTS:
    - Built an AI-powered chatbot using LangChain and OpenAI GPT-4
    - Developed ML models for text classification and sentiment analysis
    - Deployed cloud-native applications on AWS with auto-scaling
    - Led a team of 4 developers on a machine learning project
    - Implemented RAG (Retrieval Augmented Generation) systems
    
    CERTIFICATIONS:
    - AWS Certified Solutions Architect
    - Google Cloud Professional ML Engineer
    
    SOFT SKILLS:
    - Team leadership and collaboration
    - Excellent communication and presentation skills
    - Problem-solving and innovation
    - Agile/Scrum methodology experience
    """
    
    print("📄 Sample CV:")
    print("-" * 40)
    print(sample_cv.strip())
    print()
    
    print("🔍 Evaluation Process:")
    print("-" * 40)
    
    try:
        # Evaluate the CV
        result = _evaluate_cv_logic(sample_cv)
        evaluation = json.loads(result)
        
        print("✅ CV evaluation completed successfully!")
        print()
        
        # Display results
        print("📊 SCORING RESULTS:")
        print("=" * 30)
        print(f"🔧 Technical Skills:     {evaluation['technical_score']:2d}/40")
        print(f"💼 Experience & Projects: {evaluation['experience_score']:2d}/30")  
        print(f"🎓 Education:            {evaluation['education_score']:2d}/15")
        print(f"🤝 Soft Skills:          {evaluation['soft_skills_score']:2d}/15")
        print("-" * 30)
        print(f"🎯 TOTAL SCORE:          {evaluation['total_score']:2d}/100")
        print()
        
        # Recommendation
        print("🏆 RECOMMENDATION:")
        print(f"   {evaluation['recommendation']}")
        print()
        
        # Skills found
        if evaluation.get('skills_found'):
            print("✅ MATCHING SKILLS FOUND:")
            skills = ', '.join(evaluation['skills_found'][:10])  # Show first 10
            print(f"   {skills}")
            if len(evaluation['skills_found']) > 10:
                print(f"   ... and {len(evaluation['skills_found']) - 10} more")
        print()
        
        # Detailed summary
        print("📝 EVALUATION SUMMARY:")
        print("-" * 40)
        print(evaluation['evaluation_summary'])
        print()
        
        # Score interpretation
        print("🎯 SCORE INTERPRETATION:")
        print("-" * 40)
        if evaluation['total_score'] >= 80:
            print("🌟 EXCELLENT (80-100): Top-tier candidate, immediate hire recommendation")
        elif evaluation['total_score'] >= 65:
            print("⭐ STRONG (65-79): Solid candidate, proceed with interviews")
        elif evaluation['total_score'] >= 50:
            print("👍 GOOD (50-64): Potential candidate, consider with additional evaluation")
        else:
            print("⚠️  BELOW THRESHOLD (<50): May need additional training or experience")
        
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        return False
    
    return True

def demonstrate_different_candidates():
    print("\n" + "=" * 60)
    print("🔄 TESTING WITH DIFFERENT CANDIDATE PROFILES")
    print("=" * 60)
    
    candidates = [
        {
            "name": "Entry Level Developer",
            "cv": """
            Alice Johnson - Junior Developer
            Education: Bachelor in Computer Science
            Experience: 1 year internship
            Skills: Python, basic machine learning
            Projects: Simple web application
            """
        },
        {
            "name": "Experienced AI Researcher", 
            "cv": """
            Dr. Robert Chen - AI Research Scientist
            Education: PhD in Artificial Intelligence, Carnegie Mellon
            Experience: 8 years in AI research and development
            Skills: Python, TensorFlow, PyTorch, Deep Learning, NLP, Computer Vision
            Projects: Published 15 papers on machine learning, Led team of 10 researchers
            Certifications: Multiple AI/ML certifications
            Leadership: Team management, mentoring, innovation
            """
        }
    ]
    
    for candidate in candidates:
        print(f"\n🧑‍💼 {candidate['name']}:")
        print("-" * 40)
        
        try:
            result = _evaluate_cv_logic(candidate['cv'])
            evaluation = json.loads(result)
            
            print(f"Technical: {evaluation['technical_score']}/40 | "
                  f"Experience: {evaluation['experience_score']}/30 | "
                  f"Education: {evaluation['education_score']}/15 | "
                  f"Soft Skills: {evaluation['soft_skills_score']}/15")
            print(f"🎯 Total: {evaluation['total_score']}/100 - {evaluation['recommendation']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Starting CV Evaluation Demo...")
    print()
    
    success = demo_cv_evaluation()
    
    if success:
        demonstrate_different_candidates()
        
        print("\n" + "=" * 60)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("💡 The CV evaluation function is now integrated into the HR Assistant system.")
        print("🔧 HR personnel can use it via chat interface or direct API calls.")
        print("📊 All evaluations follow standardized Galacy Software AI criteria.")
    else:
        print("\n❌ Demo failed. Please check the error messages above.")