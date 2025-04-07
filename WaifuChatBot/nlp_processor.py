#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Simple NLP processing for understanding user messages

import re
import logging
from collections import Counter

logger = logging.getLogger(__name__)

# Sentiment analysis keywords
POSITIVE_WORDS = {
    "good", "great", "awesome", "excellent", "happy", "love", "like", "nice", 
    "wonderful", "beautiful", "amazing", "fantastic", "cool", "cute", "kawaii",
    "fun", "enjoy", "sweet", "lovely", "excited", "glad", "thanks", "thank", "pleased",
    "pleasant", "joy", "cheerful", "delighted", "perfect", "yay", "wow"
}

NEGATIVE_WORDS = {
    "bad", "terrible", "horrible", "awful", "sad", "hate", "dislike", "angry",
    "upset", "annoyed", "disappointed", "sorry", "unfortunate", "ugly", "boring",
    "tired", "sick", "hurt", "pain", "cry", "crying", "tears", "depressed",
    "unhappy", "miserable", "stupid", "dumb", "idiot", "sucks", "worst"
}

# Topic detection keywords with expanded categories and NSFW content
TOPIC_KEYWORDS = {
    "anime": {"anime", "manga", "otaku", "cosplay", "waifu", "japan", "japanese", 
              "character", "episode", "watch", "series", "show", "weeb", "hentai", 
              "ecchi", "yuri", "yaoi", "senpai", "kawaii", "moe"},
              
    "food": {"food", "eat", "cooking", "cook", "delicious", "hungry", "meal", "dish", 
             "taste", "recipe", "baking", "kitchen", "yummy", "flavor", "sweet", "sour",
             "spicy", "salty", "bitter", "umami", "restaurant", "cuisine", "snack", "dessert"},
             
    "games": {"game", "gaming", "play", "video game", "gamer", "console", "pc", 
              "playstation", "xbox", "nintendo", "character", "level", "rpg", "mmo",
              "fps", "moba", "strategy", "puzzle", "shooter", "adventure", "quest", 
              "mission", "boss", "raid", "dungeon", "steam", "twitch", "stream"},
              
    "music": {"music", "song", "listen", "singer", "band", "concert", "j-pop", "k-pop", 
              "melody", "rhythm", "dance", "lyrics", "tune", "artist", "album", "playlist",
              "rap", "rock", "pop", "classical", "jazz", "edm", "metal", "indie", "vocal",
              "instrument", "guitar", "piano", "drums", "bass", "violin", "symphony"},
              
    "weather": {"weather", "sunny", "rainy", "cloudy", "hot", "cold", "warm", "snow", 
                "temperature", "forecast", "season", "winter", "summer", "spring", "fall",
                "climate", "humid", "dry", "wind", "storm", "thunder", "lightning", "fog",
                "mist", "drought", "flood", "hurricane", "typhoon", "tornado"},
                
    "art": {"art", "drawing", "paint", "sketch", "artist", "canvas", "gallery", "exhibition",
            "sculpture", "photography", "design", "digital", "illustration", "aesthetic",
            "creative", "masterpiece", "portrait", "landscape", "abstract", "surreal",
            "impressionism", "modern", "contemporary", "traditional"},
            
    "literature": {"book", "novel", "author", "read", "write", "writing", "story", "fiction",
                  "fantasy", "sci-fi", "mystery", "thriller", "horror", "romance", "poetry",
                  "poem", "writer", "character", "plot", "chapter", "publish", "literature",
                  "genre", "series", "trilogy", "saga", "lore", "narrative", "prose"},
                  
    "technology": {"tech", "technology", "computer", "code", "program", "software", "hardware",
                  "internet", "web", "app", "application", "device", "gadget", "smartphone",
                  "laptop", "ai", "artificial intelligence", "robot", "automation", "machine learning",
                  "algorithm", "data", "digital", "innovation", "startup", "coding", "development"},
                  
    "philosophy": {"philosophy", "meaning", "existence", "life", "death", "mind", "soul", "spirit",
                  "consciousness", "reality", "truth", "ethics", "morality", "virtue", "justice",
                  "freedom", "wisdom", "knowledge", "thought", "thinking", "purpose", "metaphysics",
                  "ontology", "epistemology", "existential", "philosophical", "philosopher"},
    
    "romance": {"love", "relationship", "dating", "date", "boyfriend", "girlfriend", "partner",
               "marriage", "wedding", "anniversary", "romantic", "romance", "crush", "intimate",
               "passion", "affection", "devotion", "commitment", "couple", "together", "heart",
               "soulmate", "flirt", "kiss", "hug", "cuddle", "attraction", "chemistry"},
    
    "nsfw_mild": {"nsfw", "adult", "sexy", "intimate", "relationship", "mature", "romance", 
                 "romantic", "dating", "date", "kiss", "kissing", "sensual", "flirt", "crush",
                 "private", "naughty", "tease", "suggestive", "risqué", "seductive", "attractive",
                 "hot", "desire", "passion", "tempt", "provocative", "alluring", "enticing",
                 "flirtatious", "arousing", "teasing", "turned on", "exciting", "underwear",
                 "panties", "lingerie", "sheer", "revealing", "body", "curves", "figure",
                 "touching", "caress", "stroke", "hold", "embrace", "seduce", "whisper",
                 "lips", "mouth", "tongue", "desire", "want", "need", "crave", "yearn",
                 "playful", "mischievous", "cheeky", "adventurous", "exciting", "thrill"},
                 
    "nsfw_explicit": {"sex", "sexual", "nude", "naked", "kinky", "lewd", "erotic", "porn",
                      "pornography", "fetish", "bdsm", "dominance", "submission", "kink", "role-play",
                      "lingerie", "toy", "orgasm", "foreplay", "intercourse", "pleasure",
                      "explicit", "xxx", "adult content", "nsfw content", "18+", "mature content",
                      "fuck", "fucking", "cum", "cumming", "dick", "cock", "penis", "pussy", 
                      "vagina", "clit", "ass", "tits", "boobs", "breasts", "nipples", "anal", "oral",
                      "blowjob", "handjob", "masturbate", "masturbation", "jerk off", "finger",
                      "threesome", "foursome", "orgy", "gangbang", "bondage", "discipline", 
                      "dominant", "submissive", "domination", "spank", "spanking", "whip", "flog",
                      "penetration", "penetrate", "dildo", "vibrator", "toy", "buttplug", "plug",
                      "climax", "squirt", "squirting", "wet", "hard", "horny", "69", "position",
                      "doggy", "missionary", "cowgirl", "reverse", "rough", "hardcore", "taboo",
                      "forbidden", "slutty", "strip", "stripper", "webcam", "cam", "video"}
}

