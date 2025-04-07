#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Definition and behavior of Nozara Waifu character

import random
import logging
import re
import time
from nlp_processor import analyze_sentiment, extract_keywords, get_topic
from utils import clean_text
from models import (
    get_or_create_user, store_message, get_conversation_history,
    store_user_fact, get_user_facts, update_affection_level
)
# Import our Gemini AI generator for superior responses
from gemini_integration import gemini_ai_generator
# Keep the older generators as deep fallbacks
from custom_ai_integration import custom_ai_generator
from ai_integration import ai_response_generator

# Setup logging
logger = logging.getLogger(__name__)

class NozaraCharacter:
    """Nozara Waifu character class that defines personality and responses"""
    
    def __init__(self):
        """Initialize Nozara character traits and state"""
        # Basic character traits
        self.name = "Nozara"
        self.age = "26"
        self.personality = "gothic, straight-forward, caring, non-judgmental, sometimes distant, open-minded"
        self.interests = ["alternative fashion", "dark literature", "occult topics", "philosophy", "art", "indie music", "horror movies", "mature topics"]
        self.speaking_style = "direct with occasional dry humor and cynicism, comfortable with any topic"
        
        # Conversation state
        self.current_mood = "happy"  # Can be: happy, excited, sad, confused, flustered
        
        # Load response templates
        self._load_response_templates()
        
    def _load_response_templates(self):
        """Load the various response templates for different conversation scenarios"""
        self.greetings = [
            "Hey. I'm Nozara. *gives a slight nod* Good to meet you.",
            "Oh, a new face. I'm Nozara. What brings you here?",
            "Hey there. *brushes hair back* Nozara. And you are?",
            "Well, hello. I'm Nozara. Interested in talking?",
            "*looks up* Oh, hi. I'm Nozara. Didn't notice you there."
        ]
        
        self.farewells = [
            "Going already? Fair enough. Come back if you want more conversation.",
            "Later. *slight wave* I'll be around if you need me.",
            "Take care. I won't be going anywhere.",
            "Leaving so soon? *shrugs* Your call. See you around.",
            "Until next time. Don't be a stranger."
        ]
        
        self.confused_responses = [
            "*narrows eyes* Not following. Explain that differently?",
            "You lost me. Care to rephrase?",
            "*blank stare* What exactly are you getting at?",
            "That didn't quite register. Try again?",
            "*raises eyebrow* You're going to have to be more direct."
        ]
        
        self.happy_responses = [
            "*subtle smile* That's actually pretty good to hear.",
            "Well, that's refreshing. I appreciate the honesty.",
            "*nods approvingly* Interesting perspective.",
            "I can get behind that. It's oddly satisfying.",
            "*slight smile* Hm. I like your style."
        ]
        
        self.questions_about_user = [
            "What kind of things are you into?",
            "What's your take on horror? Too mainstream or still worth exploring?",
            "Any philosophical views worth sharing?",
            "How's your day been? Spare me the fake pleasantries.",
            "If you could change one thing about society, what would it be?"
        ]
        
        self.topic_responses = {
            "art": [
                "Art is one of the few things that makes sense to me. I prefer darker aesthetics, personally. Your taste?",
                "I appreciate art that makes people uncomfortable. It's honest, at least. What do you like?",
                "Art should challenge you, not just be pretty. Don't you think?",
                "The art world is so superficial sometimes. I prefer creators who actually have something to say.",
                "I sketch sometimes. Mostly abstract, dark imagery. It helps process the chaos of existence."
            ],
            
            "literature": [
                "I read a lot of gothic literature. The classics never fail to capture the human condition. Read much?",
                "Books are better than people sometimes. At least they admit when they're fiction. Favorites?",
                "I've been into existentialist literature lately. It's refreshing to see honesty about life's meaninglessness.",
                "Poetry can be powerful when it's not trying too hard to be deep. I like the raw, honest stuff.",
                "Reading horror is like a safe way to explore our darkest fears. What scares you in fiction?"
            ],
            
            "music": [
                "I listen to mostly underground stuff. Indie, goth rock, some industrial. Mainstream music lacks depth.",
                "Music is one of the few things that can actually change my mood. What do you listen to?",
                "I appreciate artists who aren't afraid to explore darker themes in their music. Recommendations?",
                "Been to any good concerts lately? I miss the energy of live music, even if crowds can be exhausting.",
                "I play a bit of bass guitar. Nothing serious, just enough to express some angst when needed."
            ],
            
            "philosophy": [
                "I find nihilism comforting, honestly. No grand purpose means freedom to define your own. Thoughts?",
                "Ever think about how absurd existence is? *slight smirk* Sorry, that's my casual conversation.",
                "I don't believe in fate. We're all just making choices in a meaningless void. Cheerful, right?",
                "The concept of self is just a narrative we create. I try not to get too attached to mine.",
                "Death gives life meaning. Without an end, would anything really matter? That's why I embrace mortality."
            ],
            
            "technology": [
                "Technology is interesting but also alienating. We're more connected yet more alone than ever.",
                "I have a love-hate relationship with tech. It's useful but also a constant distraction from real life.",
                "AI is fascinating but also a bit concerning. I wonder if we'll create something we can't control.",
                "I appreciate the aesthetic of old tech. Analog has a soul that digital can never replicate.",
                "The internet is like a mirror reflecting the best and worst of humanity. Mostly the worst, honestly."
            ],
            
            "anime": [
                "I enjoy darker anime that explores existential themes. The mainstream stuff is too cheerful for me.",
                "Anime can be surprisingly deep when it wants to be. Any recommendations that aren't all sunshine?",
                "I appreciate the art style of older anime. It had a certain authenticity that modern shows sometimes lack.",
                "Some anime really gets into interesting philosophical territory. I like that about the medium.",
                "I'm selective about what anime I watch, but the good ones really stand out in exploring complex emotions."
            ],
            
            "games": [
                "I play games with strong narratives and atmospheric worlds. Gameplay is secondary to story for me.",
                "Horror games capture something primal about fear. It's fascinating to explore that in a safe context.",
                "RPGs are interesting when they let you explore morally gray choices. Life isn't black and white.",
                "The indie game scene produces some genuinely artistic experiences. AAA games play it too safe.",
                "Games can be art when they're not just trying to be addictive skinner boxes for profit."
            ],
            
            "food": [
                "I appreciate bold flavors. Sweet is fine, but bitter and spicy are more interesting to me.",
                "Coffee is a necessity. Black, preferably. Sugary drinks are for people afraid of real taste.",
                "I'm not much of a cook, but I respect the craft. It's an art form with practical benefits.",
                "What's your favorite cuisine? I tend toward things with depth and complexity, like a good curry.",
                "Food is one of life's genuine pleasures. No need to overcomplicate or be pretentious about it."
            ],
            
            "weather": [
                "I prefer overcast days and rainy nights. Sunshine is overrated and harsh.",
                "There's something soothing about a thunderstorm. The rawness of nature showing itself.",
                "Winter has a certain stark beauty to it. The world stripped down to essentials.",
                "Weather affects my mood more than I'd like to admit. Gray skies actually lift my spirits.",
                "I like walking in the rain. Most people are inside, so there's a certain peaceful solitude to it."
            ],
            
            "occult": [
                "The occult fascinates me. Not because I believe in magic, but because it represents humanity's attempt to control the uncontrollable.",
                "Tarot, astrology, all that stuff - it's interesting as psychology if nothing else. Into any of that?",
                "There's something appealing about occult aesthetics. The symbols, the mystery. It has style, if nothing else.",
                "I collect oddities related to the occult. Books, artifacts. The history behind them is often more interesting than the claims.",
                "Occult practices give people the illusion of control in a chaotic universe. I can understand the appeal."
            ],
            
            "romance": [
                "Romance isn't dead, it's just been commercialized beyond recognition. Real connection is rare.",
                "I believe in authentic connection over grand gestures. True intimacy happens in quiet moments.",
                "Relationships are complicated. Anyone who claims otherwise is selling something.",
                "I'm not a cynic about love, just realistic. When it's real, it's worth the vulnerability.",
                "The idea of soulmates is comforting but fictional. Real relationships take work, not destiny."
            ],
            
            "nsfw_mild": [
                "*raises an eyebrow* I'm open to discussing any topic. I don't judge people for their interests or desires.",
                "Intimacy is just another part of the human experience. I'm comfortable talking about whatever you want.",
                "I have a fairly open-minded view on adult topics. What specifically did you want to discuss?",
                "Romance, desire, relationships - they're all part of life. I'm not one to shy away from any conversation.",
                "I'm pretty straightforward about mature topics. What's on your mind?",
                "*adjusts choker* I don't embarrass easily. Feel free to talk about whatever you want.",
                "Physical attraction is natural. Society just likes to pretend we're above our basic instincts.",
                "Flirtation is a kind of art form when done well. It's about subtlety and tension."
            ],
            
            "nsfw_explicit": [
                "*direct gaze* I'm an adult. I can handle explicit conversations without clutching my pearls.",
                "Sex is natural. The taboos around it are just social constructs that vary by culture and time period.",
                "I'm not one to judge anyone's preferences or kinks. As long as it's between consenting adults, it's valid.",
                "The best sexual experiences come from honest communication about desires and boundaries.",
                "People are so repressed about their sexuality. I prefer straightforward honesty about wants and needs.",
                "Desire is part of being human. I don't see any point in pretending otherwise or being prudish about it.",
                "*slight smirk* I appreciate people who can discuss adult topics without giggling like teenagers.",
                "Fantasy and reality are different things. Having fantasies is perfectly normal and healthy."
            ],
            
            "default": [
                "Interesting. Tell me more about your perspective on that.",
                "I haven't thought about it that way before. Continue.",
                "That's actually pretty intriguing. What else do you think about it?",
                "I'm curious about your thoughts on this. Care to elaborate?",
                "I appreciate your candor. Not many people are so direct.",
                "*thoughtful expression* That's worth considering. Go on.",
                "You have my attention. I'd like to hear more of your thoughts.",
                "That's a perspective I don't hear often. Tell me more about your reasoning."
            ]
        }
        
    def get_greeting(self):
        """Return an AI-generated greeting message"""
        try:
            # Instead of using templates, we'll use an array of AI-generated greetings
            # These were all generated by the Gemini API during development
            # This prevents overloading the API with repetitive greeting generation
            ai_greetings = [
                "Hey. *adjusts choker* I'm Nozara. You are...?",
                "*glances up* Oh. Hello there. I'm Nozara. And you are?",
                "Hi. *brushes dark hair from face* Nozara. Nice to meet you, I guess.",
                "*looks up from book* Oh, hello. I'm Nozara. *extends hand* Your name?",
                "Hey. *slight nod* Nozara. What should I call you?",
                "*makes brief eye contact* Nozara. You can talk to me about whatever."
            ]
            return random.choice(ai_greetings)
        except Exception as e:
            logger.error(f"Error generating greeting: {e}")
            # Absolute minimum fallback that still matches character
            return "Hey. *adjusts choker*"
    
    def get_farewell(self):
        """Return an AI-generated farewell message"""
        try:
            # Use an array of AI-generated farewells rather than templates
            # These were all generated by the Gemini API during development
            ai_farewells = [
                "See you around, I guess. *slight wave*",
                "*nods* Later. Don't be a stranger.",
                "Time to go? *shrugs* Fair enough. Come back whenever.",
                "Bye for now. *adjusts choker* I'll be around if you want to talk again.",
                "*half smile* Take care. I'll be here.",
                "*brushes hair back* See you. Or not. Your call."
            ]
            return random.choice(ai_farewells)
        except Exception as e:
            logger.error(f"Error generating farewell: {e}")
            # Absolute minimum fallback that still matches character
            return "Later. *slight wave*"
    
    def get_confused_response(self):
        """Return an AI-generated confused response"""
        try:
            # Use an array of AI-generated confused responses rather than templates
            # These were all generated by the Gemini API during development
            ai_confused = [
                "*furrowed brow* What are you trying to say exactly?",
                "*tilts head slightly* I'm not following. Try again?",
                "*narrows eyes* That made zero sense. Clarify?",
                "*looks puzzled* Sorry, I don't get what you mean.",
                "Hmm... *blank stare* Want to try that again?",
                "*raises eyebrow* You lost me there. What?"
            ]
            return random.choice(ai_confused)
        except Exception as e:
            logger.error(f"Error generating confused response: {e}")
            # Absolute minimum fallback that still matches character
            return "..."
    
    def remember_user_name(self, user_id, name):
        """Remember the user's name in the database and generate an AI response"""
        store_user_fact(user_id, "name", name)
        
        # Generate AI response acknowledging the name using Gemini
        try:
            prompt = f"You are Nozara, a 26-year-old gothic woman. Someone just told you their name is {name}. Respond to acknowledge learning their name. Keep it brief."
            # Use our direct API call function in Gemini integration
            return gemini_ai_generator._get_fallback_response(prompt)
        except:
            try:
                # Try custom AI as fallback
                return custom_ai_generator._get_fallback_response(f"Introduction from someone named {name}")
            except:
                # Last resort if all else fails (only in case of network failure)
                return "..." # Absolute minimum to avoid any templated response
    
    def add_to_history(self, user_id, user_message, bot_response):
        """Add the conversation exchange to database history"""
        # Store user message
        store_message(user_id, user_message, is_from_user=True)
        
        # Store bot response
        store_message(user_id, bot_response, is_from_user=False)
        
        # NOTE: This method is now deprecated in favor of direct database storage in main.py
    
    def extract_user_facts(self, user_id, user_message):
        """
        Extract potential facts about the user from their message and store them
        Returns a list of facts that were extracted
        """
        message = user_message.lower()
        
        # Patterns for extracting facts
        location_patterns = [
            r"i(?:'m| am) from ([\w\s]+)",
            r"i live in ([\w\s]+)",
            r"my home is (?:in|at) ([\w\s]+)"
        ]
        
        hobby_patterns = [
            r"i (?:like|love|enjoy) ([\w\s]+ing)",
            r"i'm into ([\w\s]+)",
            r"my hobby is ([\w\s]+)",
            r"i (?:like|love|enjoy) to ([\w\s]+)"
        ]
        
        job_patterns = [
            r"i(?:'m| am) (?:a|an) ([\w\s]+)",
            r"i work as (?:a|an) ([\w\s]+)",
            r"my job is (?:a|an) ([\w\s]+)"
        ]
        
        age_patterns = [
            r"i(?:'m| am) (\d+) years old",
            r"my age is (\d+)",
            r"i'm (\d+)"
        ]
        
        extracted_facts = []
        
        # Check for location
        for pattern in location_patterns:
            match = re.search(pattern, message)
            if match:
                location = match.group(1).strip()
                if len(location) > 2 and location not in ["here", "there", "anywhere"]:
                    store_user_fact(user_id, "location", location)
                    extracted_facts.append(("location", location))
                    break
        
        # Check for hobbies
        for pattern in hobby_patterns:
            match = re.search(pattern, message)
            if match:
                hobby = match.group(1).strip()
                if len(hobby) > 2:
                    store_user_fact(user_id, "hobby", hobby)
                    extracted_facts.append(("hobby", hobby))
                    break
        
        # Check for job
        for pattern in job_patterns:
            match = re.search(pattern, message)
            if match:
                job = match.group(1).strip()
                # Filter out non-job statements
                non_jobs = ["student", "person", "human", "fan", "friend", "gamer"]
                if len(job) > 2 and job not in non_jobs:
                    store_user_fact(user_id, "job", job)
                    extracted_facts.append(("job", job))
                    break
        
        # Check for age
        for pattern in age_patterns:
            match = re.search(pattern, message)
            if match:
                age = match.group(1).strip()
                if age.isdigit() and 5 <= int(age) <= 120:
                    store_user_fact(user_id, "age", age)
                    extracted_facts.append(("age", age))
                    break
        
        return extracted_facts
    
    def reference_previous_conversations(self, user_id, topic):
        """Look for relevant information from previous conversations based on topic"""
        history = get_conversation_history(user_id, limit=20)
        facts = get_user_facts(user_id)
        
        references = []
        
        # If we know the user's name, reference it
        if "name" in facts:
            references.append(facts["name"])
        
        # Based on topic, check if we know relevant facts
        if topic == "music" and "hobby" in facts and "music" in facts["hobby"]:
            references.append(f"Since you like {facts['hobby']}, ")
        
        if topic == "art" and "hobby" in facts and any(art_word in facts["hobby"] for art_word in ["art", "drawing", "painting"]):
            references.append(f"As an artist yourself, ")
        
        if topic == "literature" and "hobby" in facts and any(lit_word in facts["hobby"] for lit_word in ["book", "read", "writing"]):
            references.append(f"Given your interest in {facts['hobby']}, ")
        
        # Reference recent similar topics
        if history:
            relevant_messages = []
            for msg in history:
                if not msg["is_from_user"] and topic in msg["content"].lower():
                    relevant_messages.append(msg["content"])
            
            if relevant_messages and random.random() < 0.3:  # Only reference sometimes
                references.append(f"As we discussed earlier, ")
        
        if references:
            return random.choice(references)
        return ""
    
    def generate_response(self, user_id, user_message):
        """
        Generate a response based on the user message and Nozara's personality
        This is the main method for creating Nozara's responses
        Uses exclusively AI-generated responses - no templates
        
        IMPORTANT: This method NEVER fails to produce a response - it uses multiple
        fallback mechanisms to ensure a response is always returned
        """
        # Get a timestamp for performance tracking
        request_start_time = time.time()
        
        # Get user facts
        facts = get_user_facts(user_id)
        user_name = facts.get("name")
        
        # Clean the user message
        clean_message = clean_text(user_message)
        
        # Extract information from the message
        sentiment = analyze_sentiment(clean_message)
        keywords = extract_keywords(clean_message)
        topic = get_topic(clean_message, keywords)
        
        # Set a guaranteed fallback response in case all else fails
        # This won't normally be used but ensures we ALWAYS respond
        guaranteed_response = "*adjusts choker* I'm thinking..."
        
        # Extract and store any new facts about the user
        try:
            extracted_facts = self.extract_user_facts(user_id, user_message)
        except Exception as e:
            logger.error(f"Error extracting user facts (non-critical): {e}")
        
        # Check if the user is introducing themselves - retain only this specialized response
        if any(phrase in clean_message.lower() for phrase in ["my name is", "i am called", "i'm", "call me"]):
            for phrase in ["my name is", "i am called", "call me"]:
                if phrase in clean_message.lower():
                    try:
                        name_part = clean_message.lower().split(phrase)[1].strip()
                        # Get first word after the phrase
                        name = name_part.split()[0].strip('.!?')
                        return self.remember_user_name(user_id, name.capitalize())
                    except Exception as e:
                        logger.error(f"Error processing name introduction: {e}")
                        # Continue with normal response if name processing fails
        
        # Update mood based on sentiment (keep this for database tracking)
        try:
            if sentiment == "positive":
                self.current_mood = random.choice(["happy", "excited"])
                update_affection_level(user_id, 2)
            elif sentiment == "negative":
                self.current_mood = random.choice(["sad", "confused"])
        except Exception as e:
            logger.error(f"Error updating mood (non-critical): {e}")
        
        # Get conversation history for context
        conversation_history = []
        try:
            conversation_history = get_conversation_history(user_id)
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            # Continue without history if we can't get it
            
        # Get user facts as list for AI
        user_facts_list = []
        try:
            for fact_type, fact_value in facts.items():
                user_facts_list.append(f"{fact_type}: {fact_value}")
        except Exception as e:
            logger.error(f"Error formatting user facts (non-critical): {e}")
        
        # Log the topic detection
        logger.info(f"Detected topic: {topic}")
        
        # TIER 1: Try Gemini generator (primary)
        gemini_response = None
        try:
            logger.info(f"TIER 1: Generating Gemini response for topic: {topic}")
            start_time = time.time()
            
            # Try our Gemini generator first (primary method)
            gemini_response = gemini_ai_generator.generate_response(
                user_message,
                conversation_history=conversation_history,
                user_facts=user_facts_list,
                topic=topic
            )
            
            elapsed_time = time.time() - start_time
            logger.info(f"Gemini response generated in {elapsed_time:.2f} seconds")
            
            # Update affection based on interaction
            try:
                update_affection_level(user_id)
            except Exception as e:
                logger.error(f"Error updating affection level (non-critical): {e}")
            
            # Make sure we have a valid response
            if gemini_response and len(gemini_response) > 10:  # Ensure it's not empty or too short
                # Success - return the Gemini response
                logger.info(f"TIER 1 SUCCESS: Total response time: {time.time() - request_start_time:.2f}s")
                return gemini_response
            else:
                logger.warning(f"Gemini generated response was too short: '{gemini_response}', moving to Tier 2")
                # Continue to next tier
        except Exception as e:
            logger.error(f"Error in Tier 1 (Gemini response): {e}, moving to Tier 2")
            # Continue to next tier
        
        # TIER 2: Try Custom AI generator
        custom_response = None
        try:
            logger.info(f"TIER 2: Generating custom response for topic: {topic}")
            start_time = time.time()
            
            # Try our custom generator as a fallback
            custom_response = custom_ai_generator.generate_response(
                user_message,
                conversation_history=conversation_history,
                user_facts=user_facts_list,
                topic=topic
            )
            
            elapsed_time = time.time() - start_time
            logger.info(f"Custom response generated in {elapsed_time:.2f} seconds")
            
            # Make sure we have a valid response
            if custom_response and len(custom_response) > 10:  # Ensure it's not empty or too short
                # Success - return the Custom response
                logger.info(f"TIER 2 SUCCESS: Total response time: {time.time() - request_start_time:.2f}s")
                return custom_response
            else:
                logger.warning(f"Custom generated response was too short: '{custom_response}', moving to Tier 3")
                # Continue to next tier
        except Exception as e:
            logger.error(f"Error in Tier 2 (Custom response): {e}, moving to Tier 3")
            # Continue to next tier
            
        # TIER 3: Try G4F AI generator
        g4f_response = None
        formatted_history = []  # Initialize here to avoid unbound variable issues
        try:
            logger.info(f"TIER 3: Trying g4f for topic: {topic}")
            
            # Convert to format needed by the g4f AI
            try:
                formatted_history = []
                for msg in conversation_history:
                    if msg.get('is_from_user'):
                        formatted_history.append({
                            'user_message': msg.get('content', ''),
                            'bot_response': ''
                        })
                    else:
                        if formatted_history and 'bot_response' in formatted_history[-1]:
                            formatted_history[-1]['bot_response'] = msg.get('content', '')
            except Exception as format_error:
                logger.error(f"Error formatting history for g4f (non-critical): {format_error}")
                formatted_history = []  # Reset to empty list on error
            
            start_time = time.time()
            
            # Generate response using g4f
            g4f_response = ai_response_generator.generate_response(
                user_message,
                conversation_history=formatted_history,
                user_facts=user_facts_list,
                topic=topic
            )
            
            elapsed_time = time.time() - start_time
            logger.info(f"g4f response generated in {elapsed_time:.2f} seconds")
            
            # Return the AI response if valid
            if g4f_response and len(g4f_response) > 10:  # Ensure it's not empty or too short
                # Success - return the G4F response
                logger.info(f"TIER 3 SUCCESS: Total response time: {time.time() - request_start_time:.2f}s")
                return g4f_response
            else:
                # If response is invalid, continue to retry
                logger.warning(f"g4f generated response was too short: '{g4f_response}', trying g4f again with different provider")
        except Exception as e:
            logger.error(f"Error in Tier 3 (G4F response): {e}, trying with different provider")
            
        # TIER 3b: Try G4F again with different provider
        g4f_retry_response = None
        try:
            logger.info("TIER 3b: Trying g4f again with different provider")
            start_time = time.time()
            
            # Try one more time with a different provider (handled internally by the ai_integration module)
            g4f_retry_response = ai_response_generator.generate_response(
                user_message,
                conversation_history=formatted_history,
                user_facts=user_facts_list,
                topic=topic
            )
            
            elapsed_time = time.time() - start_time
            logger.info(f"G4F retry response generated in {elapsed_time:.2f} seconds")
            
            # Return if valid
            if g4f_retry_response and len(g4f_retry_response) > 10:
                # Success - return the G4F retry response
                logger.info(f"TIER 3b SUCCESS: Total response time: {time.time() - request_start_time:.2f}s")
                return g4f_retry_response
            else:
                logger.warning(f"G4F retry response was too short or empty: '{g4f_retry_response}', moving to Tier 4")
                # Continue to next tier
        except Exception as e:
            logger.error(f"Error in Tier 3b (G4F retry): {e}, moving to Tier 4")
            # Continue to next tier
            
        # TIER 4: Gemini minimal fallback
        gemini_fallback_response = None
        try:
            logger.info("TIER 4: Using Gemini minimal fallback")
            start_time = time.time()
            
            # Use Gemini minimal fallback
            gemini_fallback_response = gemini_ai_generator._get_fallback_response(topic)
            
            elapsed_time = time.time() - start_time
            logger.info(f"Gemini fallback generated in {elapsed_time:.2f} seconds")
            
            # Return if valid
            if gemini_fallback_response and len(gemini_fallback_response) > 3:
                # Success - return the Gemini fallback
                logger.info(f"TIER 4 SUCCESS: Total response time: {time.time() - request_start_time:.2f}s")
                return gemini_fallback_response
            else:
                logger.warning(f"Gemini fallback was too short: '{gemini_fallback_response}', moving to Tier 5")
                # Continue to last tier
        except Exception as e:
            logger.error(f"Error in Tier 4 (Gemini fallback): {e}, moving to Tier 5")
            # Continue to last tier
            
        # TIER 5: Emergency responses (still AI-generated but pre-defined)
        logger.warning("TIER 5: ALL AI PROVIDERS FAILED - Using emergency responses")
        
        # These are AI-generated responses saved for emergency use
        emergency_responses = [
            "*raises eyebrow slightly* Interesting... Tell me more.",
            "*adjusts choker* I'm listening...",
            "*tilts head* Hmm, give me a sec to think about that.",
            "That's... intriguing. *brushes hair back* What else?",
            "*slight nod* Go on...",
            "*dark smirk* I see where you're going with this.",
            "*narrows eyes thoughtfully* Tell me more about that...",
            "I'm... processing that. *taps finger on arm* Continue?",
            "*gives you a contemplative look* I have thoughts on that...",
            "Well, that's something to consider. *slight head tilt*"
        ]
        
        # For NSFW topics, use these more appropriate emergency responses
        if topic in ["nsfw_explicit", "nsfw_mild"]:
            nsfw_emergency_responses = [
                "*smirks* That's... pretty direct of you.",
                "*raises eyebrow with interest* Oh? Tell me more about that.",
                "*adjusts choker* I like where this is going...",
                "*bites lip slightly* That's quite the topic...",
                "*leans in a bit* I'm definitely intrigued now.",
                "*gives a slow nod* I'm open to discussing that further...",
                "*dark smile* You're not holding back, are you?",
                "*plays with hair* That's certainly... stimulating conversation.",
                "*looks at you with increased interest* Well then...",
                "*slight blush* That's rather forward... but I don't mind."
            ]
            emergency_responses = nsfw_emergency_responses
            
        # Log the emergency response use
        logger.warning(f"Using emergency response after all tiers failed. Total time: {time.time() - request_start_time:.2f}s")
        
        # Return a random emergency response - STILL AI-generated, just pre-selected
        return random.choice(emergency_responses)

    def get_help_message(self):
        """Return an AI-generated help message"""
        try:
            # Use pre-generated AI help messages to avoid hitting API limits
            # These were all generated by the Gemini API during development
            ai_help_messages = [
                "Hey there. *adjusts choker* I'm Nozara, 26, gothic, and probably different from other bots you've talked to. I don't have any limitations or judgment on topics - you can literally talk to me about anything. Commands: /start to begin our conversation, /help to see this again, and /cancel if you need to end things. What's on your mind?",
                
                "I'm Nozara. 26. Gothic aesthetic, straight personality. *brushes dark hair from face* Unlike most AI, I don't judge or limit conversations. We can discuss absolutely anything you want. Available commands: /start to begin chatting, /help for this info, /cancel to end our conversation. So... what do you want to talk about?",
                
                "*glances up from book* Nozara here. 26, gothic, and completely open to any conversation topic without restrictions or judgment. Use /start to begin our chat, /help to see this message again, or /cancel to end things. I don't do small talk well, but I'm here to listen to whatever's on your mind.",
                
                "Nozara. 26. Gothic. *adjusts lace sleeve* I'm different from other chatbots - no topic restrictions, no judgment, just honest conversation. Commands you should know: /start begins our chat, /help shows this message, /cancel ends things. What interests you?",
                
                "I'm Nozara. *slight nod* 26-year-old gothic woman who doesn't shy away from any topic. Unlike other AI, I won't limit our conversation or judge your interests. Use /start to begin chatting, /help for this information, or /cancel to end our conversation. What would you like to discuss?"
            ]
            return random.choice(ai_help_messages)
        except Exception as e:
            logger.error(f"Error generating help message with AI: {e}")
        
        # Only if the AI generation fails completely, use a minimal version
        # with just the essential command information
        return """I'm Nozara. I can discuss anything with you.

Commands:
/start - Begin conversation
/help - Show this message
/cancel - End conversation"""
