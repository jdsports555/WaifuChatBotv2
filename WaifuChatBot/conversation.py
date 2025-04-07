#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Conversation handlers for the Telegram bot

import logging
from telegram import ParseMode
from character import NozaraCharacter
from utils import safe_send_message

# Create global instance of Nozara character
nozara = NozaraCharacter()

# Set up logging
logger = logging.getLogger(__name__)

# Define conversation states
CHATTING = 1

def start(update, context):
    """Handler for the /start command"""
    user = update.effective_user
    context.user_data["character"] = NozaraCharacter()  # Create a unique character instance for each user
    char = context.user_data["character"]
    
    # Store user information in context
    context.user_data["user_id"] = user.id
    context.user_data["username"] = user.username
    
    greeting = char.get_greeting()
    logger.info(f"Started conversation with user {user.id}")
    
    update.message.reply_text(
        f"{greeting}",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Send a follow-up message to explain what the bot does
    update.message.reply_text(
        "I'm your gothic companion. We can talk about whatever interests you.\n"
        "If you need help, just type /help anytime.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return CHATTING

def help_command(update, context):
    """Handler for the /help command"""
    if "character" not in context.user_data:
        context.user_data["character"] = NozaraCharacter()
    
    char = context.user_data["character"]
    help_text = char.get_help_message()
    
    update.message.reply_text(
        help_text,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return CHATTING

def cancel_command(update, context):
    """Handler for the /cancel command"""
    if "character" not in context.user_data:
        context.user_data["character"] = NozaraCharacter()
    
    char = context.user_data["character"]
    farewell = char.get_farewell()
    
    update.message.reply_text(
        farewell,
        parse_mode=ParseMode.MARKDOWN
    )
    
    # We don't actually end the conversation, just acknowledge the command
    return CHATTING

def text_message_handler(update, context):
    """Handler for text messages during conversation"""
    user_message = update.message.text
    user = update.effective_user
    
    # Create a new character instance if one doesn't exist
    if "character" not in context.user_data:
        context.user_data["character"] = NozaraCharacter()
    
    char = context.user_data["character"]
    
    logger.info(f"Received message from {user.id}: {user_message}")
    
    # Generate a response from Nozara
    response = char.generate_response(user_message)
    
    # Add to conversation history
    char.add_to_history(user_message, response)
    
    # Send the response
    safe_send_message(update, response)
    
    return CHATTING

def unknown_command(update, context):
    """Handler for unknown commands"""
    if "character" not in context.user_data:
        context.user_data["character"] = NozaraCharacter()
    
    char = context.user_data["character"]
    
    update.message.reply_text(
        f"*raises eyebrow* Not sure what that command is supposed to do.\n\nTry /help if you need guidance.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return CHATTING

def error_handler(update, context):
    """Error handler for the bot"""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Extract user information if possible
    user_id = None
    if update and update.effective_user:
        user_id = update.effective_user.id
    
    # Log detailed error information
    logger.error(f"Error for user {user_id}: {context.error}", exc_info=True)
    
    # Only notify the user if we can
    if update and update.effective_message:
        update.effective_message.reply_text(
            "*sighs* Technical difficulties. Something's not working right.\n"
            "Try again or use /start to reset our conversation.",
            parse_mode=ParseMode.MARKDOWN
        )
