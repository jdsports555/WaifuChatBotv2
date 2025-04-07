import logging
from nozara_character import get_nozara_response, NOZARA_INTRO

logger = logging.getLogger(__name__)

def start_conversation(update, context):
    """
    Handler for the /start command - introduces Nozara to the user.
    """
    user = update.effective_user
    logger.info(f"User {user.id} started a conversation")
    
    update.message.reply_text(
        f"Hello {user.first_name}! {NOZARA_INTRO}"
    )

def handle_message(update, context):
    """
    Handler for regular text messages - processes the message and generates Nozara's response.
    """
    user_message = update.message.text
    user_id = update.effective_user.id
    
    logger.info(f"Received message from user {user_id}: {user_message}")
    
    # Store the message in conversation history (could be expanded in future)
    if 'conversation_history' not in context.user_data:
        context.user_data['conversation_history'] = []
    
    context.user_data['conversation_history'].append({
        'role': 'user',
        'message': user_message
    })
    
    # Generate Nozara's response
    nozara_response = get_nozara_response(user_message)
    
    # Store Nozara's response in conversation history
    context.user_data['conversation_history'].append({
        'role': 'nozara',
        'message': nozara_response
    })
    
    # Keep conversation history limited to last 10 exchanges to avoid memory issues
    if len(context.user_data['conversation_history']) > 20:
        context.user_data['conversation_history'] = context.user_data['conversation_history'][-20:]
    
    # Send Nozara's response
    update.message.reply_text(nozara_response)

def error_handler(update, context):
    """
    Error handler for the bot - logs errors and informs the user.
    """
    logger.error(f"Update {update} caused error {context.error}")
    
    # If an update caused an error, notify the user without breaking character
    if update:
        try:
            update.effective_message.reply_text(
                "*frowns slightly* Something's not working right. "
                "Technical issues. Let's try again in a moment."
            )
        except:
            # If we can't reply to the specific message
            logger.error("Could not send error message to user")
