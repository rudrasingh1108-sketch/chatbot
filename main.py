import speech_recognition as sr
import pyttsx3
import time
import webbrowser
import os
import subprocess
from datetime import datetime
import requests
import json


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


def listen_for_audio(recognizer, source, timeout=None, phrase_time_limit=None):
    try:
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    except Exception:
        return None
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return "__API_ERROR__"


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
    engine = pyttsx3.init()
    # Configure TTS for better output
    engine.setProperty('rate', 150)  # slower speech
    engine.setProperty('volume', 1.0)  # max volume
    
    # speak initial greeting before listening for wake word
    greeting = "hello sir"
    print("Speaking:", greeting)
    engine.say(greeting)
    engine.runAndWait()

    r = sr.Recognizer()

    wake_words = ["hey assistant", "hey bot", "hello assistant", "hey sir", "assistant"]

    # Loop that opens microphone to detect wake word, then closes it before speaking
    while True:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
            print("Listening for wake word...")

            heard = listen_for_audio(r, source, timeout=None, phrase_time_limit=5)
            if heard is None:
                continue
            if heard == "__API_ERROR__":
                print("Google API error occurred while listening for wake word")
                continue

            heard_text = heard.lower()
            print("Heard:", heard_text)

            if not any(w in heard_text for w in wake_words):
                continue

        # microphone `source` is now closed (we exited the with-block)
        print("Wake word detected! Preparing to speak...")
        
        # Close previous engine and recreate it
        del engine
        time.sleep(1.0)
        
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        
        prompt = "what can i do for you today"
        print("Speaking:", prompt)
        try:
            engine.say(prompt)
            engine.runAndWait()
            print("Finished speaking prompt")
        except Exception as e:
            print("TTS error:", e)

        # Close engine and wait before opening microphone
        del engine
        time.sleep(1.5)

        # open microphone again to capture the user's request (avoids audio device conflicts)
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening for your request...")
            result = listen_for_audio(r, source, timeout=5, phrase_time_limit=8)

        if result is None:
            reply = "Could not understand what you said"
        elif result == "__API_ERROR__":
            reply = "API error occurred"
        else:
            # Check for help command first
            help_result = handle_help(result)
            if help_result:
                reply = help_result
            # Check if user wants to open a website
            elif check_and_open_website(result):
                reply = check_and_open_website(result)
            # Check if user wants to open an application
            elif open_application(result):
                reply = open_application(result)
            # Check for information and queries (time, date, weather, definitions)
            elif handle_information_request(result):
                reply = handle_information_request(result)
            elif handle_queries(result):
                reply = handle_queries(result)
            # Check for entertainment (jokes)
            elif handle_entertainment(result):
                reply = handle_entertainment(result)
            # Check for calculations
            elif handle_calculation(result):
                reply = handle_calculation(result)
            # Check for web search
            elif handle_search(result):
                reply = handle_search(result)
            # Check for system control commands
            else:
                system_reply, command_type = handle_system_commands(result)
                if system_reply:
                    reply = system_reply
                    # Execute the system command
                    if command_type:
                        execute_system_command(command_type)
                else:
                    reply = result

        print("User said:", reply)
        
        # Recreate engine for final response
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        engine.say(reply)
        engine.runAndWait()


if __name__ == "__main__":
    main()
