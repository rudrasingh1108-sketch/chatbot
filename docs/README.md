# 🤖 AI Voice Chatbot

A smart voice assistant that understands and responds to voice commands with multiple features including web browsing, system control, weather information, news, and more.

## ✨ Features

### 🌐 Website Control
- Open YouTube, Google, GitHub, Gmail, and more
- Command: *"Open [website name]"*

### 🖥️ Application Launcher
- Launch applications like Notepad, Calculator, Explorer, Paint
- Command: *"Open [app name]"*

### ⚙️ System Control
- Shutdown, Restart, Sleep, Lock computer
- Command: *"Shutdown"*, *"Restart"*, *"Lock"*, *"Sleep"*

### 🕐 Information Queries
- Get current time and date
- Check weather in any city
- Get word definitions
- Commands: *"What time is it?"*, *"What's the weather in Paris?"*, *"Define python"*

### 📰 News Headlines
- Get latest news by category
- Command: *"Technology news"*, *"Business news"*, *"Sports news"*

### 😂 Entertainment
- Tell jokes
- Command: *"Tell me a joke"*

### 🧮 Calculations
- Perform mathematical operations
- Command: *"What is 5 plus 3?"*, *"Calculate 10 times 2"*

### 🔍 Web Search
- Search Google for anything
- Command: *"Search for Python tutorials"*, *"Google machine learning"*

---

## 🚀 Quick Start

### Option 1: Using GUI Launcher (Recommended - Easiest)

1. **Double-click** `launch.bat`
2. Click **START CHATBOT** button
3. Say *"Hey Assistant"* to activate
4. Give voice commands

### Option 2: Using Web Application (NEW! 🌐)

1. **Install Web Dependencies**:
   ```bash
   pip install flask flask-cors
   ```

2. **Start Web Server**:
   ```bash
   python app.py
   ```

3. **Access in Browser**:
   - Go to: `http://localhost:5000`
   - Create user profiles
   - Chat via text interface
   - Use quick action buttons

### Option 3: Command Line Setup

1. **Install Dependencies** (First time only):
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup API Key** (Optional, for news feature):
   - Go to https://newsapi.org/
   - Sign up for free account
   - Copy your API key
   - Open `gui_launcher.py` and enter the key in settings, OR
   - Edit `main.py` line 48: replace `NEWS_API_KEY = "demo"` with your key

3. **Run the Chatbot**:
   - Option A: Double-click `launch.bat`
   - Option B: Run in terminal: `python main.py`
   - Option C: Use GUI Launcher: `python gui_launcher.py`

---

## 🌐 Web Application (NEW!)

### Features
- **Modern Chat Interface** - Clean, responsive web design
- **User Profile Management** - Create and manage multiple user profiles
- **Voice Profile Switching** - Quick user selection and personalized greetings
- **Quick Actions** - Fast access to Weather, News, Jokes, Definitions, Time
- **Chat History** - View and clear previous conversations
- **Real-time Responses** - Instant replies to user queries

### Quick Start
```bash
# Install dependencies
pip install flask flask-cors

# Start the web server
python app.py

# Open browser
# http://localhost:5000
```

### Web App Usage
1. **Create Profile**: Click "New Profile" → Enter username
2. **Select User**: Choose from dropdown → Click "Set User"
3. **Chat**: Type message → Press Enter or click Send
4. **Quick Actions**: Click Weather, Joke, News, Definition, or Time buttons
5. **Clear History**: Click "Clear History" to reset chat

### API Endpoints
- `POST /api/chat` - Send message
- `GET /api/voice-profiles` - List profiles
- `POST /api/voice-profiles/create` - Create profile
- `DELETE /api/voice-profiles/<username>` - Delete profile
- `GET /api/weather?city=City` - Get weather
- `GET /api/define?word=Word` - Get definition
- `GET /api/joke` - Get joke
- `GET /api/news?category=general` - Get news

