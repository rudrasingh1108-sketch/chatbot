from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "Barebones system is live"})

@app.route('/api/wake-status', methods=['GET'])
def wake_status():
    return jsonify({"detected": False})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
