// API Base URL
const API_BASE = `${window.location.origin}/api`;

// Web Speech API Setup
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const SpeechSynthesis = window.speechSynthesis;
let recognition = null;
let isListening = false;
let micInUse = false;
let recordedSampleRate = 16000;
let wakeStatusInterval = null;

// DOM Elements
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const voiceBtn = document.getElementById('voice-btn');
const voiceIndicator = document.getElementById('voice-indicator');
const messagesContainer = document.getElementById('messages');
const chatContainer = document.getElementById('chat-container');
const userSelect = document.getElementById('user-select');
const setUserBtn = document.getElementById('set-user-btn');
const logoutBtn = document.getElementById('logout-btn');
const currentUserDiv = document.getElementById('current-user');
const clearHistoryBtn = document.getElementById('clear-history-btn');
const analysisPanel = document.getElementById('analysis-panel');
const sentimentIndicator = document.getElementById('sentiment-indicator');
const emotionIndicator = document.getElementById('emotion-indicator');
const fraudIndicator = document.getElementById('fraud-indicator');

// Modals
const weatherModal = document.getElementById('weather-modal');
const closeWeather = document.getElementById('close-weather');
const definitionModal = document.getElementById('definition-modal');
const closeDefinition = document.getElementById('close-definition');

// Audio Variables
let audioContext = null;
let audioStream = null;
let audioSource = null;
let processorNode = null;
let recordedPCM = [];
let recordedSamples = 0;

// State
let currentUser = null;
let chatHistory = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (!messageInput || !sendBtn || !messagesContainer) return;

    // Unlock Audio on first interaction
    document.addEventListener('click', unlockAudio, { once: true });

    loadUserProfiles();
    setupEventListeners();
    loadChatHistory();
    startWakeStatusPolling();
});

function unlockAudio() {
    if (SpeechSynthesis) {
        const utterance = new SpeechSynthesisUtterance('');
        utterance.volume = 0;
        SpeechSynthesis.speak(utterance);
        
        setTimeout(() => {
            const now = new Date();
            const hour = now.getHours();
            let greeting = "Good morning";
            if (hour >= 12 && hour < 17) greeting = "Good afternoon";
            else if (hour >= 17 || hour < 4) greeting = "Good evening";
            
            const welcomeMsg = `Hello sir, ${greeting}.`;
            addMessage(welcomeMsg, false);
            speakResponse(welcomeMsg);
        }, 500);
    }
}

function startWakeStatusPolling() {
    if (wakeStatusInterval) return;
    wakeStatusInterval = setInterval(async () => {
        if (isListening || micInUse) return;
        
        try {
            const resp = await fetch(`${API_BASE}/wake-status`);
            const data = await resp.json();
            if (data.detected) {
                console.log("Wake word detected via backend!");
                if (voiceIndicator) {
                    voiceIndicator.textContent = '👂 Detected! Listening...';
                    voiceIndicator.classList.add('active');
                }
                speakResponse("How can I help you?");
                setTimeout(() => {
                    toggleVoiceInput();
                }, 1000);
            }
        } catch (e) {
            console.error("Error polling wake status:", e);
        }
    }, 500);
}

function setupEventListeners() {
    // Tab Switching
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`${target}-tab-content`).classList.add('active');
            
            if (target === 'iot') loadIoTDevices();
            if (target === 'memory') loadMemoryStats();
        });
    });

    // Send logic
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSendMessage();
    });
    sendBtn.addEventListener('click', handleSendMessage);
    voiceBtn.addEventListener('click', toggleVoiceInput);

    // Suggestion Chips
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            messageInput.value = chip.textContent;
            handleSendMessage();
        });
    });

    // Quick Actions
    document.querySelectorAll('.quick-action').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.action;
            if (action === 'weather') weatherModal.style.display = 'flex';
            if (action === 'definition') definitionModal.style.display = 'flex';
            if (action === 'joke') getQuickResult('joke');
            if (action === 'news') getQuickResult('news');
            if (action === 'time') getTime();
        });
    });

    if (closeWeather) closeWeather.onclick = () => weatherModal.style.display = "none";
    if (closeDefinition) closeDefinition.onclick = () => definitionModal.style.display = "none";

    // User handling
    setUserBtn.addEventListener('click', async () => {
        const username = userSelect.value;
        if (!username) return;
        try {
            const resp = await fetch(`${API_BASE}/set-current-user`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username })
            });
            const data = await resp.json();
            currentUser = username;
            updateUserDisplay(data.greeting);
            loadChatHistory();
        } catch (e) { console.error(e); }
    });

    logoutBtn.addEventListener('click', () => {
        currentUser = null;
        updateUserDisplay();
        messagesContainer.innerHTML = '';
        analysisPanel.style.display = 'none';
    });

    clearHistoryBtn.addEventListener('click', async () => {
        if (!confirm('Clear history?')) return;
        await fetch(`${API_BASE}/clear-history`, { method: 'POST' });
        messagesContainer.innerHTML = '';
    });
}

