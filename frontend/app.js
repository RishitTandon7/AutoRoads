/* ──────────────────────────────────────────
   OpenROAD AI Assistant – Frontend JS
   ────────────────────────────────────────── */

const API = window.location.origin;

// ── State ───────────────────────────────
let currentMode = "search";
let sidebarOpen = true;
let chatHistory = [];

// ── Quick prompts per mode ───────────────
const QUICK_PROMPTS = {
  search: [
    "What is the RTL-to-GDSII flow?",
    "How does FAISS vector search work?",
    "What is a technology LEF file?",
    "Explain OpenDB database"
  ],
  explain: [
    "Explain global_placement command",
    "Explain init_floorplan parameters",
    "Explain clock_tree_synthesis",
    "What does repair_design do?"
  ],
  generate_script: [
    "Complete RTL-to-GDSII flow script",
    "Generate floorplanning Tcl script",
    "Generate CTS script for Sky130",
    "Generate detailed routing script"
  ],
  debug: [
    "Error: insufficient routing resources",
    "Warning: utilization too high overflow",
    "Error: no clock found in CTS",
    "DRC violations after detailed routing"
  ],
  flow: [
    "Walk me through the full RTL-to-GDSII flow",
    "What happens during placement?",
    "How to set up Sky130 PDK for OpenROAD?",
    "What order should I run flow steps?"
  ]
};

const MODE_LABELS = {
  search:          "◈ Search",
  explain:         "◎ Explain",
  generate_script: "◆ Script",
  debug:           "⬡ Debug",
  flow:            "◉ Flow"
};

const TOPBAR_TITLES = {
  search:          "Documentation Search",
  explain:         "Command Explainer",
  generate_script: "Tcl Script Generator",
  debug:           "Error Debugger",
  flow:            "Flow Guidance"
};

// ── Init ─────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  updateQuickPrompts();
  checkStatus();
  setInterval(checkStatus, 15000);
  document.getElementById("queryInput").addEventListener("input", autoResize);
});

// ── Sidebar ──────────────────────────────
function toggleSidebar() {
  sidebarOpen = !sidebarOpen;
  document.getElementById("sidebar").classList.toggle("collapsed", !sidebarOpen);
}

// ── Mode switching ────────────────────────
function setMode(mode, btn) {
  currentMode = mode;
  document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  const label = MODE_LABELS[mode];
  document.getElementById("modeBadge").textContent = label;
  const pill = document.getElementById("modeBadgeInput");
  if (pill) pill.textContent = label.split(" ")[0]; // geometric symbol only
  document.getElementById("topbarTitle").textContent = TOPBAR_TITLES[mode];
  updateQuickPrompts();

  const debugPanel = document.getElementById("debugPanel");
  if (mode === "debug") {
    debugPanel.classList.add("open");
    document.getElementById("queryInput").placeholder = "Describe the error or ask about debugging…";
  } else {
    debugPanel.classList.remove("open");
    document.getElementById("queryInput").placeholder = "Ask about OpenROAD commands, flow stages, debugging…";
  }
}

function updateQuickPrompts() {
  const container = document.getElementById("quickPrompts");
  const prompts = QUICK_PROMPTS[currentMode] || [];
  container.innerHTML = prompts.map(p => `
    <button class="quick-btn" onclick="usePrompt(${JSON.stringify(p)})">${p}</button>
  `).join("");
}

function usePrompt(text) {
  const input = document.getElementById("queryInput");
  input.value = text;
  autoResize(input);
  input.focus();
  hideHero();
}

// ── Status check ─────────────────────────
async function checkStatus() {
  try {
    const res = await fetch(`${API}/api/status`);
    if (!res.ok) throw new Error(`${res.status}`);
    const data = await res.json();

    const ragDot    = document.getElementById("ragDot");
    const ragStatus = document.getElementById("ragStatus");
    ragDot.className    = data.rag_ready ? "sdot dot-ok" : "sdot dot-err";
    ragStatus.textContent = data.rag_ready ? "Ready" : "Not ready";

    const ollamaDot    = document.getElementById("ollamaDot");
    const ollamaStatus = document.getElementById("ollamaStatus");
    ollamaDot.className    = data.ollama_available ? "sdot dot-ok" : "sdot dot-warn";
    ollamaStatus.textContent = data.ollama_available ? data.ollama_model : "Offline";

    document.getElementById("docCount").textContent = `${data.doc_count} chunks`;
  } catch {
    document.getElementById("ragDot").className         = "sdot dot-err";
    document.getElementById("ollamaDot").className      = "sdot dot-err";
    document.getElementById("ragStatus").textContent    = "Offline";
    document.getElementById("ollamaStatus").textContent = "–";
  }
}

