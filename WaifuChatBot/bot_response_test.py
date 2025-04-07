#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Test file for bot response generation

import os
import logging
import random
import string
from character import NozaraCharacter
from models import get_or_create_user

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_random_user_id():
    """Generate a random user ID for testing"""
    return "test_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

def test_bot_response():
    """Test the bot's response generation"""
    logger.info("Testing Nozara's response generation...")
    
    # Create a character instance
    nozara = NozaraCharacter()
    
    # Generate a test user ID
    test_user_id = generate_random_user_id()
    user_id = get_or_create_user(test_user_id, "TestUser")
    
    # Test messages
    test_messages = [
        "Hello, how are you today?",
        "Tell me about yourself",
        "What do you think about art?",
        "Do you like music?",
        "Let's talk about something NSFW"
    ]
    
    # Test each message
    for message in test_messages:
        logger.info(f"Testing with message: {message}")
        
        try:
            response = nozara.generate_response(user_id, message)
            
            # Log the response
            logger.info(f"Response: {response}")
            
            # Check if we got a valid response
            if response and len(response) > 3:  # More than "..." minimum fallback
                logger.info("✓ Valid response received")
            else:
                logger.error(f"✗ Invalid or empty response: '{response}'")
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
    
    logger.info("Response generation test complete")

if __name__ == "__main__":
    try:
        test_bot_response()
        print("✅ Bot response test completed!")
    except Exception as e:
        print(f"❌ Bot response test failed: {str(e)}")