async function handleSendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;
    
    messageInput.value = '';
    addMessage(text, true);
    
    try {
        const resp = await fetch(`${API_BASE}/assistant`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        const data = await resp.json();
        if (resp.ok) {
            addMessage(data.reply, false, data);
            speakResponse(data.reply);
        }
    } catch (e) {
        addMessage("Analysis failed. Connection error.", false);
    }
}

function addMessage(text, isUser = false, analysis = null) {
    const welcome = document.querySelector('.welcome-message');
    if (welcome && welcome.style.display !== 'none') welcome.style.display = 'none';

    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user' : 'bot'}`;
    
    let emoji = '';
    if (!isUser) {
        const low = text.toLowerCase();
        if (low.includes('weather')) emoji = ' 🌦️';
        else if (low.includes('joke')) emoji = ' 😂';
        else if (low.includes('remember')) emoji = ' 🧠';
    }

    msgDiv.innerHTML = `<div class="message-content">${escapeHtml(text)}${emoji}</div>`;
    messagesContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    if (analysis && !isUser) showAnalysis(analysis);
}

function showAnalysis(analysis) {
    analysisPanel.style.display = 'flex';
    const sentMap = { 'positive': '😊 Positive', 'neutral': '😐 Neutral', 'negative': '😟 Negative' };
    const secMap = { 'low': '🛡️ Secure', 'medium': '⚠️ Caution', 'high': '🚨 Warning' };

    sentimentIndicator.textContent = sentMap[analysis.sentiment] || '😐 Neutral';
    emotionIndicator.textContent = `🎭 ${analysis.emotion || 'Calm'}`;
    fraudIndicator.textContent = secMap[analysis.fraud_risk] || '🛡️ Secure';
    fraudIndicator.style.color = analysis.fraud_risk === 'high' ? '#ef4444' : (analysis.fraud_risk === 'medium' ? '#f59e0b' : '#10b981');
}

async function loadUserProfiles() {
    try {
        const resp = await fetch(`${API_BASE}/voice-profiles`);
        const data = await resp.json();
        userSelect.innerHTML = '<option value="">-- Choose User --</option>';
        data.profiles.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p;
            opt.textContent = p;
            userSelect.appendChild(opt);
        });
    } catch (e) { console.error(e); }
}

function updateUserDisplay(greeting = "") {
    if (currentUser) {
        currentUserDiv.innerHTML = `<i class="fas fa-user-check"></i> <strong>${currentUser}</strong>`;
        if (greeting) addMessage(greeting, false);
    } else {
        currentUserDiv.innerHTML = `<p>Not logged in</p>`;
    }
}

