# Voice Assistant Web Application - Setup & Usage Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Flask & Flask-CORS
- NumPy
- All dependencies from `requirements.txt`

### 1. Install Web Application Dependencies

```bash
pip install flask flask-cors numpy
```

Or use the existing virtual environment:
```bash
cd c:\Users\rudra\OneDrive\Desktop\projects\chatbot
.\.venv\Scripts\activate
pip install flask flask-cors
```

### 2. Run the Web Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### 3. Access the Application

Open your browser and go to:
```
http://localhost:5000
```

---

## 📱 Web Application Features

### Chat Interface
- Clean, modern chat UI
- Real-time message exchange
- Message history
- Responsive design for all devices

### User Profile Management
- Create multiple voice profiles
- List all registered users
- Delete user profiles
- Quick user switching

### Quick Actions
- 🌤️ **Weather** - Get weather for any city
- 😂 **Joke** - Get random jokes
- 📰 **News** - Fetch latest news
- 📚 **Definition** - Look up word definitions
- ⏰ **Time** - Get current time & date

### Personalized Responses
- User selection dropdown
- Personalized greetings based on time of day
- Context-aware conversation history
- User-specific command tracking

---

## 🔌 API Endpoints

### Chat
- `POST /api/chat` - Send message and get response
- `GET /api/chat-history` - Get chat history
- `POST /api/clear-history` - Clear chat history

### Voice Profiles
- `GET /api/voice-profiles` - List all profiles
- `POST /api/voice-profiles/create` - Create new profile
- `DELETE /api/voice-profiles/<username>` - Delete profile
- `POST /api/set-current-user` - Switch to user
- `GET /api/current-user` - Get current user

### Features
- `GET /api/weather?city=London` - Get weather
- `GET /api/define?word=hello` - Get definition
- `GET /api/joke` - Get joke
- `GET /api/news?category=general` - Get news
- `GET /api/calculate` - Perform calculation

### Health
- `GET /api/health` - API health check

---

## 🎯 Usage Examples

### 1. Create a User Profile
1. Click "New Profile" button
2. Enter username (e.g., "Rudra")
3. Click "Create Profile"

### 2. Switch to a User
1. Select user from dropdown
2. Click "Set User"
3. Receive personalized greeting

### 3. Chat with Assistant
1. Type your message in the input field
2. Press Enter or click Send
3. Get instant response

### 4. Use Quick Actions
- Click any quick action button (Weather, Joke, News, etc.)
- For Weather: Enter city name and get weather data
- For Definition: Enter a word and get its definition
- For News: Get latest headlines
- For Time: See current time and date

### 5. Sample Commands
```
- "what is the weather in New York?"
- "tell me a joke"
- "define artificial intelligence"
- "what time is it?"
- "get latest news"
- "help"
```

---

## 🎨 UI Components

### Sidebar
- User Profile section
- Voice Profiles list
- Quick Actions buttons
- Settings (Clear History)

### Main Chat Area
- Welcome message with features
- Real-time chat messages
- Message input with Send button
- Voice input button (placeholder)

### Modals
- **Create Profile Modal** - Add new users
- **Weather Modal** - Check weather
- **Definition Modal** - Look up words

---

## 🔧 Configuration

### Change API Base URL
Edit `static/script.js`:
```javascript
const API_BASE = 'http://localhost:5000/api';
```

### Change Flask Port
Edit `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### Enable/Disable Debug Mode
In `app.py`:
```python
app.run(debug=True)  # Development
app.run(debug=False) # Production
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### CORS Issues
Ensure `flask-cors` is installed:
```bash
pip install flask-cors
```

### API Not Responding
1. Check Flask app is running
2. Verify localhost:5000 is accessible
3. Check browser console for errors (F12)

---

## 📂 File Structure

```
chatbot/
├── app.py                      # Flask backend
├── main.py                     # Chatbot core logic
├── voice_profiles.py           # Voice recognition system
├── requirements.txt            # Python dependencies
├── templates/
│   └── index.html             # Web interface
├── static/
│   ├── styles.css             # UI styling
│   ├── script.js              # Frontend logic
└── voice_profiles.json        # Stored user profiles
```

---

## 🚀 Deployment

### Local Network Access
```bash
python app.py
# Then access from other devices:
# http://<your-ip>:5000
```

### Production Deployment
Use Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📝 Notes

- Voice input feature is a placeholder in the web version
- Chat history is stored in memory (resets on server restart)
- Voice profiles are saved to `voice_profiles.json`
- All API responses are JSON format
- CORS is enabled for cross-origin requests

---

## 🎓 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [REST API Best Practices](https://restfulapi.net/)
- [JavaScript Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [CSS Grid & Flexbox](https://css-tricks.com/)

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Flask and JavaScript console for errors
3. Ensure all dependencies are installed
4. Test API endpoints directly via curl or Postman

---

**Version:** 1.0.0  
**Last Updated:** February 26, 2026  
**Status:** Ready for Use
