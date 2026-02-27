import os
import threading
import time
import numpy as np
import openwakeword
from openwakeword.model import Model
import sounddevice as sd
from dotenv import load_dotenv

class WakeWordDetector:
    def __init__(self):
        load_dotenv(override=True)
        # No API key needed for openwakeword
        self.model = None
        self.is_running = False
        self.thread = None
        self.wake_detected = False
        self.sample_rate = 16000
        self.chunk_size = 1280 # openwakeword expects 1280 samples (80ms at 16kHz)

    def _init_model(self):
        try:
            # Initialize openwakeword model with 'alexa' or 'hey_jarvis' if available
            # For now, using 'alexa' as it's a standard pre-trained model in openwakeword
            # We can also point to custom .onnx files if needed
            self.model = Model(wakeword_models=["alexa"], inference_framework="onnx")
            return True
        except Exception as e:
            print(f"Error initializing OpenWakeWord: {e}")
            return False

    def start(self):
        if self.is_running:
            return
        if not self._init_model():
            return

        self.is_running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("Wake word detector started (listening for 'Alexa' - OpenWakeWord)...")

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join()
        self.model = None

    def _loop(self):
        try:
            def callback(indata, frames, time, status):
                if status:
                    print(status)
                
                # Process audio chunk
                # openwakeword expects (N, 1280) chunks
                self.model.predict(indata[:, 0])
                
                # Check prediction for 'alexa'
                for md in self.model.prediction_buffer.keys():
                    if self.model.prediction_buffer[md][-1] > 0.5: # Threshold 0.5
                        print(f"Wake word '{md}' detected!")
                        self.wake_detected = True

            with sd.InputStream(samplerate=self.sample_rate, 
                              channels=1, 
                              blocksize=self.chunk_size, 
                              callback=callback):
                while self.is_running:
                    sd.sleep(100)
                    
        except Exception as e:
            print(f"Wake word loop error: {e}")
            self.is_running = False

    def check_wake(self):
        """Check if wake word was detected and reset the flag"""
        if self.wake_detected:
            self.wake_detected = False
            return True
        return False
