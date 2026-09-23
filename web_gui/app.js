// ================= ESTADO GLOBAL DA INTERFACE =================
let aiState = "listening"; // "listening", "thinking", "speaking"
let ws = null;
let timeStep = 0;

// ================= RELÓGIO HUD =================
function updateClock() {
    const now = new Date();
    const timeStr = now.toTimeString().split(' ')[0];
    document.getElementById('localTime').textContent = timeStr;
}
setInterval(updateClock, 1000);
updateClock();

// ================= CANVASES E ANIMAÇÕES =================
const eyesCanvas = document.getElementById('robotEyesCanvas');
const eyesCtx = eyesCanvas.getContext('2d');

const ecgCanvas = document.getElementById('ecgCanvas');
const ecgCtx = ecgCanvas.getContext('2d');

const barsCanvas = document.getElementById('barsCanvas');
const barsCtx = barsCanvas.getContext('2d');

const waveCanvas = document.getElementById('audioWaveCanvas');
const waveCtx = waveCanvas.getContext('2d');

const miniEyesCanvas = document.getElementById('miniEyesCanvas');
const miniEyesCtx = miniEyesCanvas ? miniEyesCanvas.getContext('2d') : null;

// --- 1. OLHOS DO ROBÔ OLED (CENTRO DO RADAR) ---
function drawRoundedRect(ctx, x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
    ctx.fill();
}

function animateRobotEyes() {
    eyesCtx.clearRect(0, 0, eyesCanvas.width, eyesCanvas.height);
    timeStep++;

    const cx = eyesCanvas.width / 2;
    const cy = eyesCanvas.height / 2;

    let eyeColor = "#00F0FF";
    let eyeWidth = 38;
    let eyeHeight = 52;
    const eyeGap = 26;
    let offsetY = 0;
    let offsetX = 0;

    if (aiState === "thinking") {
        eyeColor = "#F59E0B"; // Âmbar neural
        eyeHeight = 22 + Math.sin(timeStep * 0.25) * 6;
        offsetX = Math.cos(timeStep * 0.15) * 12;
    } else if (aiState === "speaking") {
        eyeColor = "#38BDF8"; // Azul neon pulsante
        eyeHeight = 46 + Math.sin(timeStep * 0.8) * 10;
        offsetY = Math.sin(timeStep * 0.4) * 3;
    } else {
        // Listening: Piscadela e movimento orgânico
        if (timeStep % 90 < 4) {
            eyeHeight = 5; // Pisca
        } else {
            offsetY = Math.sin(timeStep * 0.05) * 3;
            offsetX = Math.sin(timeStep * 0.02) * 5;
        }
    }

    eyesCtx.fillStyle = eyeColor;
    eyesCtx.shadowColor = eyeColor;
    eyesCtx.shadowBlur = 12;

    // Olho Esquerdo
    const leftX = (cx - eyeWidth - eyeGap / 2) + offsetX;
    const leftY = (cy - eyeHeight / 2) + offsetY;
    drawRoundedRect(eyesCtx, leftX, leftY, eyeWidth, eyeHeight, 10);

    // Olho Direito
    const rightX = (cx + eyeGap / 2) + offsetX;
    const rightY = (cy - eyeHeight / 2) + offsetY;
    drawRoundedRect(eyesCtx, rightX, rightY, eyeWidth, eyeHeight, 10);

    // Sincroniza em tempo real com o mini canvas flutuante
    if (miniEyesCtx && miniEyesCanvas) {
        miniEyesCtx.clearRect(0, 0, miniEyesCanvas.width, miniEyesCanvas.height);
        miniEyesCtx.drawImage(eyesCanvas, 0, 0, eyesCanvas.width, eyesCanvas.height, 0, 0, miniEyesCanvas.width, miniEyesCanvas.height);
    }

    requestAnimationFrame(animateRobotEyes);
}
requestAnimationFrame(animateRobotEyes);

// --- 2. ECG WAVEFORM (BATIMENTOS CARDÍACOS) ---
let ecgX = 0;
let lastEcgY = 22;
ecgCtx.strokeStyle = "#00F0FF";
ecgCtx.lineWidth = 1.5;
ecgCtx.shadowColor = "#00F0FF";
ecgCtx.shadowBlur = 6;

