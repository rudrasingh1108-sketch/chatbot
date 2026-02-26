import speech_recognition as sr
import pyttsx3
try:
    from gtts import gTTS
    import playsound
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
import time
import webbrowser
import os
import subprocess
from datetime import datetime
import requests
import json
from voice_profiles import VoiceProfile
from emotion_analyzer import EmotionAnalyzer
from gml import GigzsMemoryLayer


# Website mapping for easy access
WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://www.github.com",
    "stack overflow": "https://www.stackoverflow.com",
    "reddit": "https://www.reddit.com",
    "linkedin": "https://www.linkedin.com",
    "twitter": "https://www.twitter.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "gmail": "https://mail.google.com",
    "chatgpt": "https://www.chatgpt.com",
    "github copilot": "https://github.com/copilot",
}

# System applications mapping
APPLICATIONS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powershell": "powershell.exe",
    "command prompt": "cmd.exe",
    "file explorer": "explorer.exe",
    "settings": "ms-settings:",
    "task manager": "taskmgr.exe",
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
}

# News API configuration (Get free key from https://newsapi.org/)
NEWS_API_KEY = "017aa8b3ea10400eb7052708e71559e0"  


def listen_for_audio(recognizer, source, timeout=None, phrase_time_limit=None, engine="google"):
    try:
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    except Exception:
        return None, None
    try:
        if engine == "google":
            text = recognizer.recognize_google(audio)
        # Placeholder for other engines (e.g., Vosk, Sphinx)
        # elif engine == "vosk":
        #     ...
        # elif engine == "sphinx":
        #     text = recognizer.recognize_sphinx(audio)
        else:
            text = recognizer.recognize_google(audio)
        
        # Return both text and audio for emotion analysis
        return text, audio
    except sr.UnknownValueError:
        return None, audio
    except sr.RequestError:
        return "__API_ERROR__", audio


def check_and_open_website(user_input):
    """Check if user wants to open a website and open it if found."""
    user_input = user_input.lower()
    
    # Check for "open" command
    if "open" in user_input:
        for website_name, url in WEBSITES.items():
            if website_name in user_input:
                try:
                    webbrowser.open(url)
                    return f"Opening {website_name}"
                except Exception as e:
                    return f"Sorry, I could not open {website_name}"
    
    return None


def open_application(user_input):
    """Open applications based on user command."""
    user_input = user_input.lower()
    
    if "open" in user_input or "launch" in user_input:
        for app_name, app_path in APPLICATIONS.items():
            if app_name in user_input:
                try:
                    if "://" in app_path:  # For URLs like ms-settings:
                        os.startfile(app_path)
                    else:
                        subprocess.Popen(app_path)
                    return f"Opening {app_name}"
                except Exception as e:
                    return f"Sorry, I could not open {app_name}. It might not be installed"
    
    return None


def handle_system_commands(user_input):
    """Handle system control commands like shutdown, restart, etc."""
    user_input = user_input.lower()
    
    # Shutdown command
    if "shutdown" in user_input or "shut down" in user_input:
        response = "Shutting down the computer"
        return response, "shutdown"
    
    # Restart command
    if "restart" in user_input:
        response = "Restarting the computer"
        return response, "restart"
    
    # Sleep command
    if "sleep" in user_input or "hibernate" in user_input:
        response = "Putting the computer to sleep"
        return response, "sleep"
    
    # Lock command
    if "lock" in user_input:
        response = "Locking the computer"
        return response, "lock"
    
    return None, None


def execute_system_command(command_type):
    """Execute system control commands."""
    try:
        if command_type == "shutdown":
            os.system("shutdown /s /t 30")  # Shutdown after 30 seconds
        elif command_type == "restart":
            os.system("shutdown /r /t 30")  # Restart after 30 seconds
        elif command_type == "sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif command_type == "lock":
            os.system("rundll32.exe user32.dll,LockWorkStation")
    except Exception as e:
        print(f"Error executing command: {e}")


def get_time_and_date():
    """Get current time and date."""
    now = datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%A, %B %d, %Y")
    return f"The time is {time_str} and the date is {date_str}"


def handle_information_request(user_input):
    """Handle requests for time, date, and other information."""
    user_input = user_input.lower()
    
    if "time" in user_input or "what time" in user_input:
        return get_time_and_date()
    
    if "date" in user_input or "what date" in user_input:
        return get_time_and_date()
    
    return None


