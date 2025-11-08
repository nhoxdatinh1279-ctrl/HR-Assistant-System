#!/usr/bin/env python
"""Test script for CV evaluation with multiple positions"""

import requests
import base64
import json

# Read the test CV file
with open('test_cv.txt', 'r') as f:
    cv_content = f.read()

# Encode to base64
cv_base64 = base64.b64encode(cv_content.encode()).decode()

# Test 1: Python Developer
print("\n" + "=" * 70)
print("TEST 1: PYTHON DEVELOPER EVALUATION")
print("=" * 70)

message1 = f'Evaluate my CV for Python Developer position. CV: {cv_base64}'
response1 = requests.post('http://localhost:8000/api/chat', 
    json={
        'message': message1,
        'session_id': 'test_python',
        'language': 'en'
    })

result1 = response1.json()
print(result1['answer'][:1500])

# Test 2: Java Developer with same CV
print("\n" + "=" * 70)
print("TEST 2: JAVA DEVELOPER EVALUATION (SAME CV)")
print("=" * 70)

message2 = f'Evaluate my CV for Java Developer position. CV: {cv_base64}'
response2 = requests.post('http://localhost:8000/api/chat',
    json={
        'message': message2,
        'session_id': 'test_java',
        'language': 'en'
    })

result2 = response2.json()
print(result2['answer'][:1500])

# Test 3: DevOps Engineer with same CV
print("\n" + "=" * 70)
print("TEST 3: DEVOPS ENGINEER EVALUATION (SAME CV)")
print("=" * 70)

message3 = f'Evaluate my CV for DevOps Engineer position. CV: {cv_base64}'
response3 = requests.post('http://localhost:8000/api/chat',
    json={
        'message': message3,
        'session_id': 'test_devops',
        'language': 'en'
    })

result3 = response3.json()
print(result3['answer'][:1500])

print("\n" + "=" * 70)
print("✅ COMPARISON TEST COMPLETE")
print("=" * 70)
print("\n📊 Score Comparison:")
print("- If scores are DIFFERENT for each position → Position selection working ✅")
print("- If scores are IDENTICAL for each position → Position selection broken ❌")
print("\n📋 Position Confirmation:")
print("- Check if each response mentions correct position name")
print("- Should see 'Python Developer', 'Java Developer', 'DevOps Engineer' respectively")
