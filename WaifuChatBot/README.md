# Nozara Waifu Telegram Bot

A Telegram chatbot featuring Nozara, a 26-year-old gothic waifu character with a unique personality and advanced conversational abilities. Nozara can engage in deep discussions on various topics, remember facts about users, and personalize interactions.

## Features

- Enhanced AI-powered conversations using g4f (GPT4Free) integration
- Gothic character persona with distinct personality traits
- Long-term memory of user information and conversation history
- Support for various conversation topics, including NSFW content
- Smart topic detection and contextual responses
- PostgreSQL database storage for persistent conversation memory
- Automatic provider selection for different conversation topics
- Webhook-based deployment for reliable operation

## Setup

### Prerequisites

- Python 3.7 or higher
- A Telegram account
- A Telegram bot token (get one from [@BotFather](https://t.me/BotFather))
- PostgreSQL database (automatically provided if running on Replit)

### Environment Variables

Create the following environment variables:

- `TELEGRAM_TOKEN`: Your Telegram bot token
- `DATABASE_URL`: PostgreSQL database connection string (handled automatically on Replit)

### Running on Replit

1. Fork this project
2. Add your `TELEGRAM_TOKEN` to the Replit Secrets
3. Click Run to start the bot with the "telegram_bot" workflow

### Deploying to Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use these settings:
   - **Build Command**: `pip install -r render_requirements.txt`
   - **Start Command**: `python main.py`
4. Add the following environment variables:
   - `TELEGRAM_TOKEN`: Your Telegram bot token
   - `DATABASE_URL`: Your PostgreSQL database URL (Render provides a free PostgreSQL database)
   - `GEMINI_API_KEY`: Your Google Gemini API key (if using the Gemini integration)
5. Deploy your service

### Running Locally

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up a PostgreSQL database and set the environment variables:
   ```
   export TELEGRAM_TOKEN=your_token_here
   export DATABASE_URL=postgresql://user:password@localhost:5432/nozara_db
   ```

3. Run the bot:
   ```
   python main.py
   ```

## Usage

Once the bot is running, you can interact with Nozara on Telegram:

1. Search for your bot by its username
2. Start a conversation by sending `/start`
3. Chat with Nozara about any topic!

Nozara will remember information about you across conversations, providing a more personalized experience over time.

## Available Commands

- `/start` - Begin a conversation with Nozara
- `/help` - Show available commands and information

## Personality

Nozara has the following character traits:
- 26 years old with a gothic aesthetic and fashion sense
- Straight-forward personality who speaks directly without censoring herself
- Non-judging and open-minded, willing to discuss any topic including NSFW content
- Sometimes caring, sometimes distant
- Slight dark humor and cynical outlook
- Interests include alternative fashion, dark literature, occult topics, philosophy, art, indie music, and horror movies

## AI Integration

The bot uses multiple free AI providers through the g4f (GPT4Free) library to generate human-like responses without requiring API keys. The integration:

1. Automatically selects appropriate providers based on the conversation topic
2. Provides fallback responses if AI generation fails
3. Constructs detailed prompts that maintain Nozara's character consistency
4. Balances between different providers to avoid rate limits and improve reliability

## Project Structure

- `main.py` - Entry point and webhook handling
- `bot.py` - Bot configuration and setup
- `character.py` - Nozara's personality and response generation
- `conversation_handler.py` - Message handling and conversation flow
- `ai_integration.py` - AI response generation with g4f
- `nlp_processor.py` - Natural language processing and topic detection
- `models.py` - Database models for persistent storage
- `utils.py` - Utility functions

## License

MIT License