"""
Voice Profile Management System
Handles voice profile training, storage, and speaker identification
"""

import os
import json
import numpy as np
from datetime import datetime
import speech_recognition as sr

PROFILES_FILE = "voice_profiles.json"

class VoiceProfile:
    """Manages user voice profiles for speaker recognition"""
    
    def __init__(self):
        self.profiles = self.load_profiles()
        self.current_user = None
        
    def load_profiles(self):
        """Load existing voice profiles from file"""
        if os.path.exists(PROFILES_FILE):
            try:
                with open(PROFILES_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading profiles: {e}")
                return {}
        return {}
    
    def save_profiles(self):
        """Save profiles to file"""
        try:
            with open(PROFILES_FILE, 'w') as f:
                json.dump(self.profiles, f, indent=2)
            print("Voice profiles saved successfully.")
        except Exception as e:
            print(f"Error saving profiles: {e}")
    
    def create_profile(self, username, num_samples=3):
        """Create a new voice profile for a user"""
        if username.lower() in [u.lower() for u in self.profiles.keys()]:
            return f"User {username} already exists. Please use a different name."
        
        recognizer = sr.Recognizer()
        voice_samples = []
        
        print(f"\n=== Creating voice profile for {username} ===")
        print(f"Please record {num_samples} voice samples.")
        print("Say a short phrase like 'hello assistant' for each sample.\n")
        
        for i in range(num_samples):
            try:
                with sr.Microphone() as source:
                    print(f"Sample {i+1}/{num_samples}: Say something...")
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    
                    # Extract audio features (simple approach)
                    audio_data = np.frombuffer(audio.get_raw_data(), np.int16)
                    features = self._extract_features(audio_data)
                    voice_samples.append(features)
                    print(f"Sample {i+1} recorded successfully.")
            except Exception as e:
                print(f"Error recording sample {i+1}: {e}")
                return f"Failed to create profile for {username}"
        
        # Store profile with average features
        profile_data = {
            "username": username,
            "created": datetime.now().isoformat(),
            "voice_samples": voice_samples,
            "average_features": self._compute_average_features(voice_samples)
        }
        
        self.profiles[username] = profile_data
        self.save_profiles()
        return f"Voice profile created successfully for {username}!"
    
    def identify_speaker(self, recognizer, source, threshold=0.75):
        """Identify speaker from voice input"""
        try:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening for speaker identification...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            audio_data = np.frombuffer(audio.get_raw_data(), np.int16)
            input_features = self._extract_features(audio_data)
            
            best_match = None
            best_score = 0
            
            for username, profile in self.profiles.items():
                similarity = self._compute_similarity(
                    input_features, 
                    profile["average_features"]
                )
                
                if similarity > best_score:
                    best_score = similarity
                    best_match = username
            
            if best_score >= threshold:
                self.current_user = best_match
                return best_match, best_score
            else:
                return None, best_score
        
        except Exception as e:
            print(f"Error identifying speaker: {e}")
            return None, 0
    
    def _extract_features(self, audio_data):
        """Extract simple audio features for comparison"""
        try:
            # Normalize audio
            audio_data = audio_data.astype(np.float32)
            audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Extract basic features
            features = {
                "mean": float(np.mean(audio_data)),
                "std": float(np.std(audio_data)),
                "max": float(np.max(audio_data)),
                "min": float(np.min(audio_data)),
                "energy": float(np.sum(audio_data ** 2)),
                "zero_crossing_rate": float(np.mean(np.abs(np.diff(np.sign(audio_data))))), 
                "length": len(audio_data)
            }
            return features
        except Exception as e:
            print(f"Error extracting features: {e}")
            return {
                "mean": 0, "std": 0, "max": 0, "min": 0, 
                "energy": 0, "zero_crossing_rate": 0, "length": 0
            }
    
    def _compute_average_features(self, samples):
        """Compute average features from multiple samples"""
        if not samples:
            return {}
        
        avg_features = {}
        for key in samples[0].keys():
            avg_features[key] = np.mean([s[key] for s in samples])
        return avg_features
    
    def _compute_similarity(self, features1, features2):
        """Compute similarity between two feature sets (0-1 scale)"""
        try:
            if not features1 or not features2:
                return 0
            
            # Normalize and compare
            differences = []
            for key in features1.keys():
                if key in features2:
                    f1 = features1[key]
                    f2 = features2[key]
                    
                    # Handle division by zero
                    if f2 != 0:
                        diff = abs(f1 - f2) / (abs(f2) + 1e-6)
                    else:
                        diff = abs(f1 - f2)
                    
                    differences.append(diff)
            
            if not differences:
                return 0
            
            # Similarity inversely proportional to average difference
            avg_diff = np.mean(differences)
            similarity = max(0, 1 - avg_diff)
            return float(similarity)
        except Exception as e:
            print(f"Error computing similarity: {e}")
            return 0
    
    def list_users(self):
        """List all registered voice profiles"""
        if not self.profiles:
            return "No voice profiles registered."
        
        users = list(self.profiles.keys())
        return f"Registered users: {', '.join(users)}"
    
    def delete_profile(self, username):
        """Delete a voice profile"""
        if username in self.profiles:
            del self.profiles[username]
            self.save_profiles()
            return f"Profile for {username} deleted."
        return f"Profile for {username} not found."
    
    def get_personalized_greeting(self, username):
        """Get a personalized greeting for the user"""
        greetings = {
            "default": f"Hello {username}! How can I help you today?",
            "morning": f"Good morning {username}! Ready to start your day?",
            "afternoon": f"Good afternoon {username}! What can I do for you?",
            "evening": f"Good evening {username}! Need anything?"
        }
        
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return greetings["morning"]
        elif 12 <= hour < 17:
            return greetings["afternoon"]
        elif 17 <= hour < 21:
            return greetings["evening"]
        else:
            return greetings["default"]
