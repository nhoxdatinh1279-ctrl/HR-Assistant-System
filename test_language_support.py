import requests
import json

# Test Vietnamese language support
def test_vietnamese_support():
    print("🇻🇳 Testing Vietnamese Language Support")
    print("=" * 50)
    
    # Test data
    tests = [
        {
            "message": "Tôi có bao nhiêu ngày nghỉ phép còn lại?",
            "language": "vi",
            "description": "Vietnamese leave balance question"
        },
        {
            "message": "Chính sách làm việc từ xa như thế nào?", 
            "language": "vi",
            "description": "Vietnamese remote work policy"
        },
        {
            "message": "How many leave days do I have left?",
            "language": "en", 
            "description": "English leave balance question"
        }
    ]
    
    api_url = "http://localhost:8000/api/chat"
    
    for i, test in enumerate(tests, 1):
        print(f"\n🔍 Test {i}: {test['description']}")
        print(f"Language: {test['language'].upper()}")
        print(f"Question: {test['message']}")
        print("-" * 30)
        
        try:
            response = requests.post(
                api_url,
                json={
                    "message": test["message"],
                    "language": test["language"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Response received:")
                print(f"Answer: {data['answer']}")
                
                if data.get('source_documents'):
                    print(f"Sources: {len(data['source_documents'])} documents")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print()

if __name__ == "__main__":
    test_vietnamese_support()