// API Base URL
const API_BASE = 'http://localhost:5000/api';

// Web Speech API Setup
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const SpeechSynthesis = window.speechSynthesis;
let recognition = null;
let isListening = false;
let recognitionActive = false;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.language = 'en-US';
}

// DOM Elements
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const voiceBtn = document.getElementById('voice-btn');
const voiceIndicator = document.getElementById('voice-indicator');
const voiceTranscript = document.getElementById('voice-transcript');
const messagesDiv = document.getElementById('messages');
const chatContainer = document.getElementById('chat-container');
const userSelect = document.getElementById('user-select');
const setUserBtn = document.getElementById('set-user-btn');
const logoutBtn = document.getElementById('logout-btn');
const currentUserDiv = document.getElementById('current-user');
const profilesList = document.getElementById('profiles-list');
const createProfileBtn = document.getElementById('create-profile-btn');
const clearHistoryBtn = document.getElementById('clear-history-btn');

// Modals
const profileModal = document.getElementById('profile-modal');
const closeProfileModal = document.getElementById('close-modal');
const createProfileConfirmBtn = document.getElementById('create-profile-confirm-btn');
const profileUsername = document.getElementById('profile-username');

const weatherModal = document.getElementById('weather-modal');
const closeWeatherModal = document.getElementById('close-weather');
const getWeatherBtn = document.getElementById('get-weather-btn');
const weatherCity = document.getElementById('weather-city');
const weatherResult = document.getElementById('weather-result');

const definitionModal = document.getElementById('definition-modal');
const closeDefinitionModal = document.getElementById('close-definition');
const getDefinitionBtn = document.getElementById('get-definition-btn');
const definitionWord = document.getElementById('definition-word');
const definitionResult = document.getElementById('definition-result');

// State
let currentUser = null;
let chatHistory = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadUserProfiles();
    setupEventListeners();
    setupVoiceRecognition();
    loadChatHistory();
});

// Event Listeners
function setupEventListeners() {
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    voiceBtn.addEventListener('click', toggleVoiceInput);
    setUserBtn.addEventListener('click', setCurrentUser);
    logoutBtn.addEventListener('click', logout);
    createProfileBtn.addEventListener('click', () => {
        profileModal.style.display = 'block';
        profileUsername.focus();
    });
    createProfileConfirmBtn.addEventListener('click', createNewProfile);
    closeProfileModal.addEventListener('click', () => {
        profileModal.style.display = 'none';
    });
    clearHistoryBtn.addEventListener('click', clearChatHistory);

    // Weather Modal
    document.querySelectorAll('.quick-action[data-action="weather"]').forEach(btn => {
        btn.addEventListener('click', () => {
            weatherModal.style.display = 'block';
            weatherCity.focus();
        });
    });
    closeWeatherModal.addEventListener('click', () => {
        weatherModal.style.display = 'none';
    });
    getWeatherBtn.addEventListener('click', getWeather);

    // Definition Modal
    document.querySelectorAll('.quick-action[data-action="definition"]').forEach(btn => {
        btn.addEventListener('click', () => {
            definitionModal.style.display = 'block';
            definitionWord.focus();
        });
    });
    closeDefinitionModal.addEventListener('click', () => {
        definitionModal.style.display = 'none';
    });
    getDefinitionBtn.addEventListener('click', getDefinition);

    // Quick Actions
    document.querySelectorAll('.quick-action').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            handleQuickAction(action);
        });
    });

    // Close modals on outside click
    window.addEventListener('click', (e) => {
        if (e.target === profileModal) profileModal.style.display = 'none';
        if (e.target === weatherModal) weatherModal.style.display = 'none';
        if (e.target === definitionModal) definitionModal.style.display = 'none';
    });
}

async function loadUserProfiles() {
    try {
        const response = await fetch(`${API_BASE}/voice-profiles`);
        const data = await response.json();
        const profiles = data.profiles || [];

        // Update user select dropdown
        userSelect.innerHTML = '<option value="">-- Choose User --</option>';
        profiles.forEach(profile => {
            const option = document.createElement('option');
            option.value = profile;
            option.textContent = profile;
            userSelect.appendChild(option);
        });

        // Update profiles list in sidebar
        profilesList.innerHTML = '';
        if (profiles.length === 0) {
            profilesList.innerHTML = '<p style="text-align: center; color: #a0aec0;">No profiles yet</p>';
        } else {
            profiles.forEach(profile => {
                const item = document.createElement('div');
                item.className = 'profile-item';
                item.innerHTML = `
                    <span>${profile}</span>
                    <button onclick="deleteProfile('${profile}')">Delete</button>
                `;
                profilesList.appendChild(item);
            });
        }
    } catch (error) {
        console.error('Error loading profiles:', error);
    }
}

