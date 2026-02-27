"""
Chatbot Web Application - Flask Backend
Provides REST API for the voice assistant chatbot
"""

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import sys
import json
import requests
import re
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from typing import Dict, Any
from dotenv import load_dotenv
try:
    from vosk import Model, KaldiRecognizer
    import wave
    import io
    import soundfile as sf
    import numpy as np
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False

from core.voice_profiles import VoiceProfile
from core.emotion_analyzer import EmotionAnalyzer
from core.gml import GigzsMemoryLayer
import speech_recognition as sr
import numpy as np

import webbrowser
from main import check_and_open_website, execute_system_command
from brain import JarvisBrain
from whatsapp_sim import WhatsAppSimulator

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
CORS(app)

# Initialize Brain
jarvis_brain = JarvisBrain()
whatsapp_sim = WhatsAppSimulator(jarvis_brain)

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(_PROJECT_ROOT, '.env'), override=True)
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)

vosk_model = None
if VOSK_AVAILABLE:
    try:
        vosk_model = Model(lang="en-us")
    except Exception as e:
        print(f"Error loading Vosk model: {e}")

whisper_model = None
if FASTER_WHISPER_AVAILABLE:
    try:
        whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    except Exception as e:
        print(f"Error loading Whisper model: {e}")

from wake_word import WakeWordDetector

# Initialize managers
voice_profile_manager = VoiceProfile()
emotion_analyzer = EmotionAnalyzer()
gml = GigzsMemoryLayer()  # Initialize Gigzs Memory Layer
wake_detector = WakeWordDetector()
wake_detector.start()

# Chat history storage
chat_history = []
current_user = None

# ==================== Simulated IoT Device State ====================

devices: Dict[str, Dict[str, Any]] = {
    "living_room_light": {"id": "living_room_light", "name": "Living Room Light", "type": "light", "state": {"power": False}},
    "bedroom_light": {"id": "bedroom_light", "name": "Bedroom Light", "type": "light", "state": {"power": False}},
    "fan": {"id": "fan", "name": "Fan", "type": "switch", "state": {"power": False}},
    "thermostat": {"id": "thermostat", "name": "Thermostat", "type": "thermostat", "state": {"temperature": 24}},
    "door_lock": {"id": "door_lock", "name": "Door Lock", "type": "lock", "state": {"locked": True}},
}

from main import (
    check_and_open_website,
    open_application,
    handle_system_commands,
    execute_system_command,
    handle_information_request,
    handle_queries,
    handle_entertainment,
    handle_calculation,
    handle_search,
    handle_help,
    get_weather,
    get_word_definition,
    get_news,
    tell_joke,
    perform_calculation
)

@app.route('/')
def index():
    """Serve landing page"""
    return render_template('landing.html')


@app.route('/chat')
def chat_page():
    """Serve the chatbot interface"""
    return render_template('chat.html')


@app.route('/iot')
def iot_page():
    """Serve the IoT dashboard"""
    return render_template('iot.html')


@app.route('/.well-known/appspecific/com.chrome.devtools.json')
def chrome_devtools_well_known():
    return jsonify({}), 200


@app.route('/favicon.ico')
def favicon():
    return (b"", 204)


