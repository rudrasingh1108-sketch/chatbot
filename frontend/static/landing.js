const API_BASE = `${window.location.origin}/api`;

const tabButtons = document.querySelectorAll('.tab-btn');
const panelLogin = document.getElementById('panel-login');
const panelRegister = document.getElementById('panel-register');
const authStatus = document.getElementById('auth-status');

function setStatus(text, kind = 'info') {
  authStatus.textContent = text;
  authStatus.dataset.kind = kind;
}

function showTab(tab) {
  tabButtons.forEach(btn => btn.classList.toggle('active', btn.dataset.tab === tab));
  panelLogin.classList.toggle('hidden', tab !== 'login');
  panelRegister.classList.toggle('hidden', tab !== 'register');
  setStatus('Ready');
}

tabButtons.forEach(btn => {
  btn.addEventListener('click', () => showTab(btn.dataset.tab));
});

async function login(username) {
  if (!username) {
    setStatus('Enter a username', 'error');
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/set-current-user`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username })
    });
    const data = await res.json();

    if (!res.ok) {
      setStatus(data.error || 'Login failed', 'error');
      return;
    }

    setStatus('Success! Redirecting...', 'success');
    window.location.href = '/chat';
  } catch (e) {
    console.error(e);
    setStatus('Network error', 'error');
  }
}

async function register(username) {
  if (!username) {
    setStatus('Enter a username', 'error');
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/voice-profiles/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username })
    });
    const data = await res.json();

    if (!res.ok) {
      setStatus(data.error || 'Registration failed', 'error');
      return;
    }

    setStatus('Account created. Logging you in...', 'success');
    await login(username);
  } catch (e) {
    console.error(e);
    setStatus('Network error', 'error');
  }
}

document.getElementById('login-btn').addEventListener('click', () => {
  login(document.getElementById('login-username').value.trim());
});

document.getElementById('register-btn').addEventListener('click', () => {
  register(document.getElementById('register-username').value.trim());
});

// Default tab
showTab('login');