async function setCurrentUser() {
    const username = userSelect.value.trim();
    if (!username) {
        alert('Please select a user');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/set-current-user`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });
        const data = await response.json();

        if (response.ok) {
            currentUser = username;
            currentUserDiv.innerHTML = `
                <strong>${username}</strong>
                <p style="color: #a0aec0; margin-top: 8px;">${data.greeting}</p>
            `;
            setUserBtn.style.display = 'none';
            logoutBtn.style.display = 'block';
            addMessageToChat(data.greeting, 'bot');
        } else {
            alert(data.error || 'Error setting user');
        }
    } catch (error) {
        console.error('Error setting user:', error);
        alert('Error setting user');
    }
}

function logout() {
    currentUser = null;
    currentUserDiv.innerHTML = '<p>Not logged in</p>';
    userSelect.value = '';
    setUserBtn.style.display = 'block';
    logoutBtn.style.display = 'none';
}

// Voice Recognition Setup
function setupVoiceRecognition() {
    if (!recognition) {
        voiceBtn.disabled = true;
        voiceBtn.title = 'Speech Recognition not supported in this browser';
        return;
    }

    // Listening started
    recognition.onstart = () => {
        isListening = true;
        voiceBtn.classList.add('listening');
        voiceIndicator?.classList.add('active');
        if (voiceIndicator) voiceIndicator.textContent = '🎤 Listening...';
        messageInput.placeholder = 'Listening...';
    };

    // Interim results (real-time transcription)
    recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;

            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }

        // Update text input with final transcript
        if (finalTranscript) {
            messageInput.value = finalTranscript;
        }

        // Show interim results
        if (voiceTranscript) {
            voiceTranscript.textContent = interimTranscript || finalTranscript;
        }
    };

    // Listening ended
    recognition.onend = () => {
        isListening = false;
        voiceBtn.classList.remove('listening');
        voiceIndicator?.classList.remove('active');
        if (voiceIndicator) voiceIndicator.textContent = '🎤 Tap to speak';
        messageInput.placeholder = 'Type your message or use voice...';

        // Auto-send if we have final text
        if (messageInput.value.trim()) {
            setTimeout(() => sendMessage(), 500);
        }
    };

    // Error handling
    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        let errorMsg = 'Speech recognition error: ';
        switch (event.error) {
            case 'no-speech':
                errorMsg += 'No speech detected. Please try again.';
                break;
            case 'audio-capture':
                errorMsg += 'No microphone found.';
                break;
            case 'not-allowed':
                errorMsg += 'Microphone access denied.';
                break;
            default:
                errorMsg += event.error;
        }
        alert(errorMsg);
        isListening = false;
        voiceBtn.classList.remove('listening');
    };
}

// Toggle voice input
function toggleVoiceInput() {
    if (!recognition) {
        alert('Speech Recognition is not supported in your browser. Try Chrome, Edge, or Safari.');
        return;
    }

    if (isListening) {
        recognition.stop();
    } else {
        // Clear input and start listening
        messageInput.value = '';
        if (voiceTranscript) voiceTranscript.textContent = '';
        recognition.stop();
        setTimeout(() => recognition.start(), 100);
    }
}

// Speak text response using Web Speech Synthesis API
function speakResponse(text) {
    if (!SpeechSynthesis) return;

    // Cancel any ongoing speech
    SpeechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    utterance.language = 'en-US';

    SpeechSynthesis.speak(utterance);
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    messageInput.value = '';
    addMessageToChat(message, 'user');

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        const data = await response.json();

        if (response.ok) {
            addMessageToChat(data.bot, 'bot');
            // Speak the bot's response
            speakResponse(data.bot);
            chatHistory.push(data);
        } else {
            const errorMsg = data.error || 'Error processing message';
            addMessageToChat(errorMsg, 'bot');
            speakResponse(errorMsg);
        }
    } catch (error) {
        console.error('Error:', error);
        const errorMsg = 'Sorry, an error occurred while processing your message.';
        addMessageToChat(errorMsg, 'bot');
        speakResponse(errorMsg);
    }

    messageInput.focus();
}

function addMessageToChat(text, sender) {
    if (messagesDiv.parentElement.classList.contains('welcome-message')) {
        messagesDiv.parentElement.style.display = 'none';
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.innerHTML = `<div class="message-content">${escapeHtml(text)}</div>`;
    messagesDiv.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function createNewProfile() {
    const username = profileUsername.value.trim();
    if (!username) {
        alert('Please enter a username');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/voice-profiles/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });
        const data = await response.json();

        if (response.ok) {
            document.getElementById('profile-status').textContent = `✓ Profile created for ${username}`;
            profileUsername.value = '';
            setTimeout(() => {
                profileModal.style.display = 'none';
                document.getElementById('profile-status').textContent = '';
                loadUserProfiles();
            }, 1500);
        } else {
            document.getElementById('profile-status').textContent = `✗ ${data.error}`;
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('profile-status').textContent = '✗ Error creating profile';
    }
}

async function deleteProfile(username) {
    if (!confirm(`Delete profile for ${username}?`)) return;

    try {
        const response = await fetch(`${API_BASE}/voice-profiles/${username}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadUserProfiles();
            addMessageToChat(`Profile for ${username} has been deleted.`, 'bot');
        } else {
            alert('Error deleting profile');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting profile');
    }
}

