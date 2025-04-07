import os
import logging
import time
import json
import requests
import sys
import fcntl
import atexit
from character import NozaraCharacter
from utils import safe_send_message, clean_text
from models import get_or_create_user, store_message, get_conversation_history

# Set up comprehensive logging 
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Set more verbose logging for modules we care about
requests_logger = logging.getLogger("requests")
requests_logger.setLevel(logging.INFO)
urllib3_logger = logging.getLogger("urllib3")
urllib3_logger.setLevel(logging.INFO)

# Set detailed logging for our AI integration modules
gemini_logger = logging.getLogger("gemini_integration")
gemini_logger.setLevel(logging.DEBUG)
custom_ai_logger = logging.getLogger("custom_ai_integration")
custom_ai_logger.setLevel(logging.DEBUG)
ai_logger = logging.getLogger("ai_integration")
ai_logger.setLevel(logging.DEBUG)
character_logger = logging.getLogger("character")
character_logger.setLevel(logging.DEBUG)

# Create Nozara character
nozara = NozaraCharacter()

# Define Telegram Bot API URL
def get_api_url(token, method):
    return f"https://api.telegram.org/bot{token}/{method}"

# Handle /start command
def handle_start(token, chat_id, user):
    # Get or create user in database
    user_id = get_or_create_user(str(chat_id), user.get("first_name"))
    
    greeting = nozara.get_greeting()
    safe_send_message(token, chat_id, greeting)
    
    # Send a follow-up message to explain what the bot does
    intro_message = "I'm Nozara, your gothic companion. We can talk about whatever interests you.\nIf you need help, just type /help anytime."
    safe_send_message(token, chat_id, intro_message)
    
    # Store the messages in conversation history
    store_message(user_id, greeting, is_from_user=False)
    store_message(user_id, intro_message, is_from_user=False)

# Handle /help command
def handle_help(token, chat_id):
    # Get or create user in database
    user_id = get_or_create_user(str(chat_id))
    
    help_text = nozara.get_help_message()
    safe_send_message(token, chat_id, help_text)
    
    # Store the message in conversation history
    store_message(user_id, help_text, is_from_user=False)

# Handle normal text message
def handle_normal_message(token, chat_id, text, from_user):
    """
    Process a normal text message from a user and generate a response.
    
    This function is designed to ALWAYS send a response to the user, even if errors occur.
    Multiple layers of fallbacks are implemented to ensure a response is sent.
    """
    # Absolute minimum guaranteed response in case of catastrophic failure
    guaranteed_response = "*adjusts choker* I'm thinking..."
    
    # Get or create user in database
    try:
        user_id = get_or_create_user(str(chat_id), from_user.get("first_name"))
        logger.info(f"Processing message from user ID: {user_id}, Telegram ID: {chat_id}")
    except Exception as e:
        logger.error(f"Error getting/creating user: {e}")
        # Create a temporary user ID using just the chat_id as string
        user_id = str(chat_id)
    
    # Store the incoming message in the database
    try:
        store_message(user_id, text, is_from_user=True)
    except Exception as e:
        logger.error(f"Error storing user message: {e}")
        # Continue even if storing fails
    
    # Clean the text for processing
    try:
        clean_message = clean_text(text)
    except Exception as e:
        logger.error(f"Error cleaning text: {e}")
        clean_message = text  # Just use original if cleaning fails
    
    # Log message info for debugging (without logging the actual content for privacy)
    logger.info(f"Processing message from user {chat_id}, length: {len(text)}")
    
    # Extract keywords for topic detection
    try:
        from nlp_processor import extract_keywords, get_topic
        keywords = extract_keywords(clean_message)
        detected_topic = get_topic(clean_message, keywords)
        logger.info(f"Detected topic: {detected_topic}")
    except Exception as e:
        logger.error(f"Error in topic detection: {e}")
        # Default to generic topic
        detected_topic = "default"
        keywords = []
    
    # Generate response with tiered fallback system
    try:
        # This should NEVER fail as it has its own internal fallback system
        response = nozara.generate_response(user_id, text)
        logger.info(f"Generated response length: {len(response)}")
    except Exception as e:
        logger.error(f"CRITICAL ERROR in nozara.generate_response: {e}")
        # Even though the function should never fail, have a backup plan
        response = guaranteed_response
    
    # Store the response in conversation history database
    try:
        store_message(user_id, response, is_from_user=False)
    except Exception as e:
        logger.error(f"Error storing bot response: {e}")
        # Continue even if storing fails
    
    # Send the response - with multiple retry attempts
    max_retries = 3
    retry_count = 0
    success = False
    
    while not success and retry_count < max_retries:
        try:
            safe_send_message(token, chat_id, response)
            success = True
            logger.info(f"Successfully sent response to user {chat_id}")
        except Exception as e:
            retry_count += 1
            logger.error(f"Error sending message (attempt {retry_count}/{max_retries}): {e}")
            time.sleep(1)  # Brief pause before retry
    
    # Last resort if sending failed after all retries
    if not success:
        try:
            logger.error(f"All attempts to send response failed. Trying minimal message.")
            # Try with an absolute minimal response
            requests.get(
                f"https://api.telegram.org/bot{token}/sendMessage",
                params={
                    "chat_id": chat_id,
                    "text": "..."
                }
            )
        except Exception as final_e:
            logger.critical(f"CRITICAL: Failed to send any response to user: {final_e}")
            # Nothing more we can do at this point

