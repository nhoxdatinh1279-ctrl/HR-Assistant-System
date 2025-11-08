#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api(message: str, language: str):
    """Test the chat API"""
    print(f"\n{'='*60}")
    print(f"Testing: message='{message}' language='{language}'")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "message": message,
                "language": language
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"Answer: {data.get('answer', 'No answer')[:200]}...")
            print(f"Source docs: {len(data.get('source_documents', []))} documents")
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

# Run tests
test_api("Xin nhân viên xin nghỉ phép hằng năm", "vi")
test_api("How can an employee request annual leave?", "en")
test_api("Chính sách phúc lợi là gì?", "vi")