async function parseApiResponse(res) {
  let data = {};
  try {
    data = await res.json();
  } catch {
    if (!res.ok) throw new Error(`Request failed with status ${res.status}`);
    return {};
  }
  if (!res.ok) {
    throw new Error(data.detail || data.message || data.error || `Request failed with status ${res.status}`);
  }
  return data;
}

// ── Hero visibility ───────────────────────
function hideHero() {
  const hero = document.getElementById("hero");
  if (hero) hero.style.display = "none";
}

// ── Auto-resize textarea ──────────────────
function autoResize(el) {
  if (typeof el === "object" && el.target) el = el.target;
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 150) + "px";
}

// ── Keyboard shortcut ─────────────────────
function handleKeyDown(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendQuery();
  }
}

// ── Main query handler ────────────────────
async function sendQuery() {
  const input = document.getElementById("queryInput");
  const query = input.value.trim();
  if (!query) return;

  hideHero();
  input.value = "";
  input.style.height = "auto";
  disableSend(true);

  const topK = parseInt(document.getElementById("topK").value) || 5;
  appendUserMessage(query);
  const thinkingId = appendThinking();

  try {
    const res  = await fetch(`${API}/api/query`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ query, task_type: currentMode, top_k: topK })
    });
    const data = await parseApiResponse(res);
    removeThinking(thinkingId);
    appendAIMessage(data);
  } catch (err) {
    removeThinking(thinkingId);
    appendError(err.message || "Could not reach the backend. Make sure the server is running.");
  } finally {
    disableSend(false);
    input.focus();
  }
}

// ── Debug submit ──────────────────────────
async function submitDebug() {
  const logText = document.getElementById("logInput").value.trim();
  const query   = document.getElementById("queryInput").value.trim() || "Analyze this error";

  if (!logText && !query) { showToast("Please paste a log or describe the error."); return; }

  hideHero();
  disableSend(true);
  const thinkingId = appendThinking();

  try {
    const combined = logText ? `${query}\n\nLog:\n${logText}` : query;
    const res  = await fetch(`${API}/api/query`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ query: combined, task_type: "debug", top_k: 4 })
    });
    const data = await parseApiResponse(res);
    appendUserMessage(query + (logText ? `\n\n\`\`\`\n${logText.slice(0, 300)}…\n\`\`\`` : ""));
    removeThinking(thinkingId);
    appendAIMessage(data);
    document.getElementById("logInput").value  = "";
    document.getElementById("queryInput").value = "";
  } catch (err) {
    removeThinking(thinkingId);
    appendError(err.message || "Backend unreachable. Check if the server is running.");
  } finally {
    disableSend(false);
  }
}

// ── DOM helpers ───────────────────────────
function disableSend(state) {
  document.getElementById("sendBtn").disabled = state;
}

function getTime() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function appendUserMessage(text) {
  const chat = document.getElementById("chatContainer");
  const id   = "msg_" + Date.now();
  chat.insertAdjacentHTML("beforeend", `
    <div class="message user" id="${id}">
      <div class="msg-avatar user-avatar">You</div>
      <div class="msg-body">
        <div class="msg-header">
          <span class="msg-name">You</span>
          <span class="msg-time">${getTime()}</span>
        </div>
        <div class="msg-bubble">${escapeHtml(text).replace(/\n/g, "<br>")}</div>
      </div>
    </div>`);
  scrollToBottom();
  return id;
}

function appendThinking() {
  const chat = document.getElementById("chatContainer");
  const id   = "think_" + Date.now();
  chat.insertAdjacentHTML("beforeend", `
    <div class="message ai" id="${id}">
      <div class="msg-avatar ai-avatar">🤖</div>
      <div class="msg-body">
        <div class="msg-header"><span class="msg-name">OpenROAD AI</span></div>
        <div class="msg-bubble thinking">
          <div class="dots">
            <div class="dot"></div><div class="dot"></div><div class="dot"></div>
          </div>
          <span>Searching knowledge base &amp; generating response…</span>
        </div>
      </div>
    </div>`);
  scrollToBottom();
  return id;
}

