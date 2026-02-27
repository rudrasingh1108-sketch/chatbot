import requests
import os
from flask import Flask, request, jsonify

class WhatsAppSimulator:
    def __init__(self, brain):
        self.brain = brain
        print("\n[JARVIS WhatsApp Simulator Active]")
        print("To simulate an incoming message, use the following CURL command:")
        print("curl -X POST http://127.0.0.1:8080/api/simulator/whatsapp -H 'Content-Type: application/json' -d '{\"from\": \"+1234567890\", \"text\": \"Hello JARVIS\"}'\n")

    def handle_message(self, sender_id, text):
        print(f"\n[WhatsApp Received] From: {sender_id} | Message: {text}")
        analysis = self.brain.chat(sender_id, text)
        reply = analysis.get('reply', "Neural link interrupted.")
        print(f"[WhatsApp Reply] To: {sender_id} | Response: {reply}\n")
        return reply

# This class will be initialized in app.py
