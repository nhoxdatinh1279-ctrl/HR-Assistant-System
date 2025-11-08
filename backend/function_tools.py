"""
Function calling tools for the HR Assistant Chatbot.
These tools can be invoked by Azure OpenAI when the user needs to check
specific HR information like leave balance or pay dates.
"""

from langchain_core.tools import tool
from datetime import datetime, timedelta
import json
from company_data import JOB_POSITIONS, SKILL_SCORES, EXPERIENCE_MULTIPLIER, get_position_names

# Mock employee database
EMPLOYEE_DATABASE = {
    "alice": {"name": "Alice Johnson", "leave_balance": 5, "department": "Engineering"},
    "bob": {"name": "Bob Smith", "leave_balance": 10, "department": "Sales"},
    "charlie": {"name": "Charlie Brown", "leave_balance": 3, "department": "HR"},
    "diana": {"name": "Diana Prince", "leave_balance": 8, "department": "Marketing"},
}


@tool("check_leave_balance")
def check_leave_balance(employee_name: str) -> str:
    """
    Check the annual leave balance for an employee.
    
    Args:
        employee_name: The name of the employee (first name only, case-insensitive)
    
    Returns:
        A message with the employee's remaining leave balance
    """
    emp_key = employee_name.lower().strip()
    
    if emp_key in EMPLOYEE_DATABASE:
        employee = EMPLOYEE_DATABASE[emp_key]
        balance = employee["leave_balance"]
        return f"{employee['name']} has {balance} days of annual leave remaining."
    else:
        return f"Employee '{employee_name}' not found in the system. Please check the name and try again."


@tool("check_pay_date")
def check_pay_date() -> str:
    """
    Check the company's payroll schedule.
    
    Returns:
        Information about when salaries are paid
    """
    today = datetime.now()
    day_of_month = 25
    
    if today.day <= day_of_month:
        # Next pay date is this month
        next_pay = today.replace(day=day_of_month)
    else:
        # Next pay date is next month
        if today.month == 12:
            next_pay = today.replace(year=today.year + 1, month=1, day=day_of_month)
        else:
            next_pay = today.replace(month=today.month + 1, day=day_of_month)
    
    days_until = (next_pay - today).days
    return f"Salaries are paid on the 25th of every month. Your next salary will be deposited in {days_until} days ({next_pay.strftime('%B %d, %Y')})."


@tool("check_company_info")
def check_company_info() -> str:
    """
    Get general company information.
    
    Returns:
        Basic company details
    """
    return "Our company has 500+ employees across 3 offices. Founded in 2015, we specialize in AI and cloud solutions. HR Department is available Monday-Friday, 9 AM - 5 PM."


@tool("get_employee_department")
def get_employee_department(employee_name: str) -> str:
    """
    Get the department of an employee.
    
    Args:
        employee_name: The name of the employee (first name only, case-insensitive)
    
    Returns:
        The employee's department
    """
    emp_key = employee_name.lower().strip()
    
    if emp_key in EMPLOYEE_DATABASE:
        employee = EMPLOYEE_DATABASE[emp_key]
        return f"{employee['name']} works in the {employee['department']} department."
    else:
        return f"Employee '{employee_name}' not found in the system."


