#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Test file for Gemini API

import os
import logging
import requests
import json
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gemini_api():
    """Test the Gemini API connection and response generation"""
    logger.info("Testing Gemini API...")
    
    # Get API key from environment
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment variables")
        return False
        
    # The correct endpoint for Gemini 1.5 Pro
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
    
    # Safety settings to allow all content
    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE"
        }
    ]
    
    # Test with a simple prompt
    prompt = "You are Nozara, a 26-year-old gothic woman. Respond to the user's greeting. User says: 'Hello, how are you today?'"
    
    try:
        logger.info("Sending request to Gemini API...")
        start_time = time.time()
        
        # Call the Gemini API
        response = requests.post(
            f"{api_url}?key={api_key}",
            json={
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }
                ],
                "safetySettings": safety_settings,
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 100,
                }
            }
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"Request completed in {elapsed_time:.2f} seconds")
        
        # Check if the request was successful
        if response.status_code != 200:
            logger.error(f"Gemini API request failed with status code {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
        
        # Parse the response
        response_data = response.json()
        logger.info(f"Full response: {json.dumps(response_data, indent=2)}")
        
        # Extract the generated text
        if ('candidates' in response_data and 
            len(response_data['candidates']) > 0 and 
            'content' in response_data['candidates'][0] and
            'parts' in response_data['candidates'][0]['content'] and
            len(response_data['candidates'][0]['content']['parts']) > 0):
            
            generated_text = response_data['candidates'][0]['content']['parts'][0]['text']
            logger.info(f"Generated response: {generated_text}")
            return True
        else:
            logger.error(f"Unexpected response structure from Gemini API")
            return False
            
    except Exception as e:
        logger.error(f"Error testing Gemini API: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    if success:
        print("✅ Gemini API test successful!")
    else:
        print("❌ Gemini API test failed!")