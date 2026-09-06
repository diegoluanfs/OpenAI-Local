const modelSelect = document.querySelector('#model');
const form = document.querySelector('#ask-form');
const questionInput = document.querySelector('#question');
const messages = document.querySelector('#messages');
const sendButton = document.querySelector('#send-button');
const clearButton = document.querySelector('#clear-button');
const apiKeyInput = document.querySelector('#api-key');
const healthDot = document.querySelector('#health-dot');
const healthText = document.querySelector('#health-text');
const providerStatus = document.querySelector('#provider-status');
const defaultModel = document.querySelector('#default-model');
const latency = document.querySelector('#latency');

function addMessage(role, content) {
  const message = document.createElement('div');
  message.className = `message ${role}`;
  const roleLabel = role === 'user' ? 'You' : 'Local model';
  message.innerHTML = `<div class="role">${roleLabel}</div><div class="bubble"></div>`;
  message.querySelector('.bubble').textContent = content;
  messages.appendChild(message);
  messages.scrollTop = messages.scrollHeight;
}

function setHealth(online, text) {
  healthDot.className = `dot ${online ? 'ok' : 'bad'}`;
  healthText.textContent = text;
  providerStatus.textContent = online ? 'Ollama online' : 'Ollama offline';
}

async function loadStatus() {
  try {
    const [healthResponse, modelsResponse] = await Promise.all([
      fetch('/health'),
      fetch('/v1/models'),
    ]);
    if (!healthResponse.ok) throw new Error('Health check failed');
    const health = await healthResponse.json();
    setHealth(health.ollama_online, health.ollama_online ? 'Service online' : 'Ollama offline');
    defaultModel.textContent = health.default_model;
    const models = await modelsResponse.json();
    modelSelect.replaceChildren();
    const availableModels = models.data || [];
    availableModels.forEach((model) => {
      const option = document.createElement('option');
      option.value = model.id;
      option.textContent = model.id;
      option.selected = model.id === health.default_model;
      modelSelect.appendChild(option);
    });
    if (!availableModels.length) {
      const option = document.createElement('option');
      option.value = health.default_model;
      option.textContent = health.default_model;
      modelSelect.appendChild(option);
    }
  } catch (error) {
    setHealth(false, 'Service unavailable');
    defaultModel.textContent = 'Unavailable';
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;
  const startedAt = performance.now();
  addMessage('user', question);
  questionInput.value = '';
  sendButton.disabled = true;
  sendButton.querySelector('span').textContent = 'Thinking...';
  try {
    const headers = { 'Content-Type': 'application/json' };
    if (apiKeyInput.value.trim()) headers['X-API-Key'] = apiKeyInput.value.trim();
    const response = await fetch('/ask', {
      method: 'POST',
      headers,
      body: JSON.stringify({ question, model: modelSelect.value || undefined }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error?.message || 'Request failed');
    addMessage('assistant', payload.answer);
    latency.textContent = `${Math.round(performance.now() - startedAt)} ms · ${payload.model}`;
  } catch (error) {
    addMessage('assistant', `Unable to answer: ${error.message}`);
    latency.textContent = 'Request failed';
  } finally {
    sendButton.disabled = false;
    sendButton.querySelector('span').textContent = 'Send';
  }
});

clearButton.addEventListener('click', () => {
  messages.innerHTML = '<div class="welcome"><span class="welcome-kicker">READY TO THINK</span><h2>What would you like to explore?</h2><p>Ask a question and the local model will answer without leaving your environment.</p></div>';
  latency.textContent = 'Local · private · direct';
});

questionInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

loadStatus();