async function getWeather() {
    const city = weatherCity.value.trim() || 'London';

    try {
        const response = await fetch(`${API_BASE}/weather?city=${encodeURIComponent(city)}`);
        const data = await response.json();

        if (response.ok) {
            weatherResult.textContent = data.weather;
            addMessageToChat(data.weather, 'bot');
            weatherCity.value = 'London';
            setTimeout(() => {
                weatherModal.style.display = 'none';
                weatherResult.textContent = '';
            }, 2000);
        } else {
            weatherResult.textContent = data.error || 'Error fetching weather';
        }
    } catch (error) {
        console.error('Error:', error);
        weatherResult.textContent = 'Error fetching weather';
    }
}

async function getDefinition() {
    const word = definitionWord.value.trim();
    if (!word) {
        alert('Please enter a word');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/define?word=${encodeURIComponent(word)}`);
        const data = await response.json();

        if (response.ok) {
            definitionResult.textContent = data.definition;
            addMessageToChat(data.definition, 'bot');
            definitionWord.value = '';
        } else {
            definitionResult.textContent = data.error || 'Error fetching definition';
        }
    } catch (error) {
        console.error('Error:', error);
        definitionResult.textContent = 'Error fetching definition';
    }
}

async function handleQuickAction(action) {
    switch (action) {
        case 'weather':
            weatherModal.style.display = 'block';
            weatherCity.focus();
            break;
        case 'joke':
            getJoke();
            break;
        case 'news':
            getNews();
            break;
        case 'definition':
            definitionModal.style.display = 'block';
            definitionWord.focus();
            break;
        case 'time':
            getTime();
            break;
    }
}

async function getJoke() {
    try {
        const response = await fetch(`${API_BASE}/joke`);
        const data = await response.json();

        if (response.ok) {
            addMessageToChat(data.joke, 'bot');
        } else {
            addMessageToChat('Error fetching joke', 'bot');
        }
    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('Error fetching joke', 'bot');
    }
}

async function getNews() {
    try {
        const response = await fetch(`${API_BASE}/news?category=general`);
        const data = await response.json();

        if (response.ok) {
            addMessageToChat(data.news, 'bot');
        } else {
            addMessageToChat('Error fetching news', 'bot');
        }
    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('Error fetching news', 'bot');
    }
}

function getTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    const dateStr = now.toLocaleDateString();
    const message = `The time is ${timeStr} and the date is ${dateStr}`;
    addMessageToChat(message, 'bot');
}

async function clearChatHistory() {
    if (!confirm('Are you sure you want to clear chat history?')) return;

    try {
        const response = await fetch(`${API_BASE}/clear-history`, {
            method: 'POST'
        });

        if (response.ok) {
            messagesDiv.innerHTML = '';
            chatHistory = [];
            addMessageToChat('Chat history cleared. How can I help?', 'bot');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function loadChatHistory() {
    try {
        const response = await fetch(`${API_BASE}/chat-history`);
        chatHistory = await response.json();
        // Optionally display recent messages
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

function toggleVoiceInput() {
    // Placeholder for voice recognition
    voiceBtn.textContent = '🎤 (Not implemented)';
    alert('Voice input feature requires browser microphone access.\nPlease use the text input for now.');
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