function animateECG() {
    ecgCtx.fillStyle = 'rgba(6, 14, 26, 0.05)';
    ecgCtx.fillRect(0, 0, ecgCanvas.width, ecgCanvas.height);

    let targetY = 22;
    // Padrão de pico cardíaco a cada ciclo
    const cycle = ecgX % 70;
    if (cycle === 30) targetY = 8;
    else if (cycle === 34) targetY = 38;
    else if (cycle === 38) targetY = 15;
    else targetY = 22 + (Math.random() - 0.5) * 3;

    ecgCtx.beginPath();
    ecgCtx.moveTo(ecgX, lastEcgY);
    ecgCtx.lineTo(ecgX + 2, targetY);
    ecgCtx.stroke();

    lastEcgY = targetY;
    ecgX += 2;
    if (ecgX > ecgCanvas.width) {
        ecgX = 0;
        ecgCtx.clearRect(0, 0, ecgCanvas.width, ecgCanvas.height);
    }

    setTimeout(animateECG, 40);
}
animateECG();

// --- 3. BARRAS DE FREQUÊNCIA DE ÁUDIO ---
const numBars = 22;
function animateSoundBars() {
    barsCtx.clearRect(0, 0, barsCanvas.width, barsCanvas.height);
    const barWidth = 8;
    const gap = 4;
    const startX = (barsCanvas.width - (numBars * (barWidth + gap))) / 2;

    for (let i = 0; i < numBars; i++) {
        let barHeight = 6;
        if (aiState === "speaking") {
            barHeight = 6 + Math.abs(Math.sin(timeStep * 0.2 + i * 0.4)) * 28;
        } else if (aiState === "thinking") {
            barHeight = 4 + Math.abs(Math.sin(timeStep * 0.1 + i * 0.2)) * 14;
        } else {
            barHeight = 3 + Math.abs(Math.sin(timeStep * 0.04 + i * 0.3)) * 8;
        }

        const x = startX + i * (barWidth + gap);
        const y = barsCanvas.height - barHeight;

        barsCtx.fillStyle = i % 2 === 0 ? "#00F0FF" : "#0284C7";
        barsCtx.shadowColor = "#00F0FF";
        barsCtx.shadowBlur = 4;
        barsCtx.fillRect(x, y, barWidth, barHeight);
    }

    // Onda central abaixo do radar
    waveCtx.clearRect(0, 0, waveCanvas.width, waveCanvas.height);
    const waveBars = 16;
    const wWidth = 6;
    const wGap = 4;
    const wStartX = (waveCanvas.width - (waveBars * (wWidth + wGap))) / 2;

    for (let j = 0; j < waveBars; j++) {
        let h = 4;
        if (aiState === "speaking") {
            h = 4 + Math.abs(Math.cos(timeStep * 0.25 + j * 0.5)) * 20;
        }
        const wx = wStartX + j * (wWidth + wGap);
        const wy = (waveCanvas.height - h) / 2;
        waveCtx.fillStyle = "#00F0FF";
        waveCtx.shadowColor = "#00F0FF";
        waveCtx.shadowBlur = 5;
        waveCtx.fillRect(wx, wy, wWidth, h);
    }

    setTimeout(animateSoundBars, 50);
}
animateSoundBars();

// ================= ATUALIZAÇÃO VISUAL DE ESTADO =================
function updateAIState(newState) {
    aiState = newState;
    const statusText = document.getElementById('statusText');
    const pill = document.getElementById('micPill');
    const pillText = document.getElementById('micPillText');

    pill.className = "awaiting-pill";

    if (newState === "listening") {
        statusText.textContent = "OPTIMAL";
        statusText.className = "status-value status-optimal";
        pillText.textContent = "AWAITING COMMAND...";
    } else if (newState === "thinking") {
        statusText.textContent = "PROCESSING";
        statusText.style.color = "#F59E0B";
        pill.classList.add("thinking");
        pillText.textContent = "⚡ PROCESSANDO ÁUDIO...";
    } else if (newState === "speaking") {
        statusText.textContent = "AUDIO OUTPUT";
        statusText.style.color = "#38BDF8";
        pill.classList.add("speaking");
        pillText.textContent = "🔊 TRANSMITINDO VOZ...";
    }
}

