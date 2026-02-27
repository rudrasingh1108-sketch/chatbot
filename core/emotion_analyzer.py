"""
Emotion-Aware AI Analysis Module
Analyzes voice characteristics to detect emotional states
Features: pitch, speed, pauses, tone, energy
"""

import numpy as np
import json
import os
from datetime import datetime


class EmotionAnalyzer:
    """
    Analyzes audio for emotional indicators.
    
    Detects:
    - Stress (high pitch, fast speech, short pauses)
    - Confidence (steady pitch, moderate speed, longer pauses)
    - Nervousness (fluctuating pitch, variable speed, frequent pauses)
    - Excitement (high pitch, variable speed, shorter pauses)
    """
    
    def __init__(self):
        """Initialize emotion analyzer with thresholds"""
        self.emotion_history_file = "emotion_history.json"
        self.emotion_history = self._load_history()
        
        # Emotional state thresholds
        self.thresholds = {
            "pitch_high": 250,        # Hz (high pitch indicator)
            "pitch_low": 80,          # Hz (low pitch indicator)
            "pitch_variance": 30,     # Hz (pitch variation)
            "speed_fast": 5.5,        # words per second
            "speed_slow": 3.0,        # words per second
            "pause_long": 0.8,        # seconds
            "pause_short": 0.1,       # seconds
            "energy_high": 0.3,       # normalized energy
            "energy_low": 0.05,       # normalized energy
        }
        
        # Emotion base scores
        self.emotions = {
            "stress": {"description": "Stressed", "suggestions": ["relaxation music", "deep breathing"]},
            "confidence": {"description": "Confident", "suggestions": ["encouraging statements"]},
            "nervousness": {"description": "Nervous", "suggestions": ["reassurance", "calming music"]},
            "excitement": {"description": "Excited", "suggestions": ["motivating messages"]},
            "sadness": {"description": "Sad", "suggestions": ["uplifting music", "positive affirmation"]},
            "calm": {"description": "Calm", "suggestions": ["normal assistance"]},
        }
    
    def analyze_emotion(self, audio_data, sample_rate=16000):
        """
        Analyze audio data for emotional indicators.
        
        Args:
            audio_data: numpy array of audio samples
            sample_rate: sample rate in Hz (default 16000)
        
        Returns:
            dict with emotion_state, confidence_scores, and suggestions
        """
        try:
            if len(audio_data) < sample_rate:
                return {
                    "emotional_state": "unknown",
                    "confidence": 0.0,
                    "message": "Audio too short to analyze emotion",
                    "scores": {},
                }
            
            # Extract audio features
            features = self._extract_features(audio_data, sample_rate)
            
            # Classify emotion based on features
            emotion_scores = self._classify_emotion(features)
            
            # Determine primary emotion
            primary_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = emotion_scores[primary_emotion]
            
            # Generate contextual message
            message = self._generate_message(primary_emotion, features)
            
            # Get suggestions
            suggestions = self.emotions[primary_emotion]["suggestions"]
            
            # Store in history
            self._save_emotion_record(primary_emotion, confidence, features)
            
            return {
                "emotional_state": primary_emotion,
                "description": self.emotions[primary_emotion]["description"],
                "confidence": round(confidence, 3),
                "scores": {k: round(v, 3) for k, v in emotion_scores.items()},
                "features": {
                    "pitch_hz": round(features["pitch"], 1),
                    "pitch_variance": round(features["pitch_variance"], 1),
                    "speaking_speed_wps": round(features["speaking_speed"], 2),
                    "avg_pause_duration": round(features["avg_pause"], 3),
                    "energy_level": round(features["energy"], 3),
                    "voice_stability": round(features["stability"], 3),
                },
                "message": message,
                "suggestions": suggestions,
            }
        
        except Exception as e:
            return {
                "emotional_state": "error",
                "confidence": 0.0,
                "message": f"Emotion analysis error: {str(e)}",
                "scores": {},
            }
    
    def _extract_features(self, audio_data, sample_rate):
        """
        Extract emotional indicators from audio.
        
        Returns:
            dict with features: pitch, pitch_variance, speaking_speed,
                               avg_pause, energy, stability
        """
        features = {}
        
        # 1. PITCH ANALYSIS (Fundamental Frequency)
        features["pitch"], features["pitch_variance"] = self._analyze_pitch(
            audio_data, sample_rate
        )
        
        # 2. SPEAKING SPEED
        features["speaking_speed"] = self._analyze_speaking_speed(
            audio_data, sample_rate
        )
        
        # 3. PAUSE ANALYSIS
        features["avg_pause"] = self._analyze_pauses(audio_data, sample_rate)
        
        # 4. ENERGY ANALYSIS (Volume/Intensity)
        features["energy"] = self._analyze_energy(audio_data)
        
        # 5. VOICE STABILITY (Consistency)
        features["stability"] = self._analyze_stability(audio_data, sample_rate)
        
        return features
    
    def _analyze_pitch(self, audio_data, sample_rate):
        """
        Estimate fundamental frequency (pitch) using autocorrelation method.
        
        Returns:
            tuple: (avg_pitch_hz, pitch_variance)
        """
        try:
            # Normalize audio
            audio_normalized = audio_data.astype(float) / (np.max(np.abs(audio_data)) + 1e-10)
            
            # Use autocorrelation for pitch detection
            frame_length = int(0.025 * sample_rate)  # 25ms frames
            hop_length = int(0.010 * sample_rate)    # 10ms step
            
            pitches = []
            
            for i in range(0, len(audio_normalized) - frame_length, hop_length):
                frame = audio_normalized[i : i + frame_length]
                
                # Apply window
                window = np.hanning(len(frame))
                frame = frame * window
                
                # Autocorrelation
                autocorr = np.correlate(frame, frame, mode="full")
                autocorr = autocorr[len(autocorr) // 2 :]
                
                # Find peaks in autocorrelation
                if len(autocorr) > 0:
                    # Look for pitch in range 80-400 Hz
                    min_lag = int(sample_rate / 400)  # 400 Hz max
                    max_lag = int(sample_rate / 80)   # 80 Hz min
                    
                    if max_lag < len(autocorr):
                        region = autocorr[min_lag:max_lag]
                        if len(region) > 0 and np.max(region) > 0:
                            lag = np.argmax(region) + min_lag
                            pitch = sample_rate / lag
                            
                            # Only accept reasonable pitches
                            if 80 <= pitch <= 400:
                                pitches.append(pitch)
            
            if len(pitches) > 0:
                avg_pitch = np.mean(pitches)
                pitch_variance = np.std(pitches)
            else:
                avg_pitch = 150  # Default to neutral pitch
                pitch_variance = 0
            
            return avg_pitch, pitch_variance
        
        except Exception as e:
            print(f"Pitch analysis error: {e}")
            return 150, 0
    
    def _analyze_speaking_speed(self, audio_data, sample_rate, num_phonemes=None):
        """
        Estimate speaking speed (words per second) by analyzing voice activity.
        
        Uses energy-based voice activity detection.
        
        Returns:
            float: Estimated words per second
        """
        try:
            # Normalize
            audio_normalized = audio_data.astype(float) / (np.max(np.abs(audio_data)) + 1e-10)
            
            # Voice activity detection using energy
            frame_length = int(0.025 * sample_rate)
            hop_length = int(0.010 * sample_rate)
            
            voice_frames = 0
            total_frames = 0
            
            for i in range(0, len(audio_normalized) - frame_length, hop_length):
                frame = audio_normalized[i : i + frame_length]
                energy = np.sum(frame ** 2) / len(frame)
                
                total_frames += 1
                if energy > 0.01:  # Voice activity threshold
                    voice_frames += 1
            
            # Calculate speaking rate based on voice activity
            if total_frames > 0:
                voice_ratio = voice_frames / total_frames
                total_duration = len(audio_data) / sample_rate
                voice_duration = total_duration * voice_ratio
                
                # Estimate speaking speed (typical: 3-5 words/sec)
                # Based on voice activity percentage
                if voice_duration > 0:
                    speaking_speed = 4.0 * (voice_ratio * 1.5)  # Adjusted estimation
                    speaking_speed = np.clip(speaking_speed, 0.5, 8.0)
                else:
                    speaking_speed = 0
            else:
                speaking_speed = 0
            
            return speaking_speed
        
        except Exception as e:
            print(f"Speaking speed analysis error: {e}")
            return 4.0  # Default speed
    
    def _analyze_pauses(self, audio_data, sample_rate):
        """
        Analyze pause patterns (silence detection).
        
        Returns:
            float: Average pause duration in seconds
        """
        try:
            # Normalize
            audio_normalized = audio_data.astype(float) / (np.max(np.abs(audio_data)) + 1e-10)
            
            # Silence detection with energy threshold
            frame_length = int(0.025 * sample_rate)
            hop_length = int(0.010 * sample_rate)
            
            silence_frames = 0
            pause_count = 0
            pause_durations = []
            in_pause = False
            pause_start = 0
            
            for i in range(0, len(audio_normalized) - frame_length, hop_length):
                frame = audio_normalized[i : i + frame_length]
                energy = np.sum(frame ** 2) / len(frame)
                
                if energy < 0.01:  # Silence threshold
                    silence_frames += 1
                    if not in_pause:
                        in_pause = True
                        pause_start = i / sample_rate
                else:
                    if in_pause:
                        pause_duration = (i / sample_rate) - pause_start
                        if pause_duration > 0.05:  # Only count pauses > 50ms
                            pause_durations.append(pause_duration)
                            pause_count += 1
                        in_pause = False
            
            # Calculate average pause
            if len(pause_durations) > 0:
                avg_pause = np.mean(pause_durations)
            else:
                avg_pause = 0.1  # No significant pauses
            
            return avg_pause
        
        except Exception as e:
            print(f"Pause analysis error: {e}")
            return 0.1
    
    def _analyze_energy(self, audio_data):
        """
        Analyze overall energy/loudness level.
        
        Returns:
            float: Normalized energy (0-1)
        """
        try:
            # RMS energy
            energy = np.sqrt(np.mean(audio_data.astype(float) ** 2))
            
            # Normalize to 0-1 range
            # Typical audio data range is 0-32768 for 16-bit
            max_possible = 32768
            normalized_energy = min(energy / max_possible, 1.0)
            
            return normalized_energy
        
        except Exception:
            return 0.1
    
    def _analyze_stability(self, audio_data, sample_rate):
        """
        Analyze voice stability (consistency of speech).
        
        Returns:
            float: Stability score (0-1, higher = more stable/confident)
        """
        try:
            # Normalize
            audio_normalized = audio_data.astype(float) / (np.max(np.abs(audio_data)) + 1e-10)
            
            # Analyze frequency content consistency
            frame_length = int(0.025 * sample_rate)
            hop_length = int(0.010 * sample_rate)
            
            freq_variations = []
            
            for i in range(0, len(audio_normalized) - frame_length, hop_length):
                frame = audio_normalized[i : i + frame_length]
                fft = np.fft.fft(frame)
                freq_magnitude = np.abs(fft[: len(fft) // 2])
                
                if len(freq_variations) > 0:
                    # Compare with previous frame
                    prev_freq = freq_variations[-1]
                    variation = np.mean(np.abs(freq_magnitude - prev_freq))
                    freq_variations.append(variation)
                
                freq_variations.append(freq_magnitude)
            
            # Lower variation = higher stability
            if len(freq_variations) > 1:
                avg_variation = np.mean(freq_variations[::2])  # Every other is variation
                # Normalize to 0-1 (inverse relationship)
                stability = 1.0 - np.clip(avg_variation, 0, 1)
            else:
                stability = 0.5
            
            return stability
        
        except Exception:
            return 0.5
    
    def _classify_emotion(self, features):
        """
        Classify emotion based on extracted features.
        
        Returns:
            dict: Emotion scores
        """
        scores = {
            "stress": 0.0,
            "confidence": 0.0,
            "nervousness": 0.0,
            "excitement": 0.0,
            "sadness": 0.0,
            "calm": 0.0,
        }
        
        pitch = features["pitch"]
        pitch_var = features["pitch_variance"]
        speed = features["speaking_speed"]
        pause = features["avg_pause"]
        energy = features["energy"]
        stability = features["stability"]
        
        t = self.thresholds
        
        # STRESS: High pitch + Fast speed + Short pauses + High energy
        stress_score = 0
        if pitch > t["pitch_high"]:
            stress_score += 0.25
        if speed > t["speed_fast"]:
            stress_score += 0.25
        if pause < t["pause_short"]:
            stress_score += 0.25
        if energy > t["energy_high"]:
            stress_score += 0.25
        scores["stress"] = min(stress_score, 1.0)
        
        # CONFIDENCE: Steady pitch + Moderate speed + Longer pauses + Stable
        confidence_score = 0
        if pitch_var < 20:  # Steady pitch
            confidence_score += 0.2
        if t["speed_slow"] <= speed <= t["speed_fast"]:
            confidence_score += 0.2
        if pause > t["pause_long"]:
            confidence_score += 0.2
        if stability > 0.7:
            confidence_score += 0.2
        if 0.1 <= energy <= 0.4:
            confidence_score += 0.2
        scores["confidence"] = min(confidence_score, 1.0)
        
        # NERVOUSNESS: Fluctuating pitch + Variable speed + Frequent pauses
        nervousness_score = 0
        if pitch_var > t["pitch_variance"]:
            nervousness_score += 0.33
        if speed < t["speed_slow"] or speed > t["speed_fast"]:
            nervousness_score += 0.33
        if pause < t["pause_short"]:
            nervousness_score += 0.34
        scores["nervousness"] = min(nervousness_score, 1.0)
        
        # EXCITEMENT: High pitch + Variable speed + Short pauses + High energy
        excitement_score = 0
        if pitch > t["pitch_high"]:
            excitement_score += 0.2
        if speed > t["speed_fast"]:
            excitement_score += 0.2
        if pause < t["pause_short"]:
            excitement_score += 0.2
        if energy > t["energy_high"]:
            excitement_score += 0.2
        if stability < 0.5:  # More variation = excitement
            excitement_score += 0.2
        scores["excitement"] = min(excitement_score, 1.0)
        
        # SADNESS: Low pitch + Slow speech + Longer pauses + Low energy
        sadness_score = 0
        if pitch < t["pitch_low"]:
            sadness_score += 0.25
        if speed < t["speed_slow"]:
            sadness_score += 0.25
        if pause > t["pause_long"]:
            sadness_score += 0.25
        if energy < t["energy_low"]:
            sadness_score += 0.25
        scores["sadness"] = min(sadness_score, 1.0)
        
        # CALM: Moderate pitch + Moderate speed + Consistent + Average energy
        calm_score = 0
        if t["pitch_low"] < pitch < t["pitch_high"]:
            calm_score += 0.15
        if t["speed_slow"] <= speed <= t["speed_fast"]:
            calm_score += 0.15
        if pitch_var < 25:
            calm_score += 0.15
        if pause > 0.2:
            calm_score += 0.15
        if stability > 0.6:
            calm_score += 0.15
        if 0.08 <= energy <= 0.35:
            calm_score += 0.25
        scores["calm"] = min(calm_score, 1.0)
        
        # Normalize scores so they sum to ~1
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        
        return scores
    
    def _generate_message(self, emotion, features):
        """
        Generate contextual message based on detected emotion.
        
        Returns:
            str: Personalized message
        """
        messages = {
            "stress": "I notice you sound a bit stressed right now. Heavy pitch, fast pace, and short pauses detected. Would you like to take a break or need some calming music?",
            "confidence": "You sound quite confident! Steady voice, good pacing, and thoughtful pauses. Keep going!",
            "nervousness": "I sense some nervousness - your pitch is varying and pauses are frequent. That's perfectly normal! I'm here to help.",
            "excitement": "Wow, you sound excited! High pitch, energetic pace - that's great enthusiasm! What's got you so pumped up?",
            "sadness": "I'm picking up some sadness in your voice - lower pitch and slower pace. Are you okay? Want to talk about it?",
            "calm": "You sound calm and collected right now. Your voice is steady and well-paced. Feeling good?",
        }
        
        return messages.get(emotion, "Analyzing your emotional state...")
    
    def _save_emotion_record(self, emotion, confidence, features):
        """Save emotion record to history for tracking patterns."""
        try:
            record = {
                "timestamp": datetime.now().isoformat(),
                "emotion": emotion,
                "confidence": float(confidence),
                "pitch": float(features["pitch"]),
                "speaking_speed": float(features["speaking_speed"]),
                "pause_duration": float(features["avg_pause"]),
                "energy": float(features["energy"]),
            }
            
            self.emotion_history.append(record)
            
            # Keep only last 100 records
            if len(self.emotion_history) > 100:
                self.emotion_history = self.emotion_history[-100:]
            
            # Save to file
            with open(self.emotion_history_file, "w") as f:
                json.dump(self.emotion_history, f, indent=2)
        
        except Exception as e:
            print(f"Error saving emotion record: {e}")
    
    def _load_history(self):
        """Load emotion history from file."""
        try:
            if os.path.exists(self.emotion_history_file):
                with open(self.emotion_history_file, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        
        return []
    
    def get_emotion_summary(self):
        """
        Get summary of recent emotional patterns.
        
        Returns:
            dict: Summary of emotions over time
        """
        if not self.emotion_history:
            return {"message": "No emotion history yet"}
        
        emotions_list = [record["emotion"] for record in self.emotion_history[-20:]]
        emotion_counts = {}
        
        for emotion in emotions_list:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        most_common = max(emotion_counts, key=emotion_counts.get)
        
        return {
            "total_records": len(self.emotion_history),
            "recent_emotions": emotion_counts,
            "most_common": most_common,
            "total_sessions": len(set(r["timestamp"][:10] for r in self.emotion_history)),
        }
    
    def get_emotion_tips(self, emotion):
        """
        Get tips for handling specific emotional state.
        
        Returns:
            list: Helpful suggestions
        """
        tips = {
            "stress": [
                "Try deep breathing exercises (4-7-8 technique)",
                "Take a 5-minute break away from screen",
                "Listen to calming music (lo-fi, ambient)",
                "Go for a short walk",
                "Drink some water or tea",
            ],
            "confidence": [
                "You're doing great! Keep this momentum",
                "This is a perfect time to tackle challenging tasks",
                "Consider taking on that project you were considering",
            ],
            "nervousness": [
                "That's normal! Everyone feels this way sometimes",
                "Try grounding techniques (5-4-3-2-1 senses)",
                "Remember past successes to boost confidence",
                "Talk it out - sometimes speaking helps",
                "Take some deep breaths",
            ],
            "excitement": [
                "Channel this energy into productive work",
                "Great time to brainstorm new ideas",
                "Share your enthusiasm with others",
                "Use this momentum to accomplish goals",
            ],
            "sadness": [
                "It's okay to feel sad sometimes",
                "Try uplifting music or content",
                "Reach out to someone you trust",
                "Engage in activities you enjoy",
                "Consider some light exercise",
            ],
            "calm": [
                "You're in a great mental space",
                "Perfect time for focused, detailed work",
                "Good moment for creative thinking",
                "Consider mentoring or helping others",
            ],
        }
        
        return tips.get(emotion, ["Take care of yourself!"])
