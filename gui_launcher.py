import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
import threading
from pathlib import Path


class ChatbotLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbot Launcher")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # Set color scheme
        self.root.configure(bg="#2c3e50")
        self.chatbot_process = None
        
        # Create main frames
        self.create_header()
        self.create_info_section()
        self.create_buttons_section()
        self.create_settings_section()
        self.create_status_section()
        
    def create_header(self):
        """Create header frame with title."""
        header_frame = tk.Frame(self.root, bg="#34495e", height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        title_label = tk.Label(
            header_frame,
            text="🤖 AI Voice Chatbot",
            font=("Helvetica", 24, "bold"),
            bg="#34495e",
            fg="#ecf0f1"
        )
        title_label.pack(pady=15)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Smart Voice Assistant with Multiple Features",
            font=("Helvetica", 10),
            bg="#34495e",
            fg="#bdc3c7"
        )
        subtitle_label.pack(pady=5)
    
    def create_info_section(self):
        """Create information section showing available features."""
        info_frame = tk.LabelFrame(
            self.root,
            text="📋 Available Features",
            font=("Helvetica", 10, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1",
            padx=10,
            pady=10
        )
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        features = [
            "🌐 Open Websites (YouTube, Google, GitHub, etc.)",
            "🖥️ Launch Applications (Notepad, Calculator, Explorer, etc.)",
            "⚙️ System Control (Shutdown, Restart, Sleep, Lock)",
            "🕐 Information (Time, Date, Weather, Definitions)",
            "📰 News Headlines (Technology, Business, Sports, etc.)",
            "😂 Entertainment (Tell Jokes)",
            "🧮 Calculations (Math Operations)",
            "🔍 Web Search (Google Search)"
        ]
        
        features_text = "\n".join(features)
        features_label = tk.Label(
            info_frame,
            text=features_text,
            font=("Helvetica", 9),
            bg="#2c3e50",
            fg="#ecf0f1",
            justify=tk.LEFT
        )
        features_label.pack(anchor=tk.W)
    
    def create_buttons_section(self):
        """Create main action buttons."""
        buttons_frame = tk.Frame(self.root, bg="#2c3e50")
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Start button
        start_button = tk.Button(
            buttons_frame,
            text="▶ START CHATBOT",
            command=self.start_chatbot,
            font=("Helvetica", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=10,
            relief=tk.RAISED,
            cursor="hand2"
        )
        start_button.pack(side=tk.LEFT, padx=5)
        
        # Stop button
        stop_button = tk.Button(
            buttons_frame,
            text="⏹ STOP CHATBOT",
            command=self.stop_chatbot,
            font=("Helvetica", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            padx=20,
            pady=10,
            relief=tk.RAISED,
            cursor="hand2"
        )
        stop_button.pack(side=tk.LEFT, padx=5)
        
        # Help button
        help_button = tk.Button(
            buttons_frame,
            text="❓ HELP",
            command=self.show_help,
            font=("Helvetica", 12, "bold"),
            bg="#3498db",
            fg="white",
            padx=20,
            pady=10,
            relief=tk.RAISED,
            cursor="hand2"
        )
        help_button.pack(side=tk.LEFT, padx=5)
    
    def create_settings_section(self):
        """Create settings section for API key configuration."""
        settings_frame = tk.LabelFrame(
            self.root,
            text="⚙️ Settings",
            font=("Helvetica", 10, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1",
            padx=10,
            pady=10
        )
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # News API Key input
        api_label = tk.Label(
            settings_frame,
            text="News API Key:",
            font=("Helvetica", 9),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        api_label.pack(anchor=tk.W, pady=5)
        
        self.api_entry = tk.Entry(
            settings_frame,
            font=("Helvetica", 9),
            width=50,
            show="*"
        )
        self.api_entry.pack(fill=tk.X, pady=5)
        
        # Load existing API key if available
        self.load_api_key()
        
        save_button = tk.Button(
            settings_frame,
            text="💾 Save API Key",
            command=self.save_api_key,
            font=("Helvetica", 9),
            bg="#9b59b6",
            fg="white",
            relief=tk.RAISED,
            cursor="hand2"
        )
        save_button.pack(pady=5)
        
        info_text = tk.Label(
            settings_frame,
            text="Get free API key from https://newsapi.org/",
            font=("Helvetica", 8),
            bg="#2c3e50",
            fg="#bdc3c7"
        )
        info_text.pack(anchor=tk.W, pady=5)
    
    def create_status_section(self):
        """Create status display section."""
        status_frame = tk.LabelFrame(
            self.root,
            text="📊 Status",
            font=("Helvetica", 10, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1",
            padx=10,
            pady=10
        )
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.status_text = scrolledtext.ScrolledText(
            status_frame,
            font=("Courier", 9),
            bg="#1a1a1a",
            fg="#00ff00",
            height=8,
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        self.log_message("✓ Chatbot Launcher Ready")
        self.log_message("Click START CHATBOT to begin")
    
    def start_chatbot(self):
        """Start the chatbot process."""
        if self.chatbot_process is not None:
            messagebox.showwarning("Warning", "Chatbot is already running!")
            return
        
        script_path = Path(__file__).parent / "main.py"
        
        if not script_path.exists():
            messagebox.showerror("Error", f"main.py not found at {script_path}")
            self.log_message("✗ Error: main.py not found")
            return
        
        try:
            self.log_message("▶ Starting Chatbot...")
            
            # Start the chatbot in a separate thread
            thread = threading.Thread(target=self._run_chatbot, daemon=True)
            thread.start()
            
            self.log_message("✓ Chatbot Started Successfully!")
            self.log_message("🎤 Listening for wake words...")
            messagebox.showinfo("Started", "Chatbot is running.\n\nSay: 'Hey Assistant' to activate")
            
        except Exception as e:
            error_msg = f"✗ Error: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", f"Failed to start chatbot:\n{str(e)}")
    
    def _run_chatbot(self):
        """Run chatbot in background thread."""
        try:
            script_path = Path(__file__).parent / "main.py"
            self.chatbot_process = subprocess.Popen(
                ["python", str(script_path)],
                cwd=Path(__file__).parent
            )
            self.chatbot_process.wait()
            self.chatbot_process = None
            self.log_message("✓ Chatbot Stopped")
        except Exception as e:
            self.log_message(f"✗ Error running chatbot: {str(e)}")
            self.chatbot_process = None
    
    def stop_chatbot(self):
        """Stop the running chatbot process."""
        if self.chatbot_process is None:
            messagebox.showwarning("Warning", "Chatbot is not running!")
            return
        
        try:
            self.log_message("⏹ Stopping Chatbot...")
            self.chatbot_process.terminate()
            self.chatbot_process.wait(timeout=5)
            self.chatbot_process = None
            self.log_message("✓ Chatbot Stopped Successfully")
            messagebox.showinfo("Stopped", "Chatbot has been stopped")
        except Exception as e:
            try:
                self.chatbot_process.kill()
                self.chatbot_process = None
                self.log_message("✓ Chatbot Force Stopped")
            except:
                pass
            self.log_message(f"✗ Error: {str(e)}")
    
    def show_help(self):
        """Show help window with commands."""
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - Available Commands")
        help_window.geometry("600x700")
        help_window.configure(bg="#2c3e50")
        
        help_text_content = """
CHATBOT COMMANDS - SAY THESE TO ACTIVATE FEATURES:

🌐 WEBSITES:
  • "Open YouTube"
  • "Open Google"
  • "Open GitHub"
  • "Open Gmail"
  • "Open Stack Overflow"

🖥️ APPLICATIONS:
  • "Open Notepad"
  • "Open Calculator"
  • "Open File Explorer"
  • "Open Paint"
  • "Open Task Manager"

⚙️ SYSTEM CONTROL:
  • "Shutdown" - Shuts down computer (30 sec delay)
  • "Restart" - Restarts computer (30 sec delay)
  • "Lock" - Locks workstation
  • "Sleep" - Puts computer to sleep

🕐 INFORMATION:
  • "What time is it?"
  • "What's the date?"
  • "Weather in [city]"
  • "Define [word]"

📰 NEWS:
  • "What's the news?"
  • "Technology news"
  • "Business news"
  • "Sports headlines"

😂 ENTERTAINMENT:
  • "Tell me a joke"
  • "Tell me something funny"

🧮 CALCULATIONS:
  • "What is 5 plus 3?"
  • "Calculate 10 times 2"
  • "100 divided by 5"

🔍 SEARCH:
  • "Search for Python"
  • "Google machine learning"

❓ HELP:
  • "Help" - Show available commands
  • "What can you do?"
        """
        
        text_widget = scrolledtext.ScrolledText(
            help_window,
            font=("Courier", 9),
            bg="#1a1a1a",
            fg="#00ff00",
            padx=10,
            pady=10
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, help_text_content)
        text_widget.config(state=tk.DISABLED)
    
    def load_api_key(self):
        """Load API key from config file if it exists."""
        try:
            config_file = Path(__file__).parent / "config.txt"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    api_key = f.read().strip()
                    if api_key:
                        self.api_entry.insert(0, api_key)
        except:
            pass
    
    def save_api_key(self):
        """Save API key to config file."""
        api_key = self.api_entry.get().strip()
        
        if not api_key:
            messagebox.showwarning("Warning", "Please enter an API key")
            return
        
        try:
            # Save to config file
            config_file = Path(__file__).parent / "config.txt"
            with open(config_file, 'w') as f:
                f.write(api_key)
            
            # Update main.py with the API key
            main_file = Path(__file__).parent / "main.py"
            if main_file.exists():
                with open(main_file, 'r') as f:
                    content = f.read()
                
                # Replace the API key in main.py
                import re
                content = re.sub(
                    r'NEWS_API_KEY = "[^"]*"',
                    f'NEWS_API_KEY = "{api_key}"',
                    content
                )
                
                with open(main_file, 'w') as f:
                    f.write(content)
            
            self.log_message("✓ API Key Saved Successfully!")
            messagebox.showinfo("Success", "API Key saved successfully!")
        except Exception as e:
            self.log_message(f"✗ Error saving API key: {str(e)}")
            messagebox.showerror("Error", f"Failed to save API key:\n{str(e)}")
    
    def log_message(self, message):
        """Add a message to the status display."""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update()


def main():
    root = tk.Tk()
    app = ChatbotLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