def get_weather(city="London"):
    """Get weather information for a city using open-meteo API (no key required)."""
    try:
        # Get coordinates for the city
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_response = requests.get(geo_url, timeout=5)
        geo_data = geo_response.json()
        
        if not geo_data.get("results"):
            return f"Could not find weather for {city}"
        
        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        city_name = geo_data["results"][0]["name"]
        
        # Get weather data
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,wind_speed_10m&temperature_unit=celsius"
        weather_response = requests.get(weather_url, timeout=5)
        weather_data = weather_response.json()
        
        current = weather_data.get("current", {})
        temp = current.get("temperature_2m", "N/A")
        wind = current.get("wind_speed_10m", "N/A")
        
        return f"Weather in {city_name}: {temp} degrees Celsius with wind speed of {wind} kilometers per hour"
    except Exception as e:
        return "Sorry, I could not fetch weather information"


def get_word_definition(word):
    """Get word definition from dictionary API."""
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.lower()}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                meanings = data[0].get("meanings", [])
                if meanings:
                    definition = meanings[0]["definitions"][0]["definition"]
                    return f"The definition of {word} is: {definition}"
        
        return f"Could not find definition for {word}"
    except Exception as e:
        return "Sorry, I could not fetch the definition"


def handle_queries(user_input):
    """Handle information and query requests."""
    user_input = user_input.lower()
    
    # Weather queries
    if "weather" in user_input:
        # Try to extract city name
        words = user_input.split()
        city = "London"  # Default city
        
        # Look for city name after "weather" or "weather in"
        if "in" in words:
            idx = words.index("in")
            if idx + 1 < len(words):
                city = " ".join(words[idx + 1:])
        
        return get_weather(city)
    
    # Dictionary/Definition queries
    if "define" in user_input or "definition" in user_input or "what is" in user_input:
        words = user_input.split()
        
        # Find the word to define
        if "define" in words:
            idx = words.index("define")
            if idx + 1 < len(words):
                word = words[idx + 1]
                return get_word_definition(word)
        elif "definition" in words:
            idx = words.index("definition")
            if idx + 2 < len(words) and words[idx + 1] == "of":
                word = words[idx + 2]
                return get_word_definition(word)
        elif "what is" in user_input:
            # Extract word after "what is"
            parts = user_input.split("what is")
            if len(parts) > 1:
                word = parts[1].strip().split()[0]
                return get_word_definition(word)
    
    # News queries
    if "news" in user_input or "headlines" in user_input:
        return get_news(user_input)
    
    return None


def get_news(user_input=""):
    """Fetch latest news headlines."""
    try:
        if NEWS_API_KEY == "demo":
            return "Please set up a free API key from newsapi.org and update the NEWS_API_KEY variable in the code"
        
        # Try to extract category or search term
        category = "general"
        keywords = ["business", "entertainment", "health", "science", "sports", "technology"]
        
        for keyword in keywords:
            if keyword in user_input.lower():
                category = keyword
                break
        
        # NewsAPI endpoint
        url = f"https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={NEWS_API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            
            if not articles:
                return f"No news found for {category}"
            
            # Get top 3 headlines
            headlines = ""
            for i, article in enumerate(articles[:3], 1):
                title = article.get("title", "No title")
                headlines += f"{i}. {title}. "
            
            return f"Here are the latest {category} news headlines: {headlines}"
        else:
            return "Sorry, I could not fetch news at the moment"
    except Exception as e:
        return "Sorry, I could not fetch news. Please check your internet connection"


def tell_joke():
    """Fetch and tell a random joke."""
    try:
        url = "https://official-joke-api.appspot.com/random_joke"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            joke = data.get("setup", "") + " " + data.get("punchline", "")
            return f"Here's a joke for you: {joke}"
        else:
            return "Sorry, I could not fetch a joke"
    except Exception as e:
        return "Sorry, I could not fetch a joke"