# Process incoming update
def process_update(token, update):
    """
    Process a Telegram update by extracting relevant information and routing
    to the appropriate handler. This handles all types of messages.
    """
    # Log the type of update we received
    update_type = next((k for k in ["message", "edited_message", "callback_query"] if k in update), "unknown")
    logger.info(f"Received update of type: {update_type}")
    
    try:
        if "message" in update:
            message = update["message"]
            chat_id = message["chat"]["id"]
            from_user = message["from"]
            
            # Handle different message types - text, sticker, photo, etc.
            if "text" in message:
                text = message["text"]
                
                # Check for commands
                if text.startswith("/start"):
                    handle_start(token, chat_id, from_user)
                elif text.startswith("/help"):
                    handle_help(token, chat_id)
                else:
                    handle_normal_message(token, chat_id, text, from_user)
            
            # For stickers or other non-text content, ask user to send text
            elif any(k in message for k in ["sticker", "photo", "voice", "video", "document"]):
                msg_type = next((k for k in ["sticker", "photo", "voice", "video", "document"] if k in message), "media")
                logger.info(f"Received {msg_type} message from user {chat_id}")
                
                # Get or create the user
                user_id = get_or_create_user(str(chat_id), from_user.get("first_name"))
                
                # Generate a response about the media
                response = f"*examines your {msg_type}* I prefer text conversations. What did you want to talk about?"
                
                # Store the interaction and send response
                store_message(user_id, f"[User sent {msg_type}]", is_from_user=True)
                store_message(user_id, response, is_from_user=False)
                safe_send_message(token, chat_id, response)
            
            # For any other type of content
            else:
                logger.info(f"Received unknown message type from user {chat_id}")
                
                # Get or create the user
                user_id = get_or_create_user(str(chat_id), from_user.get("first_name"))
                
                # Generic response for unhandled message types
                response = "Hmm, I'm not sure how to respond to that. Maybe try sending a text message instead?"
                
                # Store the interaction and send response
                store_message(user_id, "[User sent unrecognized content]", is_from_user=True)
                store_message(user_id, response, is_from_user=False)
                safe_send_message(token, chat_id, response)
                
        # Handle edited messages by treating them as new messages
        elif "edited_message" in update and "text" in update["edited_message"]:
            edited_message = update["edited_message"]
            chat_id = edited_message["chat"]["id"]
            from_user = edited_message["from"]
            text = edited_message["text"]
            
            # Log that this is an edited message
            logger.info(f"User {chat_id} edited a message")
            
            # Process like a normal message but note that it was edited
            handle_normal_message(token, chat_id, f"{text} (edited)", from_user)
            
        # Handle callback queries from inline keyboards (if used in future)
        elif "callback_query" in update:
            callback_query = update["callback_query"]
            chat_id = callback_query["message"]["chat"]["id"]
            from_user = callback_query["from"]
            data = callback_query["data"]
            
            logger.info(f"Received callback query with data '{data}' from user {chat_id}")
            
            # Get or create the user
            user_id = get_or_create_user(str(chat_id), from_user.get("first_name"))
            
            # Simple handling of button presses - can be expanded later
            response = f"You selected: {data}"
            
            # Store the interaction and send response
            store_message(user_id, f"[User selected: {data}]", is_from_user=True)
            store_message(user_id, response, is_from_user=False)
            safe_send_message(token, chat_id, response)
            
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        try:
            # If we have a chat_id, try to notify the user
            # First, try to extract chat_id from the update
            chat_id = None
            
            if 'update' in locals() and update:
                if 'message' in update and 'chat' in update['message']:
                    chat_id = update['message']['chat']['id']
                elif 'edited_message' in update and 'chat' in update['edited_message']:
                    chat_id = update['edited_message']['chat']['id']
                elif 'callback_query' in update and 'message' in update['callback_query']:
                    chat_id = update['callback_query']['message']['chat']['id']
            
            # If we found a chat_id, send the error message
            if chat_id:
                error_message = "I encountered an error processing your message. Please try again."
                safe_send_message(token, chat_id, error_message)
            else:
                logger.error("Could not determine chat_id from update")
        except Exception as notify_error:
            # If we can't even send an error message, just log it
            logger.error(f"Could not send error message to user: {notify_error}")