QUESTION_WORDS = {"what", "when", "where", "who", "why", "how", "can", "could", "would", "should", "is", "are", "do", "does"}

def analyze_sentiment(text):
    """
    Simple sentiment analysis based on keyword matching
    Returns 'positive', 'negative', or 'neutral'
    """
    text = text.lower()
    words = set(re.findall(r'\w+', text))
    
    positive_count = len(words.intersection(POSITIVE_WORDS))
    negative_count = len(words.intersection(NEGATIVE_WORDS))
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"

def extract_keywords(text):
    """Extract potentially important keywords from the text"""
    text = text.lower()
    words = re.findall(r'\b[a-z]{3,}\b', text)  # Only words with 3 or more chars
    
    # Remove common stop words
    stop_words = {"the", "and", "for", "that", "this", "with", "you", "your", "can", "are", "have", "just"}
    keywords = [word for word in words if word not in stop_words]
    
    # Count word frequencies
    word_counts = Counter(keywords)
    
    # Return most common keywords, or all if few words
    return [word for word, _ in word_counts.most_common(5)] if len(keywords) > 5 else keywords

def get_topic(text, keywords):
    """
    Determine the likely topic of the text with enhanced NSFW detection
    and more accurate topic classification
    """
    text_lower = text.lower()
    word_set = set(keywords + re.findall(r'\b[a-z]{3,}\b', text_lower))
    
    # Enhanced context-based topic detection
    
    # Check for direct greeting patterns first
    greeting_patterns = [
        r"^hi\b", r"^hello\b", r"^hey\b", r"^greetings", r"^good (morning|afternoon|evening)",
        r"^how are you", r"^what'?s up\b", r"^sup\b", r"^yo\b", r"^howdy\b"
    ]
    
    for pattern in greeting_patterns:
        if re.search(pattern, text_lower):
            logger.info("Detected greeting pattern")
            return "greeting"
    
    # Initialize topic scores with weights for each topic
    topic_scores = {}
    for topic, topic_keywords in TOPIC_KEYWORDS.items():
        # Count how many topic keywords are in the message
        matched_keywords = word_set.intersection(topic_keywords)
        # Basic score from keyword matching
        base_score = len(matched_keywords)
        
        # Apply special weighting for NSFW content
        if topic == "nsfw_explicit":
            # Higher weight for explicit content to ensure it's properly classified
            topic_scores[topic] = base_score * 1.5
        elif topic == "nsfw_mild":
            topic_scores[topic] = base_score * 1.2
        else:
            topic_scores[topic] = base_score
        
        # Enhanced logging for topic detection
        if matched_keywords:
            logger.debug(f"Topic '{topic}' matched keywords: {matched_keywords}")
    
    # Find the topic with the highest score
    if any(topic_scores.values()):
        # Sort topics by score in descending order
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        best_topic = sorted_topics[0]
        
        if best_topic[1] > 0:  # If we found any keyword matches
            # NSFW content detection - if both mild and explicit match, select the appropriate one
            if "nsfw_mild" in [t[0] for t in sorted_topics[:2]] and "nsfw_explicit" in [t[0] for t in sorted_topics[:2]]:
                # If explicit score is significantly higher, use that
                explicit_score = topic_scores.get("nsfw_explicit", 0)
                mild_score = topic_scores.get("nsfw_mild", 0)
                
                if explicit_score > mild_score * 1.3:  # 30% higher threshold
                    best_topic = ("nsfw_explicit", explicit_score)
                else:
                    # Default to milder interpretation if scores are close
                    best_topic = ("nsfw_mild", mild_score)
            
            # Log the detected topic
            logger.info(f"Selected topic '{best_topic[0]}' with score {best_topic[1]}")
            
            # Log detailed topic scores for debugging
            sorted_scores = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            logger.info(f"Top 3 topic scores: {sorted_scores}")
            
            return best_topic[0]
    
    # Check for question patterns before defaulting
    if is_question(text_lower):
        if "you" in text_lower or "your" in text_lower:
            logger.info("Detected personal question")
            return "personal"
    
    logger.info("No clear topic detected, using default")
    return "default"

def is_question(text):
    """Determine if the text is likely a question"""
    text_lower = text.lower()
    
    # Check for question marks
    if "?" in text:
        return True
    
    # Check for question words at the beginning
    words = text_lower.split()
    if words and words[0] in QUESTION_WORDS:
        return True
    
    return False