// ================= WEBSOCKET COM PYTHON (BACKEND) =================
function connectWebSocket() {
    const wsUrl = `ws://${window.location.host}/ws`;
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log("⚡ [ARES WebSocket] Conectado ao núcleo com sucesso.");
        appendTerminalLine("SYSTEM LINK // ESTABLISHED", "success-line");
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handleIncomingData(data);
        } catch (e) {
            console.error("Erro ao decodificar mensagem do socket:", e);
        }
    };

    ws.onclose = () => {
        console.warn("⚠️ [ARES WebSocket] Conexão perdida. Reconectando em 2s...");
        setTimeout(connectWebSocket, 2000);
    };

    ws.onerror = (err) => {
        ws.close();
    };
}

function handleIncomingData(data) {
    if (data.type === "state") {
        updateAIState(data.state);
    }
    
    if (data.type === "stats") {
        if (data.cpu !== undefined) {
            document.getElementById('cpuText').textContent = `${data.cpu}%`;
            document.getElementById('cpuBar').style.width = `${data.cpu}%`;
        }
        if (data.ram !== undefined) {
            document.getElementById('ramText').textContent = `${data.ram}%`;
            document.getElementById('ramBar').style.width = `${data.ram}%`;
        }
        if (data.apps !== undefined) {
            document.getElementById('activeAppsCount').textContent = `APPS: ${data.apps}`;
        }
        if (data.weather !== undefined) {
            document.getElementById('weatherText').textContent = data.weather;
        }
    }

    if (data.type === "chat") {
        appendTerminalLine(`[${data.speaker}] ${data.message}`, data.speaker === "VOCÊ" ? "user-line" : "ares-line");
    }

    if (data.type === "terminal") {
        appendTerminalLine(data.message, "prompt-line");
    }

    if (data.type === "agents") {
        renderSubAgents(data.agents);
    }

    if (data.type === "apps_list") {
        renderActiveApps(data.apps);
    }
}

function appendTerminalLine(text, cssClass = "") {
    const box = document.getElementById('terminalDisplay');
    if (!box) return;
    const div = document.createElement('div');
    div.className = `term-line ${cssClass}`;
    div.textContent = text;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

// ================= RENDERIZADOR DE APLICATIVOS ATIVOS (UP-LINK) =================
function renderActiveApps(apps) {
    const list = document.getElementById('activeAppsList');
    const countEl = document.getElementById('activeAppsCount');
    if (countEl) countEl.textContent = `${apps ? apps.length : 0} APPS`;
    if (!list) return;

    list.innerHTML = "";
    if (!apps || apps.length === 0) {
        list.innerHTML = `<div class="empty-apps-msg">Nenhum aplicativo do usuário detectado no momento.</div>`;
        return;
    }

    apps.forEach(app => {
        const row = document.createElement('div');
        row.className = "app-item-row";
        row.innerHTML = `
            <div class="app-info-left">
                <span class="app-dot"></span>
                <span class="app-name-tag" title="${app.name} (${app.raw_name})">${app.name}</span>
            </div>
            <div class="app-info-right">
                <span class="app-pid-tag">PID: ${app.pid}</span>
                <button class="btn-kill-app" onclick="killProcess(${app.pid}, '${app.name}')" title="Encerrar processo agora">ENCERRAR</button>
            </div>
        `;
        list.appendChild(row);
    });
}

window.killProcess = function(pid, name) {
    if (!confirm(`Deseja realmente encerrar "${name}" (PID: ${pid})?`)) return;
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "kill_process", pid: pid, name: name }));
        appendTerminalLine(`[SISTEMA] Solicitando encerramento do processo '${name}' (PID: ${pid})...`, "prompt-line");
    }
};

// ================= RENDERIZADOR DE SUB-AGENTES =================
function renderSubAgents(agents) {
    const list = document.getElementById('subAgentsList');
    const badge = document.getElementById('agentsCountBadge');
    if (badge) badge.textContent = `${agents ? agents.length : 0} AGENTS`;
    if (!list) return;

    list.innerHTML = "";
    if (!agents || agents.length === 0) {
        list.innerHTML = `<div class="empty-agents-msg">Nenhum sub-agente em segundo plano no momento.</div>`;
        return;
    }

    agents.forEach(a => {
        const card = document.createElement('div');
        card.className = "agent-item-card";

        const badgeClass = a.status === "running" ? "badge-running" : (a.status === "completed" ? "badge-completed" : "badge-stopped");
        const statusLabel = a.status === "running" ? "● RODANDO" : (a.status === "completed" ? "✔ PRONTO" : "■ PARADO");

        card.innerHTML = `
            <div class="agent-item-header">
                <span>🤖 ${a.name} (${a.id})</span>
                <span class="agent-badge ${badgeClass}">${statusLabel}</span>
            </div>
            <div class="agent-task">Tarefa: ${a.task}</div>
            <div class="agent-log">${a.last_log || "Aguardando..."}</div>
        `;
        list.appendChild(card);
    });
}