def clean_webhook_and_updates(token):
    """
    Completely clean up Telegram webhook configuration and pending updates.
    This function is more thorough than a simple deleteWebhook call.
    """
    try:
        # Step 1: Delete the webhook with drop_pending_updates=True
        delete_webhook_url = get_api_url(token, "deleteWebhook")
        delete_response = requests.get(delete_webhook_url, params={"drop_pending_updates": True})
        
        if delete_response.status_code == 200:
            logger.info("Webhook deleted successfully with drop_pending_updates=True")
            return True
        else:
            logger.warning(f"Failed to delete webhook: {delete_response.status_code}")
            
        # Step 2: As a backup, try to flush updates using getUpdates with a large offset
        # This will mark all pending updates as read
        get_updates_url = get_api_url(token, "getUpdates")
        
        # Get the latest update_id first
        response = requests.get(get_updates_url, params={"limit": 1, "timeout": 1})
        
        if response.status_code == 200 and response.json()["result"]:
            latest_update = response.json()["result"][0]
            latest_id = latest_update["update_id"]
            
            # Now mark all updates as read by using offset = latest_id + 1
            requests.get(get_updates_url, params={"offset": latest_id + 1, "timeout": 1})
            logger.info(f"Flushed updates up to update_id {latest_id}")
            return True
        elif response.status_code == 200:
            # No updates to flush
            logger.info("No pending updates found")
            return True
        else:
            logger.warning(f"Failed to get updates for flushing: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error cleaning webhook and updates: {e}")
        return False

def acquire_lock():
    """Try to acquire a lock file to ensure only one instance is running"""
    lock_file = open("bot.lock", "w")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        logger.info("Lock acquired, we are the only instance running")
        # Keep the file open to maintain the lock
        return lock_file
    except IOError:
        logger.error("Another instance is already running. Exiting.")
        sys.exit(1)
        
def release_lock(lock_file):
    """Release the lock file"""
    try:
        fcntl.flock(lock_file, fcntl.LOCK_UN)
        lock_file.close()
        os.unlink("bot.lock")
        logger.info("Lock released")
    except Exception as e:
        logger.error(f"Error releasing lock: {e}")

