"""
Chatbot Web Application - Flask Backend
Provides REST API for the voice assistant chatbot
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime
from voice_profiles import VoiceProfile
from emotion_analyzer import EmotionAnalyzer
from gml import GigzsMemoryLayer
import speech_recognition as sr
import numpy as np

app = Flask(__name__)
CORS(app)

# Initialize managers
voice_profile_manager = VoiceProfile()
emotion_analyzer = EmotionAnalyzer()
gml = GigzsMemoryLayer()  # Initialize Gigzs Memory Layer

# Chat history storage
chat_history = []
current_user = None

# Import command handlers from main.py
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
    """Serve the main chatbot interface"""
    return render_template('index.html')

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

@app.route('/api/current-user', methods=['GET'])
def get_current_user():
    """Get current user"""
    return jsonify({
        'current_user': current_user,
        'greeting': voice_profile_manager.get_personalized_greeting(current_user) if current_user else None
    })

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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
