from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
# Enable CORS for all origins
CORS(app)

@app.route('/', methods=['GET'])
def root():
    return jsonify({"status": "online", "message": "JARVIS Root Access Granted"})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "Barebones system is live"})

@app.route('/api/wake-status', methods=['GET'])
def wake_status():
    return jsonify({"detected": False})

if __name__ == '__main__':
    # Render sets the PORT environment variable
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