@app.route('/api/stt/transcribe', methods=['POST'])
def stt_transcribe():
    """Transcribe audio using local STT (Whisper if available, else Vosk). Expects multipart form-data field 'audio'."""
    if not ((FASTER_WHISPER_AVAILABLE and whisper_model) or (VOSK_AVAILABLE and vosk_model)):
        return jsonify({"error": "No local STT model available"}), 500

    if 'audio' not in request.files:
        return jsonify({"error": "audio file required"}), 400

    f = request.files['audio']
    if not f:
        return jsonify({"error": "invalid audio file"}), 400

    try:
        raw_bytes = f.read()

        # 1) Try decoding with soundfile first (fast path)
        audio_data = None
        samplerate = None
        try:
            audio_data, samplerate = sf.read(io.BytesIO(raw_bytes))
        except Exception:
            audio_data = None
            samplerate = None

        # 2) Fallback: use SpeechRecognition's AudioFile decoder (more tolerant on some systems)
        # This requires system codecs for the given container; it often succeeds where libsndfile fails.
        if audio_data is None or samplerate is None:
            try:
                r = sr.Recognizer()
                with sr.AudioFile(io.BytesIO(raw_bytes)) as source:
                    audio = r.record(source)
                pcm = audio.get_raw_data(convert_rate=16000, convert_width=2)
                samplerate = 16000
                audio_int16 = np.frombuffer(pcm, dtype=np.int16)
            except Exception as e:
                raise RuntimeError(f"Format not recognised by available decoders: {e}")
        else:
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)
            # Convert float PCM to int16
            audio_int16 = (audio_data * 32767).astype(np.int16)

        # Prefer Whisper for better accuracy
        if FASTER_WHISPER_AVAILABLE and whisper_model:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
                sf.write(tmp.name, audio_int16.astype(np.float32) / 32768.0, samplerate)
                segments, _info = whisper_model.transcribe(tmp.name, language="en")
                text = "".join(seg.text for seg in segments).strip()
                return jsonify({"text": text}), 200

        rec = KaldiRecognizer(vosk_model, samplerate)
        rec.SetWords(True)
        rec.AcceptWaveform(audio_int16.tobytes())

        res = json.loads(rec.FinalResult())
        return jsonify({"text": res.get("text", "").strip()}), 200
    except Exception as e:
        print(f"Transcription error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    global chat_history, current_user
    
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Process the message through command handlers
        reply = process_command(user_message)
        
        # Log interaction to GML memory
        if current_user:
            # Create/find user entity if not exists
            user_entity_id = gml.find_entity(current_user, "person")
            if not user_entity_id:
                user_entity_id = gml.add_entity(current_user, "person")
            
            # Log the interaction as an event
            gml.log_event(
                f"User said: '{user_message}' - Bot responded: '{reply}'",
                [user_entity_id],
                "conversation"
            )
        
        # Store in chat history
        chat_history.append({
            'user': user_message,
            'bot': reply,
            'timestamp': datetime.now().isoformat(),
            'user_id': current_user
        })
        
        # Save memory periodically
        if len(chat_history) % 10 == 0:
            gml.save_memory()
        
        return jsonify({
            'user': user_message,
            'bot': reply,
            'user_id': current_user,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def openrouter_chat(messages):
    # Reload .env each call so edits to /Users/aaruni/chatbot/.env take effect
    load_dotenv(os.path.join(_PROJECT_ROOT, '.env'), override=True)
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)

    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return ""

    model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001").strip() or "google/gemini-2.0-flash-001"
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8080",
            "X-Title": "Chatbot",
        }
        payload = {
            "model": model,
            "temperature": 0.2,
            "messages": messages,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        if resp.status_code != 200:
            return f"[openrouter_error] status={resp.status_code} body={resp.text[:500]}"
        data = resp.json()
        return (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
    except Exception as e:
        return f"[openrouter_exception] {type(e).__name__}: {str(e)}"


@app.route('/api/assistant', methods=['POST'])
def assistant():
    """Main assistant endpoint using LangGraph brain"""
    try:
        data = request.json
        user_input = data.get('text', '')
        user_id = data.get('user_id', 'default_user')
        
        if not user_input:
            return jsonify({'error': 'No input provided'}), 400

        # 1. Try to route to specialized tools first (like IoT)
        # (Assuming handle_iot_request is defined or we use old logic for now)
        # But let's prioritize the smart brain and its command detection
        
        user_id = current_user or "anonymous"
        analysis = jarvis_brain.chat(user_id, user_input)
        
        # 2. Check for local system commands in the LLM response
        command = analysis.get('command')
        command_args = analysis.get('command_args', {})
        
        # Handle open_website command from LLM
        if command == 'open_website':
            url = command_args.get('url')
            if url:
                # Basic URL normalization
                if not url.startswith(('http://', 'https://')):
                    # If it looks like a domain, add https
                    if '.' in url and '/' not in url:
                        url = 'https://' + url
                    else:
                        # Otherwise, treat as search query
                        url = f"https://www.google.com/search?q={requests.utils.quote(url)}"
                webbrowser.open(url)
                print(f"JARVIS: Executed command open_website with url {url}")
        
        # Fallback for explicit "open" keywords
        elif "open" in user_input.lower():
            # First try the predefined mapping
            site_result = check_and_open_website(user_input)
            if site_result:
                print(f"JARVIS: Fallback command executed: {site_result}")
                analysis['reply'] = f"{analysis.get('reply', '')} (Action: {site_result})".strip()
            else:
                # Direct deep link detection for common platforms
                import re
                
                # YouTube search fallback
                yt_match = re.search(r'youtube\s+(?:for|about|of)\s+(.+)', user_input.lower())
                if yt_match:
                    query = yt_match.group(1)
                    url = f"https://www.youtube.com/results?search_query={requests.utils.quote(query)}"
                    webbrowser.open(url)
                    analysis['reply'] = f"{analysis.get('reply', '')} (Searching YouTube for: {query})".strip()
                
                # LinkedIn search fallback
                li_match = re.search(r'linkedin\s+(?:profile|of|account)\s+(.+)', user_input.lower())
                if li_match:
                    name = li_match.group(1)
                    url = f"https://www.linkedin.com/search/results/all/?keywords={requests.utils.quote(name)}"
                    webbrowser.open(url)
                    analysis['reply'] = f"{analysis.get('reply', '')} (Searching LinkedIn for: {name})".strip()
                
                # Generic domain detection
                domain_match = re.search(r'open\s+([a-zA-Z0-9.-]+\.[a-z]{2,})', user_input.lower())
                if domain_match:
                    url = "https://" + domain_match.group(1)
                    webbrowser.open(url)
                    analysis['reply'] = f"{analysis.get('reply', '')} (Opening {url})".strip()

        return jsonify({
            'reply': analysis.get('reply'),
            'sentiment': analysis.get('sentiment', 'neutral'),
            'fraud_risk': analysis.get('fraud_risk', 'low'),
            'emotion': analysis.get('emotion', 'calm'),
            'command': command,
            'tool': 'llm_langgraph'
        })

    except Exception as e:
        print(f"Assistant error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat-history', methods=['GET'])
def get_chat_history():
    """Get chat history"""
    return jsonify(chat_history)

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear chat history"""
    global chat_history
    chat_history = []
    return jsonify({'status': 'History cleared'})

@app.route('/api/voice-profiles', methods=['GET'])
def get_profiles():
    """Get all voice profiles"""
    profiles = list(voice_profile_manager.profiles.keys())
    return jsonify({'profiles': profiles})

@app.route('/api/voice-profiles/create', methods=['POST'])
def create_profile():
    """Create a new voice profile"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        # Create profile (simplified - returns status)
        if username.lower() in [u.lower() for u in voice_profile_manager.profiles.keys()]:
            return jsonify({'error': f'User {username} already exists'}), 400
        
        # For web app, we'll store empty profile that can be trained later
        voice_profile_manager.profiles[username] = {
            "username": username,
            "created": datetime.now().isoformat(),
            "voice_samples": [],
            "average_features": {}
        }
        voice_profile_manager.save_profiles()
        
        return jsonify({'status': 'Profile created', 'username': username})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/voice-profiles/<username>', methods=['DELETE'])
def delete_profile(username):
    """Delete a voice profile"""
    try:
        if username in voice_profile_manager.profiles:
            del voice_profile_manager.profiles[username]
            voice_profile_manager.save_profiles()
            return jsonify({'status': 'Profile deleted'})
        else:
            return jsonify({'error': 'Profile not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/set-current-user', methods=['POST'])
def set_current_user():
    """Set the current user for personalization"""
    global current_user
    try:
        data = request.json
        username = data.get('username', '').strip()
        
        if username not in voice_profile_manager.profiles:
            return jsonify({'error': 'User not found'}), 404
        
        current_user = username
        greeting = voice_profile_manager.get_personalized_greeting(username)
        
        return jsonify({
            'status': 'User set',
            'username': username,
            'greeting': greeting
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhooks/whatsapp', methods=['GET', 'POST'])
def whatsapp_webhook():
    """Webhook for Meta WhatsApp Cloud API"""
    if request.method == 'GET':
        # Webhook Verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "jarvis_secret_token_123")
        
        if mode == 'subscribe' and token == verify_token:
            return challenge, 200
        return 'Verification failed', 403

    # Handle incoming messages (POST)
    try:
        data = request.json
        if not data:
            return jsonify({"status": "no data"}), 200

        # Meta sends a lot of notifications (read receipts, etc.), we only care about messages
        entry = data.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})
        messages = value.get('messages', [])

        if messages:
            message = messages[0]
            sender_id = message.get('from') # Phone number
            message_body = message.get('text', {}).get('body', '').lower()

            if message_body:
                # 1. Process with JARVIS Brain
                analysis = jarvis_brain.chat(sender_id, message_body)
                reply = analysis.get('reply', "Neural link interrupted.")

                # 2. Send reply via Meta Cloud API
                access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
                phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

                if access_token and phone_number_id:
                    url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
                    headers = {
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "messaging_product": "whatsapp",
                        "to": sender_id,
                        "type": "text",
                        "text": {"body": reply}
                    }
                    requests.post(url, headers=headers, json=payload)
                    print(f"JARVIS: Replied to WhatsApp {sender_id}")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"WhatsApp Webhook Error: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/api/simulator/whatsapp', methods=['POST'])
def whatsapp_simulator():
    """Simulator endpoint to test WhatsApp integration without real API keys"""
    try:
        data = request.json
        sender_id = data.get('from', '+1234567890')
        message_text = data.get('text', '')
        
        if not message_text:
            return jsonify({"error": "No text provided"}), 400
            
        reply = whatsapp_sim.handle_message(sender_id, message_text)
        return jsonify({
            "status": "simulated_success",
            "from": sender_id,
            "incoming": message_text,
            "reply": reply
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    """Get current user"""
    return jsonify({
        'current_user': current_user,
        'greeting': voice_profile_manager.get_personalized_greeting(current_user) if current_user else None
    })

@app.route('/api/wake-status', methods=['GET'])
def wake_status():
    """Check if wake word was detected"""
    return jsonify({'detected': wake_detector.check_wake()})

@app.route('/api/weather', methods=['GET'])
def weather():
    """Get weather for a city"""
    try:
        city = request.args.get('city', 'London')
        result = get_weather(city)
        return jsonify({'weather': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/define', methods=['GET'])
def define():
    """Get word definition"""
    try:
        word = request.args.get('word', '')
        if not word:
            return jsonify({'error': 'Word required'}), 400
        result = get_word_definition(word)
        return jsonify({'definition': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/joke', methods=['GET'])
def joke():
    """Get a joke"""
    try:
        result = tell_joke()
        return jsonify({'joke': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/news', methods=['GET'])
def news():
    """Get news"""
    try:
        category = request.args.get('category', 'general')
        result = get_news(category)
        return jsonify({'news': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """Calculate expression"""
    try:
        data = request.json
        expression = data.get('expression', '')
        if not expression:
            return jsonify({'error': 'Expression required'}), 400
        result = perform_calculation(expression)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_command(user_input):
    """Process user input through command handlers"""
    user_input = user_input.lower()
    
    # Check for help
    if "help" in user_input:
        return handle_help(user_input)
    
    # Check for website opening
    if "open" in user_input:
        result = check_and_open_website(user_input)
        if result:
            return result
    
    # Check for application opening
    if "open" in user_input or "launch" in user_input:
        result = open_application(user_input)
        if result:
            return result
    
    # Check for information requests
    if "time" in user_input or "date" in user_input:
        result = handle_information_request(user_input)
        if result:
            return result
    
    # Check for queries (weather, definitions, news)
    result = handle_queries(user_input)
    if result:
        return result
    
    # Check for entertainment (jokes)
    result = handle_entertainment(user_input)
    if result:
        return result
    
    # Check for calculations
    result = handle_calculation(user_input)
    if result:
        return result
    
    # Check for web search
    result = handle_search(user_input)
    if result:
        return result
    
    # Check for system commands
    system_reply, command_type = handle_system_commands(user_input)
    if system_reply:
        if command_type:
            execute_system_command(command_type)
        return system_reply
    
    # Default response
    return f"You said: {user_input}"

# ==================== GML Memory Layer API Endpoints ====================

@app.route('/api/memory/recall', methods=['POST'])
def memory_recall():
    """
    Recall memories based on query.
    POST data: {"query": "...", "recall_type": "all|entities|events"}
    """
    try:
        data = request.json
        query = data.get('query', '').strip()
        recall_type = data.get('recall_type', 'all')
        
        if not query:
            return jsonify({'error': 'Query required'}), 400
        
        result = gml.recall(query, recall_type)
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/memory/entity', methods=['POST'])
def memory_add_entity():
    """
    Add entity to GML memory.
    POST data: {"name": "...", "type": "person|place|concept", "attributes": {...}}
    """
    try:
        data = request.json
        name = data.get('name', '').strip()
        entity_type = data.get('type', 'concept')
        attributes = data.get('attributes', {})
        
        if not name:
            return jsonify({'error': 'Entity name required'}), 400
        
        entity_id = gml.add_entity(name, entity_type, attributes)
        return jsonify({
            'status': 'Entity added',
            'entity_id': entity_id,
            'name': name,
            'type': entity_type
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/memory/entity/<query>', methods=['GET'])
def memory_search_entity(query):
    """Search entities by semantic similarity"""
    try:
        results = gml.search_entities(query)
        entities = []
        for ent_id, similarity in results:
            entity = gml.get_entity(ent_id)
            if entity:
                entities.append({
                    'id': ent_id,
                    'name': entity.name,
                    'type': entity.type,
                    'similarity': similarity,
                    'attributes': entity.attributes
                })
        
        return jsonify({'query': query, 'entities': entities}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/memory/entity-info/<name>', methods=['GET'])
def memory_entity_info(name):
    """Get all information about a specific entity"""
    try:
        result = gml.recall_about_entity(name)
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/memory/relationship', methods=['POST'])
def memory_add_relationship():
    """
    Add relationship between entities.
    POST data: {"source_entity": "...", "target_entity": "...", 
                "relationship_type": "knows|likes|works_with|etc", 
                "context": "..."}
    """
    try:
        data = request.json
        source_name = data.get('source_entity', '').strip()
        target_name = data.get('target_entity', '').strip()
        rel_type = data.get('relationship_type', 'knows')
        context = data.get('context', '')
        
        if not source_name or not target_name:
            return jsonify({'error': 'Source and target entities required'}), 400
        
        # Find or create entities
        source_id = gml.find_entity(source_name)
        if not source_id:
            source_id = gml.add_entity(source_name, "person")
        
        target_id = gml.find_entity(target_name)
        if not target_id:
            target_id = gml.add_entity(target_name, "person")
        
        # Add relationship
        success = gml.add_relationship(source_id, target_id, rel_type, context)
        
        if success:
            return jsonify({
                'status': 'Relationship added',
                'source': source_name,
                'target': target_name,
                'type': rel_type
            }), 201
        else:
            return jsonify({'error': 'Failed to add relationship'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/memory/event', methods=['POST'])
def memory_log_event():
    """
    Log event to memory.
    POST data: {"description": "...", "entity_names": [...], "event_type": "interaction|..."}
    """
    try:
        data = request.json
        description = data.get('description', '').strip()
        entity_names = data.get('entity_names', [])
        event_type = data.get('event_type', 'interaction')
        
        if not description:
            return jsonify({'error': 'Event description required'}), 400
        
        # Find or create entities
        entity_ids = []
        for name in entity_names:
            ent_id = gml.find_entity(name)
            if not ent_id:
                ent_id = gml.add_entity(name, "person")
            entity_ids.append(ent_id)
        
        # Log event
        event_id = gml.log_event(description, entity_ids, event_type)
        gml.save_memory()
        
        return jsonify({
            'status': 'Event logged',
            'event_id': event_id,
            'description': description,
            'entities': entity_names
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/memory/stats', methods=['GET'])
def memory_stats():
    """Get memory statistics"""
    try:
        stats = gml.get_memory_stats()
        consolidation = gml.consolidate_memories()
        
        return jsonify({
            'statistics': stats,
            'consolidation': consolidation
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/memory/save', methods=['POST'])
def memory_save():
    """Manually save memory to disk"""
    try:
        success = gml.save_memory()
        if success:
            return jsonify({'status': 'Memory saved successfully'}), 200
        else:
            return jsonify({'error': 'Failed to save memory'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/memory/clear', methods=['POST'])
def memory_clear():
    """Clear all memories (use with caution)"""
    try:
        gml.clear_memory()
        return jsonify({'status': 'All memories cleared'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/analyze-emotion', methods=['POST'])
def analyze_emotion():
    """
    Analyze emotion from audio data
    Expects: multipart/form-data with 'audio' file
    """
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Read audio data
        audio_data = audio_file.read()
        audio_array = np.frombuffer(audio_data, np.int16)
        
        # Analyze emotion
        emotion_result = emotion_analyzer.analyze_emotion(audio_array)
        
        return jsonify(emotion_result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/emotion-tips', methods=['GET'])
def emotion_tips():
    """Get tips for a specific emotion"""
    emotion = request.args.get('emotion', 'calm')
    tips = emotion_analyzer.get_emotion_tips(emotion)
    
    return jsonify({
        'emotion': emotion,
        'tips': tips
    }), 200

@app.route('/api/emotion-summary', methods=['GET'])
def emotion_summary():
    """Get emotion pattern summary"""
    summary = emotion_analyzer.get_emotion_summary()
    return jsonify(summary), 200


# ==================== IoT API Endpoints (Simulated Smart Home) ====================

@app.route('/api/iot/devices', methods=['GET'])
def iot_list_devices():
    return jsonify({"devices": list(devices.values())}), 200


@app.route('/api/iot/device/<device_id>', methods=['PATCH'])
def iot_update_device(device_id: str):
    if device_id not in devices:
        return jsonify({"error": "Device not found"}), 404

    data = request.json or {}
    state_update = data.get("state")
    if not isinstance(state_update, dict):
        return jsonify({"error": "state must be an object"}), 400

    devices[device_id]["state"].update(state_update)
    return jsonify({"device": devices[device_id]}), 200


@app.route('/api/iot/command', methods=['POST'])
def iot_command():
    data = request.json or {}
    text = (data.get("text") or "").strip().lower()
    if not text:
        return jsonify({"error": "text required"}), 400

    def set_power(device_key: str, power: bool):
        if device_key in devices:
            devices[device_key]["state"]["power"] = power
            return True
        return False

    if "living room" in text and "light" in text:
        if "turn on" in text or "switch on" in text:
            set_power("living_room_light", True)
            return jsonify({"reply": "Turning on the living room light.", "devices": list(devices.values())}), 200
        if "turn off" in text or "switch off" in text:
            set_power("living_room_light", False)
            return jsonify({"reply": "Turning off the living room light.", "devices": list(devices.values())}), 200

    if "bedroom" in text and "light" in text:
        if "turn on" in text or "switch on" in text:
            set_power("bedroom_light", True)
            return jsonify({"reply": "Turning on the bedroom light.", "devices": list(devices.values())}), 200
        if "turn off" in text or "switch off" in text:
            set_power("bedroom_light", False)
            return jsonify({"reply": "Turning off the bedroom light.", "devices": list(devices.values())}), 200

    if "fan" in text:
        if "turn on" in text or "switch on" in text:
            set_power("fan", True)
            return jsonify({"reply": "Turning on the fan.", "devices": list(devices.values())}), 200
        if "turn off" in text or "switch off" in text:
            set_power("fan", False)
            return jsonify({"reply": "Turning off the fan.", "devices": list(devices.values())}), 200

    if "thermostat" in text or "temperature" in text:
        import re
        m = re.search(r"(\d{2})", text)
        if m:
            temp = int(m.group(1))
            devices["thermostat"]["state"]["temperature"] = temp
            return jsonify({"reply": f"Setting temperature to {temp}°C.", "devices": list(devices.values())}), 200

    if "lock" in text and "door" in text:
        if "lock" in text and "unlock" not in text:
            devices["door_lock"]["state"]["locked"] = True
            return jsonify({"reply": "Locking the door.", "devices": list(devices.values())}), 200
        if "unlock" in text:
            devices["door_lock"]["state"]["locked"] = False
            return jsonify({"reply": "Unlocking the door.", "devices": list(devices.values())}), 200

    if "status" in text or "devices" in text or "iot" in text:
        return jsonify({"reply": "Here are your devices.", "devices": list(devices.values())}), 200

    return jsonify({
        "reply": "I didn't understand that IoT command. Try: 'turn on living room light', 'set temperature to 22', 'lock the door'.",
        "devices": list(devices.values()),
    }), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