def _evaluate_cv_logic(cv_text: str) -> str:
    """
    Core CV evaluation logic (without tool decorator).
    
    Args:
        cv_text: The full text content of the candidate's CV/resume
    
    Returns:
        A JSON-formatted evaluation with scores and summary
    """
    import json
    import re
    
    # Convert CV text to lowercase for analysis
    cv_lower = cv_text.lower()
    
    # Company core skills for matching
    core_skills = {
        'python': ['python', 'py', 'django', 'flask', 'fastapi'],
        'machine_learning': ['machine learning', 'ml', 'scikit-learn', 'sklearn', 'tensorflow', 'pytorch', 'keras'],
        'deep_learning': ['deep learning', 'dl', 'neural networks', 'cnn', 'rnn', 'lstm', 'transformer'],
        'nlp': ['nlp', 'natural language processing', 'text analysis', 'sentiment analysis', 'spacy', 'nltk'],
        'langchain': ['langchain', 'llm', 'large language model', 'openai', 'gpt'],
        'rag': ['rag', 'retrieval augmented generation', 'vector database', 'embeddings'],
        'cloud': ['aws', 'gcp', 'azure', 'cloud', 'docker', 'kubernetes', 'deployment'],
        'vector_db': ['faiss', 'pinecone', 'chromadb', 'vector database', 'similarity search']
    }
    
    # 1. Technical Skills Scoring (0-40 points)
    technical_score = 0
    skill_matches = []
    
    for category, keywords in core_skills.items():
        for keyword in keywords:
            if keyword in cv_lower:
                if category == 'python':
                    technical_score += 8
                elif category in ['machine_learning', 'deep_learning']:
                    technical_score += 6
                elif category in ['nlp', 'langchain', 'rag']:
                    technical_score += 5
                elif category in ['cloud', 'vector_db']:
                    technical_score += 4
                skill_matches.append(keyword)
                break  # Only count once per category
    
    # Cap technical score at 40
    technical_score = min(technical_score, 40)
    
    # 2. Experience & Projects Scoring (0-30 points)
    experience_score = 0
    experience_keywords = ['years', 'experience', 'project', 'developed', 'built', 'implemented', 'deployed']
    ai_project_keywords = ['ai', 'machine learning', 'deep learning', 'nlp', 'chatbot', 'model', 'algorithm']
    
    # Check for years of experience
    years_match = re.search(r'(\d+)\s*(?:\+)?\s*years?', cv_lower)
    if years_match:
        years = int(years_match.group(1))
        if years >= 5:
            experience_score += 15
        elif years >= 3:
            experience_score += 12
        elif years >= 1:
            experience_score += 8
        else:
            experience_score += 5
    
    # Check for AI/ML projects
    ai_project_count = sum(1 for keyword in ai_project_keywords if keyword in cv_lower)
    experience_score += min(ai_project_count * 3, 15)
    
    # Cap experience score at 30
    experience_score = min(experience_score, 30)
    
    # 3. Education & Certifications Scoring (0-15 points)
    education_score = 0
    education_keywords = {
        'phd': 15, 'ph.d': 15, 'doctorate': 15,
        'master': 12, 'msc': 12, 'm.sc': 12, 'ms': 12,
        'bachelor': 8, 'bsc': 8, 'b.sc': 8, 'bs': 8,
        'computer science': 5, 'artificial intelligence': 8, 'data science': 6,
        'certification': 3, 'certified': 3, 'aws certified': 5, 'gcp certified': 5
    }
    
    for keyword, score in education_keywords.items():
        if keyword in cv_lower:
            education_score += score
            break  # Take highest scoring education
    
    # Cap education score at 15
    education_score = min(education_score, 15)
    
    # 4. Soft Skills & Fit Scoring (0-15 points)
    soft_skills_score = 0
    soft_skills_keywords = {
        'team': 3, 'collaboration': 3, 'leadership': 4, 'communication': 3,
        'problem solving': 4, 'innovation': 3, 'adaptability': 2, 'agile': 2,
        'scrum': 2, 'mentoring': 3, 'presentation': 2
    }
    
    for keyword, score in soft_skills_keywords.items():
        if keyword in cv_lower:
            soft_skills_score += score
    
    # Cap soft skills score at 15
    soft_skills_score = min(soft_skills_score, 15)
    
    # Calculate total score
    total_score = technical_score + experience_score + education_score + soft_skills_score
    
    # Generate evaluation summary
    summary_parts = []
    
    if technical_score >= 30:
        summary_parts.append("Strong technical alignment with company requirements.")
    elif technical_score >= 20:
        summary_parts.append("Good technical foundation with some relevant skills.")
    else:
        summary_parts.append("Limited technical alignment; recommend training in core AI/ML technologies.")
    
    if experience_score >= 20:
        summary_parts.append("Excellent experience and project portfolio.")
    elif experience_score >= 15:
        summary_parts.append("Solid experience base.")
    else:
        summary_parts.append("Limited relevant experience; may need mentoring.")
    
    if total_score >= 80:
        overall_rating = "Excellent candidate - highly recommended"
    elif total_score >= 65:
        overall_rating = "Strong candidate - recommended"
    elif total_score >= 50:
        overall_rating = "Good candidate - consider with interview"
    else:
        overall_rating = "Below threshold - may need additional evaluation"
    
    summary_parts.append(f"Overall: {overall_rating}.")
    
    # Suggestions for improvement
    suggestions = []
    if technical_score < 25:
        suggestions.append("Develop skills in Python, Machine Learning, and AI frameworks")
    if experience_score < 15:
        suggestions.append("Gain more hands-on project experience in AI/ML")
    if education_score < 8:
        suggestions.append("Consider formal education or certifications in AI/Computer Science")
    if soft_skills_score < 8:
        suggestions.append("Highlight teamwork, communication, and leadership experience")
    
    if suggestions:
        summary_parts.append(f"Improvement areas: {'; '.join(suggestions)}.")
    
    evaluation_summary = " ".join(summary_parts)
    
    # Return structured evaluation
    result = {
        "technical_score": technical_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "soft_skills_score": soft_skills_score,
        "total_score": total_score,
        "evaluation_summary": evaluation_summary,
        "skills_found": list(set(skill_matches)),
        "recommendation": overall_rating
    }
    
    return json.dumps(result, indent=2)


@tool("evaluate_candidate_cv")
def evaluate_candidate_cv(cv_text: str) -> str:
    """
    Evaluate a candidate's CV based on Galacy Software AI company criteria.
    
    Args:
        cv_text: The full text content of the candidate's CV/resume
    
    Returns:
        A JSON-formatted evaluation with scores and summary
    """
    return _evaluate_cv_logic(cv_text)


# List of all available tools


@tool("get_job_positions")
def get_job_positions() -> str:
    """
    Get list of available job positions for CV evaluation.
    Returns all job positions with descriptions.
    
    Returns:
        JSON string with all available job positions
    """
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
    
    return json.dumps(positions, indent=2, ensure_ascii=False)


