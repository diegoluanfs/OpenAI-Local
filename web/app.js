const modelSelect = document.querySelector('#model');
const form = document.querySelector('#ask-form');
const questionInput = document.querySelector('#question');
const messages = document.querySelector('#messages');
const sendButton = document.querySelector('#send-button');
const clearButton = document.querySelector('#clear-button');
const exportButton = document.querySelector('#export-button');
const apiKeyInput = document.querySelector('#api-key');
const healthDot = document.querySelector('#health-dot');
const healthText = document.querySelector('#health-text');
const providerStatus = document.querySelector('#provider-status');
const defaultModel = document.querySelector('#default-model');
const memoryStatus = document.querySelector('#memory-status');
const refreshModels = document.querySelector('#refresh-models');
const latency = document.querySelector('#latency');
const requestCount = document.querySelector('#request-count');
const inferenceCount = document.querySelector('#inference-count');
const latencyStatus = document.querySelector('#latency-status');
const streamToggle = document.querySelector('#stream-toggle');
const conversationStorageKey = 'local-llm:conversation';
const maxStoredMessages = 100;

function restorePreferences() {
  modelSelect.value = localStorage.getItem('local-llm:model') || '';
  streamToggle.checked = localStorage.getItem('local-llm:stream') === 'true';
}

function savePreferences() {
  if (modelSelect.value) localStorage.setItem('local-llm:model', modelSelect.value);
  localStorage.setItem('local-llm:stream', String(streamToggle.checked));
}

function saveConversation() {
  const transcript = [...messages.querySelectorAll('.message')].map((message) => ({
    role: message.classList.contains('user') ? 'user' : 'assistant',
    content: message.querySelector('.bubble').textContent,
  })).slice(-maxStoredMessages);
  localStorage.setItem(conversationStorageKey, JSON.stringify(transcript));
}

function restoreConversation() {
  try {
    const transcript = JSON.parse(localStorage.getItem(conversationStorageKey) || '[]');
    transcript.slice(-maxStoredMessages).forEach(({ role, content }) => addMessage(role, content));
  } catch {
    localStorage.removeItem(conversationStorageKey);
  }
}

function getConversation() {
  return JSON.parse(localStorage.getItem(conversationStorageKey) || '[]');
}

function addMessage(role, content) {
  const message = document.createElement('div');
  message.className = `message ${role}`;
  const roleLabel = role === 'user' ? 'You' : 'Local model';
  message.innerHTML = `<div class="role">${roleLabel}</div><div class="bubble"></div>`;
  message.querySelector('.bubble').textContent = content;
  messages.appendChild(message);
  messages.scrollTop = messages.scrollHeight;
  saveConversation();
  return message.querySelector('.bubble');
}

async function streamChat(question, headers, model) {
  const response = await fetch('/v1/chat/completions', {
    method: 'POST',
    headers,
    body: JSON.stringify({
      question,
      model,
      messages: [{ role: 'user', content: question }],
      stream: true,
    }),
  });
  if (!response.ok || !response.body) {
    const payload = await response.json();
    throw new Error(payload.error?.message || 'Streaming request failed');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let answer = '';
  const bubble = addMessage('assistant', '');
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split('\n\n');
    buffer = events.pop() || '';
    events.forEach((event) => {
      const line = event.split('\n').find((item) => item.startsWith('data: '));
      if (!line || line === 'data: [DONE]') return;
      try {
        const payload = JSON.parse(line.slice(6));
        answer += payload.choices?.[0]?.delta?.content || '';
        bubble.textContent = answer;
        messages.scrollTop = messages.scrollHeight;
      } catch {
        // Ignore incomplete SSE frames.
      }
    });
  }
  saveConversation();
}

function setHealth(online, text) {
  healthDot.className = `dot ${online ? 'ok' : 'bad'}`;
  healthText.textContent = text;
  providerStatus.textContent = online ? 'Ollama online' : 'Ollama offline';
}

function metricValue(metrics, name) {
  const match = metrics.match(new RegExp(`^${name}(?:\\{[^\\n]*\\})?\\s+([0-9.e+-]+)$`, 'm'));
  return match ? Number(match[1]) : 0;
}

async function loadMetrics() {
  try {
    const response = await fetch('/metrics');
    if (!response.ok) return;
    const metrics = await response.text();
    const requests = metricValue(metrics, 'local_llm_requests_total');
    const inferences = metricValue(metrics, 'local_llm_inference_requests_total');
    const duration = metricValue(metrics, 'local_llm_request_duration_seconds_sum');
    const count = metricValue(metrics, 'local_llm_request_duration_seconds_count');
    requestCount.textContent = requests.toLocaleString('en-US');
    inferenceCount.textContent = inferences.toLocaleString('en-US');
    latencyStatus.textContent = count ? `${Math.round((duration / count) * 1000)} ms` : '—';
  } catch {
    requestCount.textContent = '—';
    inferenceCount.textContent = '—';
    latencyStatus.textContent = '—';
  }
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
    memoryStatus.textContent = `${health.memory_used_mb} MB`;
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
    const savedModel = localStorage.getItem('local-llm:model');
    if (savedModel && [...modelSelect.options].some((option) => option.value === savedModel)) {
      modelSelect.value = savedModel;
    }
  } catch (error) {
    setHealth(false, 'Service unavailable');
    defaultModel.textContent = 'Unavailable';
  }
}

refreshModels.addEventListener('click', async () => {
  refreshModels.disabled = true;
  try {
    await loadStatus();
    await loadMetrics();
  } finally {
    refreshModels.disabled = false;
  }
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;
  savePreferences();
  const startedAt = performance.now();
  addMessage('user', question);
  questionInput.value = '';
  sendButton.disabled = true;
  sendButton.querySelector('span').textContent = 'Thinking...';
  try {
    const headers = { 'Content-Type': 'application/json' };
    if (apiKeyInput.value.trim()) headers['X-API-Key'] = apiKeyInput.value.trim();
    if (streamToggle.checked) {
      await streamChat(question, headers, modelSelect.value || undefined);
      latency.textContent = `${Math.round(performance.now() - startedAt)} ms · streaming`;
      return;
    }
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

modelSelect.addEventListener('change', savePreferences);
streamToggle.addEventListener('change', savePreferences);

clearButton.addEventListener('click', () => {
  messages.innerHTML = '<div class="welcome"><span class="welcome-kicker">READY TO THINK</span><h2>What would you like to explore?</h2><p>Ask a question and the local model will answer without leaving your environment.</p></div>';
  localStorage.removeItem(conversationStorageKey);
  latency.textContent = 'Local · private · direct';
});

exportButton.addEventListener('click', () => {
  const conversation = getConversation();
  if (!conversation.length) return;
  const blob = new Blob([JSON.stringify(conversation, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `local-llm-conversation-${new Date().toISOString().slice(0, 10)}.json`;
  link.click();
  URL.revokeObjectURL(url);
});

questionInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

loadStatus();
loadMetrics();
restorePreferences();
restoreConversation();