def main():
    # Get the bot token from environment variables
    token = os.getenv("TELEGRAM_TOKEN")
    
    if not token:
        logger.error("No Telegram token found. Please set the TELEGRAM_TOKEN environment variable.")
        raise ValueError("Telegram token not found")
    
    logger.info("Starting Nozara Bot with memory capabilities...")
    logger.info(f"Bot token available: {token[:5]}...{token[-5:]} (showing only first/last 5 chars for security)")
    
    # Acquire lock to ensure only one instance runs
    lock_file = acquire_lock()
    # Register to release lock on exit
    atexit.register(release_lock, lock_file)
    
    # Check bot info
    try:
        me_url = get_api_url(token, "getMe")
        me_response = requests.get(me_url)
        if me_response.status_code == 200:
            me_data = me_response.json()
            logger.info(f"Bot information: {me_data}")
        else:
            logger.error(f"Failed to get bot info: {me_response.status_code}")
    except Exception as e:
        logger.error(f"Error getting bot info: {e}")
    
    # Thoroughly clean up webhook and pending updates
    clean_webhook_and_updates(token)
    
    # Give some time for Telegram servers to fully process the webhook deletion
    time.sleep(2)
    
    # Set a maximum number of retry attempts for webhook conflicts
    max_webhook_retries = 5
    webhook_retry_count = 0
    
    # Get updates via long polling
    offset = None
    last_activity_time = time.time()
    logger.info("Starting long polling loop...")
    
    while True:
        try:
            # Build the API URL with the offset if we have one
            url = get_api_url(token, "getUpdates")
            params = {"timeout": 30}
            if offset:
                params["offset"] = offset
            
            # Make the API request
            response = requests.get(url, params=params)
            
            # Check if the request was successful
            if response.status_code == 200:
                webhook_retry_count = 0  # Reset the retry counter on success
                updates = response.json()["result"]
                
                # Log polling activity
                logger.info(f"Polling: received {len(updates)} updates")
                
                if updates:
                    # Update the last activity time when we receive updates
                    last_activity_time = time.time()
                    
                    # Process each update
                    for update in updates:
                        logger.info(f"Processing update ID: {update.get('update_id')}")
                        process_update(token, update)
                        offset = update["update_id"] + 1
                else:
                    # No updates received, but connection is working
                    logger.info("Long polling connection active, no new messages")
                        
                # Periodically clean up if we haven't had activity in a while (3 hours)
                # This prevents webhook conflicts when other processes try to set webhooks
                elapsed_time = time.time() - last_activity_time
                if elapsed_time > 10800:  # 3 hours
                    logger.info("No activity for 3 hours, refreshing webhook status")
                    clean_webhook_and_updates(token)
                    last_activity_time = time.time()
                    
            elif response.status_code == 409:
                logger.error("Conflict: Another instance is running or a webhook is set. Attempting to fix...")
                webhook_retry_count += 1
                
                if webhook_retry_count <= max_webhook_retries:
                    # Increase backoff time with each retry
                    time.sleep(5 * webhook_retry_count)
                    # Try to clean up the webhook thoroughly
                    success = clean_webhook_and_updates(token)
                    if success:
                        logger.info(f"Webhook cleanup attempt {webhook_retry_count}/{max_webhook_retries} successful")
                    else:
                        logger.warning(f"Webhook cleanup attempt {webhook_retry_count}/{max_webhook_retries} failed")
                else:
                    # If we hit the maximum retry limit, wait longer and reset the counter
                    logger.warning(f"Reached maximum webhook retry attempts ({max_webhook_retries}), waiting longer...")
                    time.sleep(60)  # Wait a full minute
                    webhook_retry_count = 0
                    
            else:
                logger.error(f"Error getting updates: {response.status_code}")
                time.sleep(5)
                
        except requests.RequestException as e:
            logger.error(f"Network error in main loop: {e}")
            time.sleep(10)  # Wait longer for network issues
            
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
