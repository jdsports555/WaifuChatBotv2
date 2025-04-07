#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Utility functions for the bot

import re
import logging
import time
import requests
from config import MAX_MESSAGE_LENGTH

logger = logging.getLogger(__name__)

def clean_text(text):
    """Clean and normalize user input text"""
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove special characters except basic punctuation
    text = re.sub(r'[^\w\s.,!?\'"-]', '', text)
    
    return text

def safe_send_message(token, chat_id, text):
    """
    Safely send a message through Telegram, handling errors and message length limits
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        if len(text) <= MAX_MESSAGE_LENGTH:
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=payload)
            return response.json()
        else:
            # Split the message if it's too long
            parts = [text[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(text), MAX_MESSAGE_LENGTH)]
            responses = []
            for part in parts:
                payload = {
                    "chat_id": chat_id,
                    "text": part,
                    "parse_mode": "Markdown"
                }
                response = requests.post(url, json=payload)
                responses.append(response.json())
                # Small delay to prevent rate limiting
                time.sleep(0.5)
            return responses
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        # Try to send without markdown as fallback
        try:
            payload = {
                "chat_id": chat_id,
                "text": f"I had trouble sending my message. Here it is without formatting:\n\n{text}"
            }
            response = requests.post(url, json=payload)
            return response.json()
        except Exception as e2:
            logger.error(f"Failed to send fallback message: {e2}")
            return None
