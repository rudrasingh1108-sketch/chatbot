# Chatbot Project Structure

This project has been organized into a clean, modular structure:

## Directory Structure

```
chatbot/
├── backend/                 # Backend API and main logic
│   ├── app.py              # Flask web application
│   ├── main.py             # Core chatbot functionality
│   └── __init__.py
├── frontend/               # Web interface files
│   ├── static/             # CSS, JavaScript, images
│   │   ├── styles.css
│   │   └── script.js
│   ├── templates/          # HTML templates
│   │   └── index.html
│   └── __init__.py
├── core/                   # Core modules and utilities
│   ├── gml.py              # Gigzs Memory Layer
│   ├── emotion_analyzer.py # Emotion analysis
│   ├── voice_profiles.py   # Voice profile management
│   ├── gml_memory.json     # Memory storage
│   └── __init__.py
├── scripts/                # Launch and utility scripts
│   ├── gui_launcher.py    # GUI launcher
│   ├── launch.bat          # Windows launcher
│   └── launch_web.bat      # Web app launcher
├── tests/                  # Test files
│   └── test_gml.py         # GML tests
├── docs/                   # Documentation
│   ├── README.md
│   ├── *.md               # Various documentation files
│   └── *.txt              # Text documentation
├── requirements.txt        # Python dependencies
└── .gitignore             # Git ignore file
```

## How to Run

### Web Application
```bash
# From project root
python backend/app.py
```

### Desktop GUI
```bash
# From project root  
python scripts/gui_launcher.py
```

### Using Launch Scripts
- Windows: Run `scripts/launch.bat` for GUI or `scripts/launch_web.bat` for web

## Key Components

- **Backend**: Flask API serving the web interface and handling core logic
- **Frontend**: Web UI with HTML, CSS, and JavaScript
- **Core**: Essential modules for memory, emotions, and voice profiles
- **Scripts**: Launch utilities and helper tools
- **Tests**: Unit tests for core functionality