For detailed web app documentation, see [WEB_APP_GUIDE.md](WEB_APP_GUIDE.md)

---

- **Python** 3.7 or higher
- **Windows** OS (currently Windows-optimized)
- **Microphone** (for voice input)
- **Internet Connection** (for weather, news, definitions)

---

## 🎤 Example Commands

### Websites
```
"Open YouTube"
"Open Google"
"Open GitHub"
"Open Gmail"
```

### Applications
```
"Open Notepad"
"Open Calculator"
"Open File Explorer"
"Open Task Manager"
```

### Information
```
"What time is it?"
"What's the date?"
"What's the weather?"
"Weather in New York"
"Define machine learning"
```

### News
```
"News"
"Technology news"
"Business headlines"
"Sports news"
```

### Entertainment & Calculations
```
"Tell me a joke"
"What is 10 plus 5?"
"Calculate 100 divided by 2"
```

### Search
```
"Search for Python tutorials"
"Google machine learning"
```

### Help
```
"Help"
"What can you do?"
```

---

## ⚙️ Configuration

### Set News API Key

**Method 1: Using GUI Launcher** (Recommended)
1. Click **START CHATBOT** in launcher
2. Enter your key in "Settings" section
3. Click **Save API Key**

**Method 2: Direct Edit**
1. Open `main.py`
2. Find line 48: `NEWS_API_KEY = "demo"`
3. Replace with: `NEWS_API_KEY = "your_api_key_here"`

---

## 🔧 Troubleshooting

### "Python is not installed"
- Install Python from https://www.python.org/
- Make sure to check **"Add Python to PATH"** during installation

### "No module named 'speech_recognition'"
- Run: `pip install -r requirements.txt`

### "Microphone not working"
- Check Windows Settings → Privacy & Security → Microphone
- Make sure microphone is enabled
- Test microphone in Sound Settings

### "No audio output after greeting"
- Check speaker volume
- Test audio in Windows Settings
- Reinstall `pyttsx3`: `pip install --upgrade pyttsx3`

### "News not working"
- Get free API key from https://newsapi.org/
- Update API key in settings (see Configuration section)

### "Wake word not detected"
- Speak clearly "Hey Assistant" or "Hey Bot"
- Check microphone is working
- Reduce background noise

---

## 📁 File Structure

```
chatbot/
├── main.py                     # Main chatbot script (voice)
├── app.py                      # Flask web application backend
├── gui_launcher.py             # GUI launcher interface
├── voice_profiles.py           # Voice recognition system
├── launch.bat                  # Quick launch batch file
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── WEB_APP_GUIDE.md           # Web app documentation
├── templates/
│   └── index.html             # Web interface
├── static/
│   ├── styles.css             # Web UI styling
│   ├── script.js              # Frontend logic
└── voice_profiles.json        # Stored user profiles
```

---

## 🔐 Privacy & Security

- All voice data is processed locally via Google Speech Recognition
- API keys are stored in `config.txt` (keep this file private)
- No personal data is stored or transmitted beyond API calls

---

## 📝 License

Free to use for personal projects

---

## 💡 Tips for Best Performance

1. **Speak Clearly** - The bot understands better with clear speech
2. **Reduce Background Noise** - Quieter environment = better accuracy
3. **Use Complete Sentences** - Say "Open YouTube" instead of just "YouTube"
4. **Wait for Prompt** - Wait for "What can I do for you?" before giving commands
5. **Restart if Issues** - Close and reopen if problems occur

---

## 🐛 Reporting Issues

If you encounter issues:
1. Check the Status window in GUI Launcher
2. Verify microphone is working
3. Check internet connection
4. Check Python version: `python --version`
5. Reinstall dependencies: `pip install -r requirements.txt --upgrade`

---

## 🎯 Future Features Coming

- Email integration
- Reminder and alarm functionality
- Local file search
- Smart home integration
- Multi-language support
- Custom voice profiles

---

**Enjoy your AI Voice Chatbot! 🎉**
