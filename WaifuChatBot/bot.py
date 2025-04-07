import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from nozara_character import get_nozara_response, NOZARA_INTRO
from character import NozaraCharacter

logger = logging.getLogger(__name__)

# Create global character instance
nozara = NozaraCharacter()

def create_bot():
    """
    Create and configure the Telegram bot application.
    Returns the configured bot updater.
    """
    # Get the bot token from environment variables
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    
    if not telegram_token:
        logger.error("No Telegram token found. Please set the TELEGRAM_TOKEN environment variable.")
        raise ValueError("Telegram token not found")
    
    # Create the Updater instance
    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher
    
    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start_conversation))
    dispatcher.add_handler(CommandHandler("help", help_command))
    
    # Add message handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Add error handler
    dispatcher.add_error_handler(error_handler)
    
    return updater

def start_conversation(update, context):
    """Handler for the /start command - introduces Nozara to the user."""
    user = update.effective_user
    greeting = nozara.get_greeting()
    
    update.message.reply_text(f"{greeting}")
    
    # Send a follow-up message to explain what the bot does
    update.message.reply_text(
        "I'm your gothic companion. We can talk about whatever interests you.\n"
        "If you need help, just type /help anytime."
    )

def help_command(update, context):
    """Send help message when the command /help is issued."""
    help_text = (
        "Hey. I'm Nozara, your gothic companion. Here's how we can interact:\n\n"
        "• Send me a message to chat\n"
        "• Use /start to restart our conversation\n"
        "• Use /help to see this message again\n\n"
        "*straightens jacket* Looking forward to our conversations, I suppose."
    )
    update.message.reply_text(help_text)

def handle_message(update, context):
    """Handler for regular text messages - processes the message and generates Nozara's response."""
    user_message = update.message.text
    
    # Generate a response from Nozara
    response = nozara.generate_response(user_message)
    
    # Add to conversation history
    nozara.add_to_history(user_message, response)
    
    # Send the response
    update.message.reply_text(response)

def error_handler(update, context):
    """Error handler for the bot - logs errors and informs the user."""
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
            "Try again or use /start to reset our conversation."
        )