// ================= ANEXO DE IMAGEM & TERMINAL =================
let attachedImageData = null;
const imageFileInput = document.getElementById('imageFileInput');
const btnAttachImg = document.getElementById('btnAttachImg');
const attachedImgPreview = document.getElementById('attachedImgPreview');
const imgThumbnail = document.getElementById('imgThumbnail');
const imgPreviewName = document.getElementById('imgPreviewName');
const btnRemoveImg = document.getElementById('btnRemoveImg');

if (btnAttachImg && imageFileInput) {
    btnAttachImg.addEventListener('click', () => imageFileInput.click());
    imageFileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleImageFile(file);
    });
}

function handleImageFile(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        attachedImageData = e.target.result;
        if (imgThumbnail) imgThumbnail.src = attachedImageData;
        if (imgPreviewName) imgPreviewName.textContent = file.name || "imagem_anexada.png";
        if (attachedImgPreview) attachedImgPreview.style.display = "flex";
        appendTerminalLine(`[SISTEMA] Imagem carregada: ${file.name || 'clipboard'}`, "prompt-line");
    };
    reader.readAsDataURL(file);
}

if (btnRemoveImg) {
    btnRemoveImg.addEventListener('click', () => {
        attachedImageData = null;
        if (imageFileInput) imageFileInput.value = "";
        if (attachedImgPreview) attachedImgPreview.style.display = "none";
    });
}

// Suporte global para colar imagens com Ctrl+V
window.addEventListener('paste', (e) => {
    const items = (e.clipboardData || e.originalEvent.clipboardData).items;
    for (let item of items) {
        if (item.type.indexOf("image") !== -1) {
            const blob = item.getAsFile();
            handleImageFile(blob);
            break;
        }
    }
});

// ================= CONTROLES E INPUT DO TERMINAL =================
const cmdInput = document.getElementById('cmdInput');
const btnSendCmd = document.getElementById('btnSendCmd');

function sendCommand() {
    const text = cmdInput.value.trim();
    if (!text && !attachedImageData) return;
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        appendTerminalLine("[ERRO] WebSocket desconectado.", "prompt-line");
        return;
    }

    if (attachedImageData) {
        appendTerminalLine(`>_ [📷 IMAGEM ANEXADA] ${text || 'Analise esta imagem'}`, "user-line");
        ws.send(JSON.stringify({ type: "command", text: text, image: attachedImageData }));
        // Limpa imagem após envio
        attachedImageData = null;
        if (imageFileInput) imageFileInput.value = "";
        if (attachedImgPreview) attachedImgPreview.style.display = "none";
    } else {
        appendTerminalLine(`>_ ${text}`, "user-line");
        ws.send(JSON.stringify({ type: "command", text: text }));
    }
    cmdInput.value = "";
}

if (btnSendCmd) btnSendCmd.addEventListener('click', sendCommand);
if (cmdInput) {
    cmdInput.addEventListener('keydown', (e) => {
        if (e.key === "Enter") sendCommand();
    });
}

// ================= BOTÕES DE AÇÃO RÁPIDA =================
let shieldActive = false;
const btnShield = document.getElementById('btnShield');
if (btnShield) {
    btnShield.addEventListener('click', () => {
        shieldActive = !shieldActive;
        btnShield.classList.toggle('active', shieldActive);
        appendTerminalLine(`[DEFESA] Modo Silêncio/Foco: ${shieldActive ? 'ATIVADO 🛡' : 'DESATIVADO'}`, "prompt-line");
    });
}

const btnBoost = document.getElementById('btnBoost');
if (btnBoost) {
    btnBoost.addEventListener('click', () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: "system_boost" }));
            appendTerminalLine("[SISTEMA] Disparando Boost e Limpeza Geral do Sistema...", "prompt-line");
        }
    });
}

const btnScreenSnap = document.getElementById('btnScreenSnap');
if (btnScreenSnap) {
    btnScreenSnap.addEventListener('click', () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: "screen_snap" }));
            appendTerminalLine("[VISÃO] Capturando tela para análise multimodal imediata...", "prompt-line");
        }
    });
}