def perform_calculation(user_input):
    """Perform simple mathematical calculations."""
    try:
        # Extract math expression from common phrases
        calc_input = user_input.lower()
        
        if "what is" in calc_input:
            calc_input = calc_input.split("what is")[-1].strip()
        elif "calculate" in calc_input:
            calc_input = calc_input.split("calculate")[-1].strip()
        elif "compute" in calc_input:
            calc_input = calc_input.split("compute")[-1].strip()
        
        # Replace written numbers with digits
        replacements = {
            "plus": "+", "add": "+",
            "minus": "-", "subtract": "-",
            "times": "*", "multiply": "*",
            "divide": "/", "divided by": "/",
            "power": "**", "squared": "**2", "cubed": "**3"
        }
        
        for word, symbol in replacements.items():
            calc_input = calc_input.replace(word, symbol)
        
        # Evaluate the expression safely
        result = eval(calc_input)
        return f"The answer is {result}"
    except Exception as e:
        return "Sorry, I could not calculate that. Please try a different calculation"


def search_web(query):
    """Search Google for information."""
    query = query.lower()
    
    # Remove common search phrases
    search_terms = query.replace("search", "").replace("google", "").replace("find", "").replace("look for", "").strip()
    
    if search_terms:
        search_url = f"https://www.google.com/search?q={search_terms}"
        webbrowser.open(search_url)
        return f"Searching Google for {search_terms}"
    
    return None


def get_help():
    """Provide list of available commands."""
    help_text = """Here are the available commands: 
    
    Website Commands: Say 'open youtube', 'open google', 'open github', etc.
    
    Application Commands: Say 'open notepad', 'open calculator', 'open file explorer', etc.
    
    System Commands: Say 'shutdown', 'restart', 'lock', or 'sleep'.
    
    Information: Say 'what time is it', 'what is the date', 'tell me a joke'.
    
    Weather: Say 'what is the weather' or 'weather in [city]'.
    
    News: Say 'news', 'headlines', or '[category] news' like 'technology news'.
    
    Definitions: Say 'define [word]' or 'what is [word]'.
    
    Calculations: Say 'what is 5 plus 3' or 'calculate 10 times 2'.
    
    Search: Say 'search [something]' or 'google [something]'.
    
    Help: Say 'help' or 'what can you do'."""
    return help_text


def handle_entertainment(user_input):
    """Handle entertainment requests like jokes."""
    user_input = user_input.lower()
    
    if "joke" in user_input or "funny" in user_input:
        return tell_joke()
    
    return None


def handle_calculation(user_input):
    """Handle calculation requests."""
    user_input = user_input.lower()
    
    if "what is" in user_input or "calculate" in user_input or "compute" in user_input or "times" in user_input or "plus" in user_input:
        # Check if it's a math question
        math_words = ["plus", "minus", "times", "divide", "multiplied", "add", "subtract", "calculate", "what is"]
        if any(word in user_input for word in math_words):
            return perform_calculation(user_input)
    
    return None


def handle_emotion_commands(user_input, emotion_analyzer, context):
    """Handle emotion analysis and psychology-aware commands."""
    user_input = user_input.lower()
    
    # Status queries
    if "how am i feeling" in user_input or "what's my emotion" in user_input or "how do i sound" in user_input:
        emotion = context.get("last_emotion", "neutral")
        confidence = context.get("emotion_confidence", 0)
        if emotion != "neutral":
            tips = emotion_analyzer.get_emotion_tips(emotion)
            return f"You sound {emotion} (confidence: {confidence:.0%}). Here are some tips: {tips[0] if tips else 'Take care of yourself!'}"
        else:
            return "I haven't analyzed your emotional state yet. Keep talking!"
    
    if "emotional summary" in user_input or "emotion history" in user_input or "how have i been" in user_input:
        summary = emotion_analyzer.get_emotion_summary()
        if summary.get("total_records"):
            return f"You've had {summary['total_records']} voice interactions. Your most common emotion was {summary['most_common']}."
        else:
            return "No emotional data collected yet."
    
    if "stress relief" in user_input or "help with stress" in user_input or "i'm stressed" in user_input:
        tips = emotion_analyzer.get_emotion_tips("stress")
        return f"Here are stress relief suggestions: {tips[0]}. {tips[1] if len(tips) > 1 else ''}"
    
    if "calm me down" in user_input or "relax" in user_input or "help me relax" in user_input:
        return "Try deep breathing: Breathe in for 4 counts, hold for 7, exhale for 8. Repeat 5 times. Would you like me to guide you through a breathing exercise?"
    
    if "boost confidence" in user_input or "build confidence" in user_input or "feel confident" in user_input:
        return "You've already accomplished so much! Remember your past successes. Focus on one thing at a time. You've got this!"
    
    if "cheer me up" in user_input or "make me happy" in user_input or "i'm sad" in user_input:
        return "I hear you. Why don't you tell me what's bothering you? Or I can tell you a joke to lighten the mood?"
    
    if "motivation" in user_input or "motivate me" in user_input or "inspire me" in user_input:
        return "You have unlimited potential! Every challenge is an opportunity to grow. Start with one small step today!"
    
    return None


