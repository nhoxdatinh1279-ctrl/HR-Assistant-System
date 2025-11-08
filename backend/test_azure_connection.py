#!/usr/bin/env python
"""Test Azure OpenAI connection"""

import os
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI

# Load environment variables
load_dotenv()

print("=" * 60)
print("Testing Azure OpenAI Connection")
print("=" * 60)

# Get credentials
embedding_api_key = os.getenv("AZURE_OPENAI_EMBEDDING_API_KEY")
embedding_endpoint = os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT")
embedding_model = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

llm_api_key = os.getenv("AZURE_OPENAI_LLM_API_KEY")
llm_endpoint = os.getenv("AZURE_OPENAI_LLM_ENDPOINT")
llm_model = os.getenv("AZURE_OPENAI_LLM_DEPLOYMENT")

print("\nEmbedding Configuration:")
print(f"  API Key: {embedding_api_key[:10]}..." if embedding_api_key else "  API Key: NOT SET")
print(f"  Endpoint: {embedding_endpoint}")
print(f"  Deployment: {embedding_model}")

print("\nLLM Configuration:")
print(f"  API Key: {llm_api_key[:10]}..." if llm_api_key else "  API Key: NOT SET")
print(f"  Endpoint: {llm_endpoint}")
print(f"  Deployment: {llm_model}")

print("\n" + "=" * 60)
print("Testing Embeddings Connection...")
print("=" * 60)

try:
    embeddings = AzureOpenAIEmbeddings(
        model=embedding_model,
        api_version="2023-05-15",
        azure_endpoint=embedding_endpoint,
        api_key=embedding_api_key,
    )
    print("✓ Embeddings initialized successfully!")
    
    # Test embedding
    test_text = "This is a test"
    result = embeddings.embed_query(test_text)
    print(f"✓ Test embedding successful! Dimension: {len(result)}")
except Exception as e:
    print(f"✗ Embeddings connection failed!")
    print(f"  Error: {str(e)}")

print("\n" + "=" * 60)
print("Testing LLM Connection...")
print("=" * 60)

try:
    llm = AzureChatOpenAI(
        model=llm_model,
        temperature=0.7,
        api_version="2023-05-15",
        azure_endpoint=llm_endpoint,
        api_key=llm_api_key,
    )
    print("✓ LLM initialized successfully!")
    
    # Test LLM
    from langchain_core.messages import HumanMessage
    message = HumanMessage(content="Hello, how are you?")
    response = llm.invoke([message])
    print(f"✓ Test LLM call successful!")
    print(f"  Response: {response.content[:100]}...")
except Exception as e:
    print(f"✗ LLM connection failed!")
    print(f"  Error: {str(e)}")

print("\n" + "=" * 60)
print("Connection Test Complete")
print("=" * 60)