const btnInterrupt = document.getElementById('btnInterrupt');
if (btnInterrupt) {
    btnInterrupt.addEventListener('click', () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: "interrupt" }));
            appendTerminalLine("[SISTEMA] Interrompendo fala imediatamente...", "prompt-line");
        }
    });
}

const btnClearTerm = document.getElementById('btnClearTerm');
if (btnClearTerm) {
    btnClearTerm.addEventListener('click', () => {
        const box = document.getElementById('terminalDisplay');
        if (box) {
            box.innerHTML = `<div class="term-line prompt-line">&gt;_ Console limpo. Sistema operacional.</div>`;
        }
    });
}

const btnNotifications = document.getElementById('btnNotifications');
if (btnNotifications) {
    btnNotifications.addEventListener('click', () => {
        appendTerminalLine(`[NOTIFICAÇÕES] Status: OPTIMAL. Conexão Neural Ativa. Todos os subsistemas operacionais.`, "success-line");
    });
}

const btnSettings = document.getElementById('btnSettings');
if (btnSettings) {
    btnSettings.addEventListener('click', () => {
        appendTerminalLine(`[CONFIGURAÇÕES] Modo HUD: Web Stark (Porta 8765) | Cérebro: Antigravity (Gemini 3.6 Flash) | Microfone: Calibrado (Floor: 380).`, "prompt-line");
    });
}

// ================= PICTURE-IN-PICTURE & MINI OLHOS FLUTUANTES =================
const pipVideo = document.getElementById('pipVideo');
const btnTogglePip = document.getElementById('btnTogglePip');
const floatingMiniEyes = document.getElementById('floatingMiniEyes');

async function activatePiP() {
    // 1. Alterna o pop-up nativo flutuante do desktop no Linux via Python
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "toggle_mini" }));
        appendTerminalLine("[MINI HUD] Alternando Mini Olhos Flutuantes do Desktop...", "prompt-line");
    }
    // 2. Também tenta acionar o Picture-in-Picture nativo do navegador
    try {
        if (document.pictureInPictureElement) {
            await document.exitPictureInPicture();
            appendTerminalLine("[MINI HUD] Picture-in-Picture desativado.", "prompt-line");
            return;
        }
        if (typeof pipVideo.requestPictureInPicture === "function") {
            if (!pipVideo.srcObject) {
                pipVideo.srcObject = eyesCanvas.captureStream(30);
                await pipVideo.play();
            }
            await pipVideo.requestPictureInPicture();
            appendTerminalLine("[MINI HUD] Olhos do Robô em Picture-in-Picture ativado!", "success-line");
        } else {
            toggleFloatingMiniPopup();
            appendTerminalLine("[MINI HUD] Olhos do Robô em Picture-in-Picture ativo!", "success-line");
        }
    } catch (err) {
        console.warn("PiP não suportado ou negado, usando mini overlay:", err);
        toggleFloatingMiniPopup();
        console.warn("PiP não suportado ou negado, usando mini overlay do desktop:", err);
    }
}

if (btnTogglePip) {
    btnTogglePip.addEventListener('click', activatePiP);
}

function toggleFloatingMiniPopup() {
    if (floatingMiniEyes) {
        const isVisible = floatingMiniEyes.style.display === "flex";
        floatingMiniEyes.style.display = isVisible ? "none" : "flex";
        appendTerminalLine(`[MINI HUD] Mini Olhos flutuantes: ${!isVisible ? 'VISÍVEL' : 'OCULTO'}`, "prompt-line");
    }
}

if (floatingMiniEyes) {
    floatingMiniEyes.addEventListener('click', () => {
        window.focus();
        floatingMiniEyes.style.display = "none";
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: "window_state", state: "visible" }));
        }
    });
}

// Detecta quando a janela for minimizada ou estiver fora de primeiro plano
// Detecta quando a janela for minimizada ou estiver fora de primeiro plano
document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
        // Envia ao servidor Python para abrir a janela nativa flutuante no canto do Linux
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: "window_state", state: "hidden" }));
        }
        if (floatingMiniEyes) floatingMiniEyes.style.display = "flex";
    } else {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: "window_state", state: "visible" }));
        }
        if (floatingMiniEyes) floatingMiniEyes.style.display = "none";
    }
});

// Detecta perda e retorno de foco da janela
window.addEventListener("blur", () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "window_state", state: "hidden" }));
    }
});

window.addEventListener("focus", () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "window_state", state: "visible" }));
    }
});

// Conecta WebSocket ao carregar a página
connectWebSocket();