def handle_search(user_input):
    """Handle web search requests."""
    user_input = user_input.lower()
    
    if "search" in user_input or ("google" in user_input and "the weather" not in user_input):
        return search_web(user_input)
    
    return None


def handle_help(user_input):
    """Handle help and command listing."""
    user_input = user_input.lower()
    
    if "help" in user_input or "what can you do" in user_input or "available commands" in user_input:
        return get_help()
    

    return None


def handle_voice_profile(user_input):
    """Handle voice profile training and identification commands."""
    user_input = user_input.lower()
    
    # This will be used after initialization
    return None


def handle_user_recognition(recognizer, source, voice_profile_manager):
    """Handle speaker identification"""
    try:
        username, confidence = voice_profile_manager.identify_speaker(recognizer, source)
        if username:
            return username, confidence
    except Exception as e:
        print(f"Error in user recognition: {e}")
    return None, 0


def main():
    # Engine selection (could be loaded from config in future)
    speech_engine = "google"  # or "vosk", "sphinx" if implemented
    tts_engine = "pyttsx3"    # or "gtts" if implemented
    
    # Initialize voice profile manager for multi-user recognition
    voice_profile_manager = VoiceProfile()
    
    # Initialize emotion analyzer for psychological mode
    emotion_analyzer = EmotionAnalyzer()
    
    # Initialize Gigzs Memory Layer for long-term recall
    gml = GigzsMemoryLayer()

    def speak(text):
        if tts_engine == "pyttsx3":
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 1.0)
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"TTS error: {e}")
        elif tts_engine == "gtts" and GTTS_AVAILABLE:
            try:
                tts = gTTS(text=text, lang='en')
                tts.save("temp_gtts.mp3")
                playsound.playsound("temp_gtts.mp3")
                os.remove("temp_gtts.mp3")
            except Exception as e:
                print(f"gTTS error: {e}")
        else:
            print("No valid TTS engine available.")

    # speak initial greeting before listening for wake word
    greeting = "hello sir"
    print("Speaking:", greeting)
    speak(greeting)

    r = sr.Recognizer()
    wake_words = ["hey assistant", "hey bot", "hello assistant", "hey sir", "assistant"]

    # Persistent conversation context memory (retained across sessions)
    context = {
        "last_command": None,
        "last_result": None,
        "history": [],
        "current_user": None,
        "user_confidence": 0
    }

    # Exit phrases to end conversation
    exit_phrases = ["exit", "bye", "goodbye", "see you", "stop listening", "that's all"]

    # Main wake word detection loop
    in_conversation = False

    while True:
        try:
            if not in_conversation:
                # Listen for wake word
                with sr.Microphone() as source:
                    try:
                        r.adjust_for_ambient_noise(source, duration=1)
                        print("Listening for wake word...")
                        heard_text, heard_audio = listen_for_audio(r, source, timeout=None, phrase_time_limit=5, engine=speech_engine)
                    except Exception as mic_err:
                        print(f"Microphone error: {mic_err}")
                        continue

                    if heard_text is None:
                        continue
                    if heard_text == "__API_ERROR__":
                        print("Google API error occurred while listening for wake word")
                        continue

                    heard_lower = heard_text.lower()
                    print("Heard:", heard_lower)

                    if not any(w in heard_lower for w in wake_words):
                        continue

                # Wake word detected, enter conversation mode
                in_conversation = True
                print("Wake word detected! Starting conversation mode...")
                time.sleep(1.0)
                
                # Attempt to identify the speaker
                try:
                    with sr.Microphone() as source:
                        username, confidence = voice_profile_manager.identify_speaker(r, source, threshold=0.70)
                        if username:
                            context["current_user"] = username
                            context["user_confidence"] = confidence
                            print(f"Speaker identified: {username} (confidence: {confidence:.2f})")
                            greeting = voice_profile_manager.get_personalized_greeting(username)
                        else:
                            context["current_user"] = None
                            greeting = "Welcome! I couldn't recognize you. What can I do for you?"
                except Exception as e:
                    print(f"Speaker identification failed: {e}")
                    context["current_user"] = None
                    greeting = "hello, how can I help you today?"
                
                print("Speaking:", greeting)
                speak(greeting)
                time.sleep(1.5)

            # Conversation mode: listen for user commands
            audio_data = None
            with sr.Microphone() as source:
                try:
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    print("Listening for your request...")
                    result, audio_data = listen_for_audio(r, source, timeout=5, phrase_time_limit=8, engine=speech_engine)
                except Exception as mic_err:
                    print(f"Microphone error: {mic_err}")
                    result = None
                    continue

            if result is None:
                reply = "Could not understand what you said"
            elif result == "__API_ERROR__":
                reply = "API error occurred"
            else:
                # Analyze emotion from user speech if audio data available
                if audio_data is not None:
                    try:
                        import numpy as np
                        audio_data_array = np.frombuffer(audio_data.get_raw_data(), np.int16)
                        emotion_result = emotion_analyzer.analyze_emotion(audio_data_array)
                        print(f"Emotion Detected: {emotion_result['description']} (confidence: {emotion_result['confidence']:.2f})")
                        context["last_emotion"] = emotion_result["emotional_state"]
                        context["emotion_confidence"] = emotion_result["confidence"]
                    except Exception as e:
                        print(f"Emotion analysis error: {e}")
                
                # Check for exit phrases to end conversation mode
                user_input = result.lower()
                if any(phrase in user_input for phrase in exit_phrases):
                    reply = "Goodbye! Going back to sleep mode."
                    in_conversation = False
                    context["current_user"] = None
                    speak(reply)
                    continue

                # Check for voice profile commands
                if "train voice" in user_input or "train profile" in user_input:
                    username = user_input.replace("train voice", "").replace("train profile", "").strip()
                    if not username:
                        username = input("Enter username for new profile: ")
                    reply = voice_profile_manager.create_profile(username, num_samples=3)
                    speak(reply)
                    continue
                
                if "list users" in user_input or "show users" in user_input:
                    reply = voice_profile_manager.list_users()
                    speak(reply)
                    continue
                
                if "delete profile" in user_input:
                    username = user_input.replace("delete profile", "").strip()
                    if not username:
                        username = input("Enter username to delete: ")
                    reply = voice_profile_manager.delete_profile(username)
                    speak(reply)
                    continue
                
                # Handle GML Memory commands
                if "remember" in user_input or "add to memory" in user_input:
                    # Extract what to remember
                    if "that" in user_input:
                        memory_text = user_input.replace("remember that", "").replace("remember", "").replace("add to memory", "").strip()
                    else:
                        memory_text = user_input.replace("remember", "").replace("add to memory", "").strip()
                    
                    if memory_text and context["current_user"]:
                        # Log as event with current user
                        user_entity_id = gml.find_entity(context["current_user"], "person")
                        if not user_entity_id:
                            user_entity_id = gml.add_entity(context["current_user"], "person")
                        
                        gml.log_event(f"User told me: {memory_text}", [user_entity_id], "important_note")
                        gml.save_memory()
                        reply = f"Got it! I'll remember that: {memory_text}"
                    else:
                        reply = "Please tell me what you'd like me to remember."
                    speak(reply)
                    continue
                
                if "recall" in user_input or "remind me" in user_input or "what do you remember" in user_input:
                    # Extract recall query
                    memory_query = user_input.replace("recall", "").replace("remind me about", "").replace("what do you remember about", "").strip()
                    
                    if not memory_query:
                        memory_query = context["current_user"] if context["current_user"] else "general"
                    
                    recall_result = gml.recall(memory_query)
                    
                    # Format response
                    if recall_result['entities']:
                        entity = recall_result['entities'][0]
                        reply = f"I remember {entity['name']}. You told me they are a {entity.get('attributes', {}).get('description', 'person')}."
                    elif recall_result['events']:
                        event = recall_result['events'][0]
                        reply = f"I remember: {event['description']}"
                    else:
                        reply = f"I don't have specific memories about {memory_query}, but I'm learning."
                    
                    speak(reply)
                    continue
                
                if "memory status" in user_input or "how much do you remember" in user_input:
                    stats = gml.get_memory_stats()
                    reply = f"My memory currently has {stats['total_entities']} entities, {stats['total_relationships']} relationships, and {stats['total_events']} events."
                    speak(reply)
                    continue

                # Contextual conversation logic
                context["history"].append(user_input)
                reply = None

                try:
                    # Multi-step context-aware logic
                    if context["last_command"] == "open_youtube" and ("search" in user_input or "find" in user_input):
                        # e.g., "search for AI tutorials"
                        search_query = user_input.replace("search for","").replace("find","").strip()
                        if search_query:
                            webbrowser.open(f"https://www.youtube.com/results?search_query={search_query.replace(' ','+')}")
                            reply = f"Searching YouTube for {search_query}"
                            context["last_command"] = "youtube_search"
                            context["last_result"] = search_query
                    elif context["last_command"] == "youtube_search" and "play" in user_input and "first" in user_input:
                        # e.g., "play the first one"
                        reply = "Playing the first YouTube result (please click it in your browser)."
                        context["last_command"] = None
                        context["last_result"] = None
                    else:
                        # Check for emotion-aware commands first
                        reply = handle_emotion_commands(user_input, emotion_analyzer, context)
                        
                        if not reply:
                            # Standard command handlers
                            command_handlers = [
                                handle_help,
                                check_and_open_website,
                                open_application,
                                handle_information_request,
                                handle_queries,
                                handle_entertainment,
                                handle_calculation,
                                handle_search
                            ]
                            for handler in command_handlers:
                                handler_result = handler(user_input)
                                if handler_result:
                                    reply = handler_result
                                # Track context for YouTube
                                if handler == check_and_open_website and "youtube" in user_input:
                                    context["last_command"] = "open_youtube"
                                    context["last_result"] = "youtube"
                                else:
                                    context["last_command"] = None
                                    context["last_result"] = None
                                break
                        if reply is None:
                            system_reply, command_type = handle_system_commands(user_input)
                            if system_reply:
                                reply = system_reply
                                if command_type:
                                    execute_system_command(command_type)
                                context["last_command"] = None
                                context["last_result"] = None
                            else:
                                reply = user_input
                                context["last_command"] = None
                                context["last_result"] = None
                    
                    # Log interaction to GML memory (auto-memory feature)
                    if context["current_user"] and reply:
                        try:
                            user_entity_id = gml.find_entity(context["current_user"], "person")
                            if not user_entity_id:
                                user_entity_id = gml.add_entity(context["current_user"], "person")
                            
                            gml.log_event(
                                f"User: '{user_input}' | Bot: '{reply[:100]}'",
                                [user_entity_id],
                                "conversation"
                            )
                            
                            # Save memory every 5 interactions
                            if len(context["history"]) % 5 == 0:
                                gml.save_memory()
                        except Exception as gml_err:
                            print(f"GML logging error: {gml_err}")
                
                except Exception as cmd_err:
                    reply = f"Sorry, an error occurred while processing your request: {cmd_err}"
                
                # Enhance response based on emotional state
                emotion = context.get("last_emotion")
                if emotion == "stress":
                    reply = f"{reply} By the way, I notice you sound a bit stressed. Want me to play some calming music or suggest a breathing exercise?"
                elif emotion == "nervousness":
                    reply = f"{reply} Don't worry, you sound a little nervous, but you're doing great! I'm here to help."
                elif emotion == "excitement":
                    reply = f"{reply} Wow, you sound excited! That's awesome energy! Let's make it happen!"
                elif emotion == "sadness":
                    reply = f"{reply} I sense you might be feeling a bit down. Want me to play some uplifting music or tell you something funny?"
                
                # Store emotion in context for potential commands
                context["last_result"] = reply

            print("User said:", reply)
            speak(reply)
        except KeyboardInterrupt:
            print("Exiting chatbot. Goodbye!")
            break
        except Exception as loop_err:
            print(f"Unexpected error in main loop: {loop_err}")
            time.sleep(2)


if __name__ == "__main__":
    main()