function removeThinking(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function appendAIMessage(data) {
  const chat = document.getElementById("chatContainer");
  const id   = "msg_" + Date.now();

  const renderedAnswer = renderMarkdown(data.answer || "No response.");

  // Sources HTML
  let sourcesHtml = "";
  if (data.sources && data.sources.length > 0) {
    const items = data.sources.map(s => `
      <div class="source-item">
        <div class="source-title">${escapeHtml(s.title)}</div>
        <div class="source-meta">
          <span class="source-cat">${s.category}</span>
          <span class="source-score">Score: ${s.score}</span>
        </div>
        ${s.snippet ? `<div class="source-snippet">${escapeHtml(s.snippet.slice(0, 180))}…</div>` : ""}
      </div>`).join("");

    sourcesHtml = `
      <div class="sources-panel" id="sp_${id}">
        <button class="sources-header" onclick="toggleSources(this)">
          <span>📚 ${data.sources.length} Source${data.sources.length !== 1 ? "s" : ""} Retrieved</span>
          <span class="sources-arrow">▶</span>
        </button>
        <div class="sources-list">${items}</div>
      </div>`;
  }

  const ollamaWarning = data.ollama_available ? "" : `
    <div class="ollama-warn">
      ⚠️ Ollama LLM offline – showing retrieved documentation. Run <code>ollama serve</code> for AI responses.
    </div>`;

  const statsHtml = `
    <div class="msg-stats">
      <span class="stat-item">⏱ ${data.processing_time}s</span>
      <span class="stat-item">📄 ${(data.sources || []).length} docs</span>
      <span class="stat-item">🤖 ${data.ollama_available ? "LLM response" : "RAG-only"}</span>
    </div>`;

  chat.insertAdjacentHTML("beforeend", `
    <div class="message ai" id="${id}">
      <div class="msg-avatar ai-avatar">🤖</div>
      <div class="msg-body">
        <div class="msg-header">
          <span class="msg-name">OpenROAD AI</span>
          <span class="msg-mode-tag">${MODE_LABELS[currentMode]}</span>
          <span class="msg-time">${getTime()}</span>
        </div>
        <div class="msg-bubble">
          ${renderedAnswer}
          ${ollamaWarning}
        </div>
        ${statsHtml}
        ${sourcesHtml}
      </div>
    </div>`);

  // ── Per-block Copy + Run buttons
  const allPres = document.querySelectorAll(`#${id} pre`);
  allPres.forEach(pre => {
    const code = pre.querySelector("code") || pre;
    pre.style.position = "relative";

    // Copy button
    const copyBtn = document.createElement("button");
    copyBtn.className = "copy-btn";
    copyBtn.textContent = "Copy";
    copyBtn.onclick = () => {
      navigator.clipboard.writeText(code.innerText).then(() => {
        copyBtn.textContent = "✓ Copied";
        setTimeout(() => { copyBtn.textContent = "Copy"; }, 2000);
      });
    };
    pre.appendChild(copyBtn);

    // ⚡ Single Run button
    const runBtn = document.createElement("button");
    runBtn.className = "single-run-btn";
    runBtn.textContent = "⚡ Run";
    runBtn.title = "Execute this code block (auto-installs missing packages)";
    runBtn.onclick = () => singleRun(code.innerText.trim(), runBtn);
    pre.appendChild(runBtn);
  });

  // ── Run All bar
  if (allPres.length > 0) {
    const msgBody  = document.querySelector(`#${id} .msg-body`);
    const runAllBar = document.createElement("div");
    runAllBar.className = "run-all-bar";
    runAllBar.innerHTML = `
      <span class="run-all-info">
        ${allPres.length} code block${allPres.length > 1 ? "s" : ""} — run individually or all at once
      </span>
      <button class="run-all-btn" id="runall_${id}">⚡ Run All on System</button>`;
    msgBody.appendChild(runAllBar);

    document.getElementById(`runall_${id}`).addEventListener("click", function () {
      const allCode = [...document.querySelectorAll(`#${id} pre`)]
        .map(p => (p.querySelector("code") || p).innerText.trim())
        .filter(Boolean)
        .join("\n\n");
      runAllOnSystem(allCode, this);
    });
  }

  scrollToBottom();
  return id;
}

function appendError(msg) {
  const chat = document.getElementById("chatContainer");
  chat.insertAdjacentHTML("beforeend", `
    <div class="message ai">
      <div class="msg-avatar ai-avatar">⚠️</div>
      <div class="msg-body error-body">
        <div class="msg-bubble">
          <strong class="error-title">Error</strong><br>${escapeHtml(msg)}
        </div>
      </div>
    </div>`);
  scrollToBottom();
}

// ── ⚡ Run All on System ──────────────────
async function runAllOnSystem(script, btn) {
  const original = btn.textContent;
  btn.textContent = "⏳ Running…";
  btn.disabled    = true;
  hideHero();

  const lineCount = script.split("\n").length;
  appendUserMessage(`⚡ Run All (${lineCount} lines):\n\`\`\`\n${script.slice(0, 600)}${script.length > 600 ? "\n… (truncated)" : ""}\n\`\`\``);
  const thinkingId = appendThinking();

  try {
    const res  = await fetch(`${API}/api/execute`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ script })
    });
    const data = await parseApiResponse(res);
    removeThinking(thinkingId);
    insertTerminalBlock(data, "⚡ Run All", "rgba(139,92,246,0.3)", "rgba(139,92,246,0.15)", "#a78bfa");
    scrollToBottom();
  } catch (err) {
    removeThinking(thinkingId);
    appendError(err.message || "Execution failed — make sure the backend server is running.");
  } finally {
    btn.textContent = original;
    btn.disabled    = false;
  }
}