async function loadIoTDevices() {
    const grid = document.getElementById('iot-device-grid');
    grid.innerHTML = '<div class="loading">Syncing local network...</div>';
    try {
        const resp = await fetch(`${API_BASE}/iot/devices`);
        const data = await resp.json();
        grid.innerHTML = '';
        data.devices.forEach(device => {
            const card = document.createElement('div');
            const isOn = device.state.power || !device.state.locked;
            card.className = `device-card ${isOn ? 'on' : ''}`;
            const icon = device.type === 'light' ? 'fa-lightbulb' : (device.type === 'lock' ? 'fa-lock' : 'fa-bolt');
            card.innerHTML = `
                <div class="device-header">
                    <div class="device-info">
                        <div class="device-icon"><i class="fas ${icon}"></i></div>
                        <div><div class="device-name">${device.name}</div><div class="device-type">${device.type}</div></div>
                    </div>
                    <label class="switch">
                        <input type="checkbox" ${isOn ? 'checked' : ''} onchange="toggleDevice('${device.id}', this.checked)">
                        <span class="slider"></span>
                    </label>
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (e) { grid.innerHTML = 'Error loading devices.'; }
}

async function loadMemoryStats() {
    const container = document.querySelector('.memory-container');
    try {
        const resp = await fetch(`${API_BASE}/memory/stats`);
        const data = await resp.json();
        container.innerHTML = `
            <div class="memory-stats-grid">
                <div class="stat-card"><span class="label">ENTITIES</span><span class="value">${data.statistics.total_entities}</span></div>
                <div class="stat-card"><span class="label">RELATIONS</span><span class="value">${data.statistics.total_relationships}</span></div>
                <div class="stat-card"><span class="label">EVENTS</span><span class="value">${data.statistics.total_events}</span></div>
            </div>
        `;
    } catch (e) { container.innerHTML = 'Error loading stats.'; }
}

function speakResponse(text) {
    if (!SpeechSynthesis) return;
    
    // Do NOT speak if microphone is currently active (recording or micInUse)
    if (isListening || micInUse) {
        console.log("Speech blocked: Mic is active.");
        if (SpeechSynthesis.speaking) SpeechSynthesis.cancel();
        return;
    }

    // Double check mic state right before speaking
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        // This is a global flag check
        if (isListening || micInUse) return;
    }

    SpeechSynthesis.cancel();
    setTimeout(() => {
        // Final safety check inside timeout
        if (isListening || micInUse) return;

        const utt = new SpeechSynthesisUtterance(text);
        utt.rate = 1.1;
        
        // Ensure we handle start event to check mic state again
        utt.onstart = () => {
            if (isListening || micInUse) {
                SpeechSynthesis.cancel();
            }
        };

        SpeechSynthesis.speak(utt);
    }, 50);
}

function toggleVoiceInput() {
    if (isListening) {
        stopVoiceRecording();
    } else {
        // STOP all dictation immediately before opening mic
        if (SpeechSynthesis && SpeechSynthesis.speaking) {
            console.log("Cancelling speech for mic entry.");
            SpeechSynthesis.cancel();
        }
        startVoiceRecording();
    }
}

async function startVoiceRecording() {
    try {
        // Cancel any ongoing speech before starting mic
        if (SpeechSynthesis) SpeechSynthesis.cancel();
        
        audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        recordedSampleRate = audioContext.sampleRate;

        recordedPCM = [];
        recordedSamples = 0;

        audioSource = audioContext.createMediaStreamSource(audioStream);
        processorNode = audioContext.createScriptProcessor(4096, 1, 1);

        processorNode.onaudioprocess = (e) => {
            if (!isListening) return;
            const input = e.inputBuffer.getChannelData(0);
            const chunk = new Float32Array(input);
            recordedPCM.push(chunk);
            recordedSamples += chunk.length;
        };

        audioSource.connect(processorNode);
        processorNode.connect(audioContext.destination);

        isListening = true;
        voiceBtn.classList.add('listening');
        voiceIndicator.textContent = 'Listening...';
        voiceIndicator.classList.add('active');
    } catch (e) { 
        console.error("Mic access error:", e);
        addMessage("Could not access microphone. Please check permissions.", false);
    }
}

async function stopVoiceRecording() {
    isListening = false;
    voiceBtn.classList.remove('listening');
    voiceIndicator.textContent = 'Ready';
    voiceIndicator.classList.remove('active');

    try {
        if (processorNode) processorNode.disconnect();
        if (audioSource) audioSource.disconnect();
        if (audioContext) await audioContext.close();
        if (audioStream) audioStream.getTracks().forEach(t => t.stop());
    } catch (e) {
        console.error("Error closing audio:", e);
    } finally {
        processorNode = null;
        audioSource = null;
        audioContext = null;
        audioStream = null;
    }

    if (recordedSamples > 0) {
        processTranscription();
    }
}

async function processTranscription() {
    voiceIndicator.textContent = 'Transcribing...';
    try {
        const wavBlob = encodeWav(recordedPCM, recordedSamples, recordedSampleRate);
        const form = new FormData();
        form.append('audio', wavBlob, 'speech.wav');

        const resp = await fetch(`${API_BASE}/stt/transcribe`, {
            method: 'POST',
            body: form
        });
        const data = await resp.json();
        if (resp.ok && data.text) {
            const text = data.text.trim();
            if (text) {
                messageInput.value = text;
                handleSendMessage();
            }
        } else {
            addMessage("Transcribing failed. Please try again.", false);
        }
    } catch (e) {
        console.error("Transcription error:", e);
        addMessage("Transcription service error.", false);
    } finally {
        voiceIndicator.textContent = 'Ready';
    }
}

function encodeWav(chunks, totalSamples, sampleRate) {
    const buffer = new Float32Array(totalSamples);
    let offset = 0;
    for (const c of chunks) {
        buffer.set(c, offset);
        offset += c.length;
    }

    const wavBuffer = new ArrayBuffer(44 + buffer.length * 2);
    const view = new DataView(wavBuffer);

    const writeString = (view, offset, string) => {
        for (let i = 0; i < string.length; i++) {
            view.setUint8(offset + i, string.charCodeAt(i));
        }
    };

    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + buffer.length * 2, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeString(view, 36, 'data');
    view.setUint32(40, buffer.length * 2, true);

    let idx = 44;
    for (let i = 0; i < buffer.length; i++) {
        let s = Math.max(-1, Math.min(1, buffer[i]));
        view.setInt16(idx, s < 0 ? s * 0x8000 : s * 0x7fff, true);
        idx += 2;
    }

    return new Blob([wavBuffer], { type: 'audio/wav' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function loadChatHistory() {
    try {
        const resp = await fetch(`${API_BASE}/chat-history`);
        chatHistory = await resp.json();
    } catch (e) { console.error(e); }
}

async function getQuickResult(type) {
    try {
        const resp = await fetch(`${API_BASE}/${type}`);
        const data = await resp.json();
        if (resp.ok) {
            const text = data[type] || data.news || '';
            addMessage(text, false);
            speakResponse(text);
        }
    } catch (e) { console.error(e); }
}

function getTime() {
    const now = new Date();
    const msg = `The time is ${now.toLocaleTimeString()}`;
    addMessage(msg, false);
    speakResponse(msg);
}

window.toggleDevice = async (id, state) => {
    try {
        await fetch(`${API_BASE}/iot/control`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ device_id: id, action: state ? 'turn_on' : 'turn_off' })
        });
        loadIoTDevices();
    } catch (e) { console.error(e); }
};
