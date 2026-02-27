#!/usr/bin/env python3
"""
Simple test script to verify chatbot functionality without voice features
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.main import (
    get_weather,
    get_word_definition,
    get_news,
    tell_joke,
    perform_calculation,
    handle_help
)

def test_basic_functions():
    """Test core chatbot functions"""
    print("🧪 Testing Chatbot Core Functions...")
    print("=" * 50)
    
    # Test 1: Weather
    print("\n1. Testing Weather API...")
    try:
        weather = get_weather("London")
        print(f"   ✅ Weather: {weather[:100]}...")
    except Exception as e:
        print(f"   ❌ Weather Error: {e}")
    
    # Test 2: Dictionary
    print("\n2. Testing Dictionary API...")
    try:
        definition = get_word_definition("python")
        print(f"   ✅ Definition: {definition[:100]}...")
    except Exception as e:
        print(f"   ❌ Dictionary Error: {e}")
    
    # Test 3: News
    print("\n3. Testing News API...")
    try:
        news = get_news()
        print(f"   ✅ News: {news[:100]}...")
    except Exception as e:
        print(f"   ❌ News Error: {e}")
    
    # Test 4: Joke
    print("\n4. Testing Joke API...")
    try:
        joke = tell_joke()
        print(f"   ✅ Joke: {joke[:100]}...")
    except Exception as e:
        print(f"   ❌ Joke Error: {e}")
    
    # Test 5: Calculator
    print("\n5. Testing Calculator...")
    try:
        result = perform_calculation("What is 25 + 17?")
        print(f"   ✅ Calculator: {result}")
    except Exception as e:
        print(f"   ❌ Calculator Error: {e}")
    
    # Test 6: Help
    print("\n6. Testing Help System...")
    try:
        help_text = handle_help("help")
        print(f"   ✅ Help: Available commands listed")
    except Exception as e:
        print(f"   ❌ Help Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Core Function Tests Complete!")
    print("📝 Note: Voice features require PyAudio installation")
    print("🌐 Web app is running at http://localhost:8080")

if __name__ == "__main__":
    test_basic_functions()