// ── ⚡ Single Run ─────────────────────────
async function singleRun(codeText, runBtn) {
  const original = runBtn.textContent;
  runBtn.textContent = "⏳ Running…";
  runBtn.disabled    = true;
  hideHero();

  appendUserMessage(`⚡ Single Run:\n\`\`\`\n${codeText.trim()}\n\`\`\``);
  const thinkingId = appendThinking();

  try {
    const res  = await fetch(`${API}/api/single-run`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ snippet: codeText })
    });
    const data = await parseApiResponse(res);
    removeThinking(thinkingId);

    // Enrich data with language/pkg badges for the shared renderer
    data._extra = [];
    if (data.language) data._extra.push(`<span class="term-badge lang-badge">🔤 ${escapeHtml(data.language)}</span>`);
    if (data.installed_packages && data.installed_packages.length > 0)
      data._extra.push(`<span class="term-badge pkg-badge">📦 Auto-installed: ${data.installed_packages.map(p => escapeHtml(p)).join(", ")}</span>`);

    insertTerminalBlock(data, "⚡ Single Run", "rgba(16,185,129,0.3)", "rgba(16,185,129,0.1)", "#34d399");
    scrollToBottom();
  } catch (err) {
    removeThinking(thinkingId);
    appendError(err.message || "Single Run failed — make sure the backend is running.");
  } finally {
    runBtn.textContent = original;
    runBtn.disabled    = false;
  }
}

// ── Shared terminal block renderer ────────
function insertTerminalBlock(data, label, borderColor, bgAccent, accentColor) {
  const success = data.success;
  const exitIcon = success ? "✅" : "❌";

  const pdkBadge = data.pdk_root
    ? `<span class="term-badge pdk-badge">📦 PDK: ${escapeHtml(data.pdk_root.split(/[/\\]/).pop())}</span>`
    : "";

  const extraBadges = (data._extra || []).join("");

  const stdoutBlock = data.stdout
    ? `<div class="term-section">
         <div class="term-label">STDOUT</div>
         <pre class="term-output">${escapeHtml(data.stdout)}</pre>
       </div>` : "";

  const stderrBlock = data.stderr
    ? `<div class="term-section">
         <div class="term-label err-label">STDERR</div>
         <pre class="term-output term-err">${escapeHtml(data.stderr)}</pre>
       </div>` : "";

  const noOutput = !data.stdout && !data.stderr
    ? `<div class="term-no-output">(no output)</div>` : "";

  const chat = document.getElementById("chatContainer");
  chat.insertAdjacentHTML("beforeend", `
    <div class="message ai terminal-msg">
      <div class="msg-avatar ai-avatar">⚡</div>
      <div class="msg-body term-msg-body" style="border-color:${borderColor};background:linear-gradient(180deg,rgba(10,14,26,0.97) 0%,rgba(8,12,20,0.99) 100%);">
        <div class="msg-header">
          <span class="msg-name">System Execution</span>
          <span class="msg-mode-tag" style="background:${bgAccent};color:${accentColor};">${label}</span>
          <span class="msg-time">${getTime()}</span>
        </div>
        <div class="term-card">
          <div class="term-header">
            <span class="term-exit">${exitIcon} Exit ${data.exit_code}</span>
            <span class="term-exec">executor: <strong>${escapeHtml(data.executor || "auto")}</strong></span>
            ${pdkBadge}
            ${extraBadges}
            <span class="term-elapsed">⏱ ${data.elapsed}s</span>
          </div>
          ${stdoutBlock}
          ${stderrBlock}
          ${noOutput}
        </div>
      </div>
    </div>`);
}