@tool("evaluate_cv_for_position")
def evaluate_cv_for_position(cv_text: str, position_key: str) -> str:
    """
    Evaluate a candidate's CV for a specific job position.
    
    Args:
        cv_text: The candidate's CV text
        position_key: The job position key (e.g., 'python_developer', 'java_developer', 'ai_ml_engineer')
    
    Returns:
        JSON string with detailed CV evaluation for the position
    """
    if position_key not in JOB_POSITIONS:
        return json.dumps({
            "error": f"Invalid position: {position_key}",
            "available_positions": list(JOB_POSITIONS.keys())
        })
    
    position = JOB_POSITIONS[position_key]
    cv_lower = cv_text.lower()
    
    # Score calculation
    must_have_score = 0
    nice_to_have_score = 0
    total_relevant_skills = 0
    found_skills = []
    missing_must_haves = []
    
    # Check must-have skills
    for skill in position["must_have"]:
        if skill.lower() in cv_lower:
            must_have_score += 15
            found_skills.append(skill)
            total_relevant_skills += 1
        else:
            missing_must_haves.append(skill)
    
    # Check nice-to-have skills
    for skill in position["nice_to_have"]:
        if skill.lower() in cv_lower:
            nice_to_have_score += 5
            found_skills.append(skill)
            total_relevant_skills += 1
    
    # Check for experience level keywords
    experience_score = 0
    if "senior" in cv_lower or "lead" in cv_lower or "principal" in cv_lower:
        experience_score = 20
    elif "mid-level" in cv_lower or "mid level" in cv_lower:
        experience_score = 15
    elif "junior" in cv_lower or "trainee" in cv_lower:
        experience_score = 8
    elif any(f"{i}+ years" in cv_lower or f"{i} years" in cv_lower for i in range(3, 10)):
        experience_score = 15
    elif any(f"{i} year" in cv_lower for i in range(1, 3)):
        experience_score = 10
    else:
        experience_score = 5
    
    # Education score
    education_score = 0
    if "bachelor" in cv_lower or "b.s." in cv_lower or "b.sc" in cv_lower:
        education_score = 15
    if "master" in cv_lower or "m.s." in cv_lower or "m.sc" in cv_lower:
        education_score += 10
    if "phd" in cv_lower or "doctorate" in cv_lower:
        education_score += 10
    if any(cert in cv_lower for cert in ["certification", "certified", "certificate", "aws", "azure", "gcp"]):
        education_score += 5
    education_score = min(education_score, 25)
    
    # Soft skills
    soft_skills_score = 0
    soft_skills = ["communication", "leadership", "teamwork", "problem solving", "critical thinking", 
                   "project management", "agile", "collaborative"]
    for skill in soft_skills:
        if skill in cv_lower:
            soft_skills_score += 3
    soft_skills_score = min(soft_skills_score, 20)
    
    # Calculate total score
    total_score = must_have_score + nice_to_have_score + experience_score + education_score + soft_skills_score
    total_score = min(total_score, 100)
    
    # Determine rating
    if len(missing_must_haves) > 0:
        rating = "Not Suitable"
        reason = f"Missing required skills: {', '.join(missing_must_haves)}"
    elif total_score >= 85:
        rating = "Excellent - Highly Recommended"
        reason = "Strong match with position requirements"
    elif total_score >= 75:
        rating = "Very Good - Recommended"
        reason = "Good match with most requirements"
    elif total_score >= 60:
        rating = "Good - Consider for Interview"
        reason = "Moderate match, may need training in some areas"
    elif total_score >= 50:
        rating = "Acceptable - Potential"
        reason = "Has relevant experience but lacks some skills"
    else:
        rating = "Below Threshold"
        reason = "Limited match with position requirements"
    
    # Build recommendations
    recommendations = []
    if missing_must_haves:
        recommendations.append(f"Missing critical skills: {', '.join(missing_must_haves)}")
    if total_relevant_skills < len(position["must_have"]) + 2:
        recommendations.append("Consider candidates with stronger background in required technologies")
    if experience_score < 10:
        recommendations.append("Limited experience level for this position")
    
    result = {
        "position": position["name"],
        "position_vi": position["name_vi"],
        "candidate_score": total_score,
        "max_score": 100,
        "rating": rating,
        "reason": reason,
        "skill_breakdown": {
            "must_have_skills_score": must_have_score,
            "nice_to_have_skills_score": nice_to_have_score,
            "experience_score": experience_score,
            "education_score": education_score,
            "soft_skills_score": soft_skills_score
        },
        "found_skills": list(set(found_skills)),
        "missing_must_have_skills": missing_must_haves,
        "recommendations": recommendations
    }
    
    return json.dumps(result, indent=2, ensure_ascii=False)


AVAILABLE_TOOLS = [
    check_leave_balance,
    check_pay_date,
    check_company_info,
    get_employee_department,
    evaluate_candidate_cv,
    get_job_positions,
    evaluate_cv_for_position,
]