const API_BASE = `${window.location.origin}/api`;

const logEl = document.getElementById('iot-log');
const commandEl = document.getElementById('iot-command');
const sendBtn = document.getElementById('iot-send');
const refreshBtn = document.getElementById('iot-refresh');
const gridEl = document.getElementById('device-grid');
const statusEl = document.getElementById('iot-status');
const micBtn = document.getElementById('iot-mic');

function addLog(text, role = 'assistant') {
  const row = document.createElement('div');
  row.className = `log-row ${role}`;
  row.textContent = text;
  logEl.appendChild(row);
  logEl.scrollTop = logEl.scrollHeight;
}

function deviceCard(device) {
  const card = document.createElement('div');
  card.className = 'device-card';

  const title = document.createElement('div');
  title.className = 'device-title';
  title.textContent = device.name;

  const meta = document.createElement('div');
  meta.className = 'device-meta';
  meta.textContent = device.type;

  const state = document.createElement('div');
  state.className = 'device-state';

  const controls = document.createElement('div');
  controls.className = 'device-controls';

  if (device.type === 'light' || device.type === 'switch') {
    const power = !!device.state.power;
    state.textContent = power ? 'ON' : 'OFF';

    const btn = document.createElement('button');
    btn.className = power ? 'btn-danger' : 'btn-primary';
    btn.textContent = power ? 'Turn off' : 'Turn on';
    btn.addEventListener('click', async () => {
      await patchDevice(device.id, { power: !power });
      await loadDevices();
    });
    controls.appendChild(btn);
  } else if (device.type === 'thermostat') {
    const temp = device.state.temperature;
    state.textContent = `${temp}°C`;

    const input = document.createElement('input');
    input.type = 'range';
    input.min = '16';
    input.max = '30';
    input.value = String(temp);
    input.className = 'temp-slider';

    const value = document.createElement('div');
    value.className = 'temp-value';
    value.textContent = `${temp}°C`;

    input.addEventListener('input', () => {
      value.textContent = `${input.value}°C`;
    });

    const btn = document.createElement('button');
    btn.className = 'btn-primary';
    btn.textContent = 'Set';
    btn.addEventListener('click', async () => {
      await patchDevice(device.id, { temperature: Number(input.value) });
      await loadDevices();
    });

    controls.appendChild(input);
    controls.appendChild(value);
    controls.appendChild(btn);
  } else if (device.type === 'lock') {
    const locked = !!device.state.locked;
    state.textContent = locked ? 'LOCKED' : 'UNLOCKED';

    const btn = document.createElement('button');
    btn.className = locked ? 'btn-primary' : 'btn-danger';
    btn.textContent = locked ? 'Unlock' : 'Lock';
    btn.addEventListener('click', async () => {
      await patchDevice(device.id, { locked: !locked });
      await loadDevices();
    });
    controls.appendChild(btn);
  } else {
    state.textContent = JSON.stringify(device.state);
  }

  card.appendChild(title);
  card.appendChild(meta);
  card.appendChild(state);
  card.appendChild(controls);
  return card;
}

async function loadDevices() {
  try {
    statusEl.textContent = 'Connected';
    const res = await fetch(`${API_BASE}/iot/devices`);
    const data = await res.json();
    gridEl.innerHTML = '';
    (data.devices || []).forEach(d => gridEl.appendChild(deviceCard(d)));
  } catch (e) {
    console.error(e);
    statusEl.textContent = 'Offline';
    addLog('Failed to load devices.', 'assistant');
  }
}

async function patchDevice(deviceId, state) {
  await fetch(`${API_BASE}/iot/device/${encodeURIComponent(deviceId)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ state })
  });
}

async function sendCommand(text) {
  if (!text) return;
  addLog(text, 'user');

  try {
    let res = await fetch(`${API_BASE}/assistant`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    if (!res.ok) {
      res = await fetch(`${API_BASE}/iot/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
    }

    const data = await res.json();
    addLog(data.reply || 'OK', 'assistant');
    if (data.devices) {
      gridEl.innerHTML = '';
      (data.devices || []).forEach(d => gridEl.appendChild(deviceCard(d)));
    } else {
      await loadDevices();
    }
  } catch (e) {
    console.error(e);
    addLog('Command failed.', 'assistant');
  }
}

// Simple voice input (browser SpeechRecognition)
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let listening = false;
if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'en-US';

  recognition.onresult = async (e) => {
    const t = e.results?.[0]?.[0]?.transcript || '';
    commandEl.value = t;
    await sendCommand(t.toLowerCase());
  };

  recognition.onerror = (e) => {
    addLog(`Mic error: ${e.error}`, 'assistant');
    listening = false;
  };

  recognition.onend = () => {
    listening = false;
    micBtn.textContent = '🎤';
  };
}

micBtn.addEventListener('click', async () => {
  if (!recognition) {
    addLog('SpeechRecognition not supported in this browser.', 'assistant');
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach(t => t.stop());
  } catch (e) {
    addLog('Microphone permission denied.', 'assistant');
    return;
  }

  if (listening) {
    recognition.stop();
    return;
  }

  listening = true;
  micBtn.textContent = '🛑';
  try {
    recognition.abort();
  } catch (e) {}
  recognition.start();
});

sendBtn.addEventListener('click', async () => {
  const text = commandEl.value.trim();
  commandEl.value = '';
  await sendCommand(text);
});

commandEl.addEventListener('keypress', async (e) => {
  if (e.key === 'Enter') {
    const text = commandEl.value.trim();
    commandEl.value = '';
    await sendCommand(text);
  }
});

refreshBtn.addEventListener('click', loadDevices);

// Chip click
document.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', async () => {
    await sendCommand(chip.textContent);
  });
});

addLog('JARVIS online. Ready for commands.', 'assistant');
loadDevices();