// ── Sources toggle ────────────────────────
function toggleSources(btn) {
  const panel = btn.closest(".sources-panel");
  const list  = panel.querySelector(".sources-list");
  const arrow = btn.querySelector(".sources-arrow");
  const isOpen = panel.classList.toggle("open");
  list.style.display   = isOpen ? "flex" : "none";
  arrow.textContent    = isOpen ? "▼" : "▶";
}

function clearChat() {
  document.getElementById("chatContainer").innerHTML = "";
  document.getElementById("hero").style.display = "";
  chatHistory = [];
}

function scrollToBottom() {
  const chat = document.getElementById("chatContainer");
  setTimeout(() => { chat.scrollTop = chat.scrollHeight; }, 50);
}

function showToast(msg, duration = 3000) {
  const toast = document.createElement("div");
  toast.className   = "toast";
  toast.textContent = msg;
  document.body.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add("toast-show"));
  setTimeout(() => {
    toast.classList.remove("toast-show");
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ── Markdown renderer ─────────────────────
function renderMarkdown(text) {
  if (!text) return "";
  let html = escapeHtml(text);

  const fencedBlocks = [];
  const inlineCodes  = [];

  // Fence code blocks first (protect from further processing)
  html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) => {
    const token = `__CODE_BLOCK_${fencedBlocks.length}__`;
    fencedBlocks.push(`<pre><code class="lang-${lang}">${code.trim()}</code></pre>`);
    return token;
  });

  // Inline code
  html = html.replace(/`([^`\n]+)`/g, (_, code) => {
    const token = `__INLINE_CODE_${inlineCodes.length}__`;
    inlineCodes.push(`<code>${code}</code>`);
    return token;
  });

  // Headers
  html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
  html = html.replace(/^## (.+)$/gm,  "<h2>$1</h2>");
  html = html.replace(/^# (.+)$/gm,   "<h1>$1</h1>");

  // Blockquote
  html = html.replace(/^&gt; (.+)$/gm, "<blockquote>$1</blockquote>");

  // HR
  html = html.replace(/^---+$/gm, "<hr>");

  // Bold / italic
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/(^|[\s(])\*(?!\s)([^*\n]+?)\*(?=[\s).,!?:;]|$)/g, "$1<em>$2</em>");

  // Unordered lists
  html = html.replace(/(?:^|\n)([-*•] .+(?:\n[-*•] .+)*)/g, match => {
    const items = match.trim().split("\n")
      .map(line => `<li>${line.replace(/^[-*•] /, "")}</li>`)
      .join("");
    return `\n<ul>${items}</ul>`;
  });

  // Ordered lists
  html = html.replace(/(?:^|\n)((?:\d+\. .+(?:\n|$))+)/g, match => {
    const items = match.trim().split("\n")
      .map(line => `<li>${line.replace(/^\d+\. /, "")}</li>`)
      .join("");
    return `\n<ol>${items}</ol>`;
  });

  // Paragraphs
  html = html
    .split(/\n{2,}/)
    .map(part => part.trim())
    .filter(Boolean)
    .map(part => {
      if (/^<(?:h[1-6]|ul|ol|pre|blockquote|hr)/.test(part)) return part;
      return `<p>${part.replace(/\n/g, "<br>")}</p>`;
    })
    .join("");

  // Restore tokens
  fencedBlocks.forEach((block, i) => {
    html = html.replace(`__CODE_BLOCK_${i}__`, block);
  });
  inlineCodes.forEach((code, i) => {
    html = html.replaceAll(`__INLINE_CODE_${i}__`, code);
  });

  return html;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
