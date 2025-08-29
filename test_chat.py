#!/usr/bin/env python3
"""
Simple test script to verify chat functionality
Run with: python test_chat.py
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_chat():
    """Test the chat functionality"""
    try:
        # Import after setting up environment
        from backend.app.services import run_chat
        
        print("🧪 Testing chat functionality...")
        print("=" * 50)
        
        # Test question
        question = "ماهي الماده الاولى في نظام الحكم"
        print(f"❓ Question: {question}")
        print("-" * 50)
        
        # Get response
        response = await run_chat(question)
        print(f"✅ Response: {response}")
        print("=" * 50)
        
        if response and not response.startswith("عذراً، حدث خطأ"):
            print("🎉 Chat is working properly!")
        else:
            print("❌ Chat is still having issues")
            
    except Exception as e:
        print(f"❌ Error testing chat: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chat())
