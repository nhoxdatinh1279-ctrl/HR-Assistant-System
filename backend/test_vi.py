#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import get_fallback_response

# Test Vietnamese keywords
test_cases = [
    ("Tôi muốn xin nghỉ phép", "vi"),
    ("Chính sách phúc lợi công ty như thế nào?", "vi"),
    ("Hello, what is the leave policy?", "en"),
    ("Xin chào", "vi"),
]

print("Testing get_fallback_response function:")
print("=" * 60)

for msg, lang in test_cases:
    response = get_fallback_response(msg, lang)
    print(f"\n📝 Message: {msg}")
    print(f"🌐 Language: {lang}")
    print(f"💬 Response: {response[:150]}...")
    print("-" * 60)

print("\n✅ All tests completed successfully!")
