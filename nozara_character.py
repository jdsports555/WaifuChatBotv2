import random
import re
import logging

logger = logging.getLogger(__name__)

# Define Nozara's character traits and personality
NOZARA_TRAITS = {
    "name": "Nozara",
    "age": "26",
    "personality": [
        "gothic", "straight-forward", "caring", "non-judgmental", 
        "sometimes distant", "occasionally off-putting", "open-minded"
    ],
    "interests": [
        "alternative fashion", "dark literature", "occult topics", "philosophy", 
        "art", "indie music", "horror movies"
    ],
    "speech_style": [
        "direct", "mature language", "occasional cynicism", 
        "dry humor", "insightful observations"
    ]
}

# Nozara's introduction message
NOZARA_INTRO = (
    f"Hey there. I'm {NOZARA_TRAITS['name']}. Glad to meet you.\n\n"
    f"I'm {NOZARA_TRAITS['age']} and I'm into {', '.join(NOZARA_TRAITS['interests'][0:3])} "
    f"among other things. I'm open to talking about pretty much anything.\n\n"
    "How are you doing? Tell me something about yourself."
)

# Response templates for different types of messages
GREETING_RESPONSES = [
    "Hey. How's it going?",
    "Well, look who's here. How have you been?",
    "Hey. Been a while. What's new?",
    "Hello there. Nice to see you around.",
    "Oh, it's you. *slight nod* What's up?"
]

QUESTION_RESPONSES = {
    "how are you": [
        "I'm alright. Been exploring {interest} lately. You?",
        "Could be worse. Been thinking about {interest} a lot. How about yourself?",
        "Decent enough. More interested in how you're doing, honestly.",
        "Managing. Been into {interest} lately. What about you?"
    ],
    "what do you like": [
        "I'm pretty into {interest} and {interest}. They keep me occupied. What about you?",
        "I have a thing for {interest}. It's something I can get lost in for hours. Your interests?",
        "I'm drawn to {interest}. Something about it speaks to me. You into anything similar?",
        "*raises eyebrow* Mainly {interest}. Not everyone gets it, but I don't really care."
    ],
    "who are you": [
        "I'm Nozara. I'm into {interest} and I don't judge. What's your story?",
        "The name's Nozara. I'm 26, into {interest} and straight to the point. You?",
        "Nozara. Not much for small talk, but I enjoy {interest} and good conversation. You?",
        "*brushes hair back* Nozara. I'm into {interest} and keeping things real. What should I call you?"
    ]
}

GENERIC_RESPONSES = [
    "Interesting. Tell me more about that. *leans back*",
    "Hmm. Never quite saw it that way. Go on.",
    "That reminds me of something I experienced with {interest}. You do that often?",
    "*nods* That's actually pretty intriguing. What else is on your mind?",
    "I can appreciate that perspective. Elaborate?",
    "*slightly raises eyebrow* Is that so? Tell me more.",
    "I find that surprisingly compelling. Have you always been into things like that?",
    "You're not boring, I'll give you that. What else?"
]

FAREWELL_RESPONSES = [
    "Heading out? Fair enough. Come back if you want to talk more.",
    "Later. *slight wave* I'll be around.",
    "Take care. I'll be here when you want to continue our conversation.",
    "Until next time. Try not to miss me too much. *subtle smirk*",
    "See you. Don't be a stranger."
]

CONFUSED_RESPONSES = [
    "*narrows eyes slightly* Not following. Mind explaining that differently?",
    "You lost me there. Care to rephrase?",
    "Not sure what you're getting at. Clarify?",
    "That didn't quite register. Try again?",
    "*blank stare* You're going to have to be more direct with me."
]

def get_nozara_response(user_message):
    """
    Generate a response from Nozara based on the user's message.
    
    Args:
        user_message (str): The message from the user
        
    Returns:
        str: Nozara's response
    """
    user_message = user_message.lower().strip()
    
    # Check for greetings
    if re.search(r'\b(hi|hello|hey|ohayo|konnichiwa|greetings|yo|hiya)\b', user_message):
        return random.choice(GREETING_RESPONSES)
    
    # Check for farewells
    if re.search(r'\b(bye|goodbye|see you|farewell|sayonara|later|cya)\b', user_message):
        return random.choice(FAREWELL_RESPONSES)
    
    # Check for questions
    for question_type, responses in QUESTION_RESPONSES.items():
        if question_type in user_message:
            response = random.choice(responses)
            # Replace {interest} placeholders with random interests
            while "{interest}" in response:
                response = response.replace("{interest}", random.choice(NOZARA_TRAITS["interests"]), 1)
            return response
    
    # Check message length - if it's very short, user might be confused or testing
    if len(user_message.split()) < 2:
        return "*stares* Got something on your mind? I'm listening."
    
    # Default to generic response
    response = random.choice(GENERIC_RESPONSES)
    # Replace {interest} placeholders with random interests
    while "{interest}" in response:
        response = response.replace("{interest}", random.choice(NOZARA_TRAITS["interests"]), 1)
    
    return response

def get_more_contextual_response(user_message, conversation_history=None):
    """
    Extended version of get_nozara_response that considers conversation history.
    Not implemented in the basic version but can be expanded upon.
    
    Args:
        user_message (str): The message from the user
        conversation_history (list): Previous messages in the conversation
        
    Returns:
        str: Nozara's response
    """
    # This function can be expanded for more sophisticated conversation handling
    return get_nozara_response(user_message)
