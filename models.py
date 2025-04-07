#!/usr/bin/env python
# -*- coding: utf-8 -*-
# In-memory models for the Nozara bot (no database required)

import logging
import datetime
import threading

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# In-memory storage
users = {}  # {telegram_id: {'id': int, 'name': str, 'affection_level': int, ...}}
messages = {}  # {user_id: [{'content': str, 'is_from_user': bool, 'timestamp': datetime}, ...]}
user_facts = {}  # {user_id: {fact_type: fact_value, ...}}

# Counter for generating IDs
id_counter = 0
id_lock = threading.Lock()

def get_next_id():
    """Generate a unique ID for users"""
    global id_counter
    with id_lock:
        id_counter += 1
        return id_counter

def get_or_create_user(telegram_id, name=None):
    """Get existing user or create a new one if not found"""
    try:
        # Check if user exists
        if telegram_id in users:
            # Update last interaction time
            users[telegram_id]['last_interaction'] = datetime.datetime.utcnow()
            if name and not users[telegram_id]['name']:
                users[telegram_id]['name'] = name
            return users[telegram_id]['id']
        
        # Create new user
        user_id = get_next_id()
        users[telegram_id] = {
            'id': user_id,
            'telegram_id': telegram_id,
            'name': name,
            'affection_level': 0,
            'first_interaction': datetime.datetime.utcnow(),
            'last_interaction': datetime.datetime.utcnow()
        }
        
        # Initialize message and fact storage for this user
        messages[user_id] = []
        user_facts[user_id] = {}
        
        return user_id
    except Exception as e:
        logging.error(f"Error in get_or_create_user: {e}")
        return -1  # Special ID to indicate error

def store_message(user_id, content, is_from_user=True):
    """Store a message in memory"""
    try:
        # Skip if user_id is invalid
        if user_id == -1:
            logging.warning("Skipping message storage due to invalid user_id")
            return
        
        # Create message entry
        message = {
            'content': content,
            'is_from_user': is_from_user,
            'timestamp': datetime.datetime.utcnow()
        }
        
        # Initialize messages list if it doesn't exist
        if user_id not in messages:
            messages[user_id] = []
        
        # Add message to history
        messages[user_id].append(message)
        
        # Trim history if it gets too long (keep last 100 messages)
        if len(messages[user_id]) > 100:
            messages[user_id] = messages[user_id][-100:]
    except Exception as e:
        logging.error(f"Error in store_message: {e}")

def get_conversation_history(user_id, limit=10):
    """Get recent conversation history for a user"""
    try:
        # Return empty history if user_id is invalid
        if user_id == -1 or user_id not in messages:
            logging.warning("Returning empty history due to invalid user_id")
            return []
        
        # Get the most recent messages
        history = messages[user_id][-limit:]
        
        return history
    except Exception as e:
        logging.error(f"Error in get_conversation_history: {e}")
        return []  # Return empty list on error

def store_user_fact(user_id, fact_type, fact_value):
    """Store a learned fact about a user"""
    try:
        # Skip if user_id is invalid
        if user_id == -1:
            logging.warning("Skipping fact storage due to invalid user_id")
            return
        
        # Initialize user facts dict if it doesn't exist
        if user_id not in user_facts:
            user_facts[user_id] = {}
        
        # Store the fact
        user_facts[user_id][fact_type] = fact_value
    except Exception as e:
        logging.error(f"Error in store_user_fact: {e}")

def get_user_facts(user_id):
    """Get all known facts about a user"""
    try:
        # Return empty facts if user_id is invalid
        if user_id == -1 or user_id not in user_facts:
            logging.warning("Returning empty facts due to invalid user_id")
            return {}
        
        return user_facts[user_id]
    except Exception as e:
        logging.error(f"Error in get_user_facts: {e}")
        return {}  # Return empty dict on error

def update_affection_level(user_id, amount=1):
    """Update the affection level for a user"""
    try:
        # Skip if user_id is invalid
        if user_id == -1:
            logging.warning("Skipping affection update due to invalid user_id")
            return
        
        # Find the user in our in-memory storage
        telegram_id = None
        for tid, user_data in users.items():
            if user_data['id'] == user_id:
                telegram_id = tid
                break
        
        if telegram_id:
            # Update affection level, ensuring it doesn't exceed 100
            current = users[telegram_id]['affection_level']
            users[telegram_id]['affection_level'] = min(100, current + amount)
    except Exception as e:
        logging.error(f"Error in update_affection_level: {e}")