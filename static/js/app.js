
document.addEventListener('DOMContentLoaded', () => {
    const explorerGrid = document.getElementById('explorer-grid');
    const omnibar = document.getElementById('omnibar');
    const dashboardView = document.getElementById('dashboard-view');
    const explorerView = document.getElementById('explorer-view');
    const recallView = document.getElementById('recall-view');
    const pipelineView = document.getElementById('pipeline-view');
    const ingestaView = document.getElementById('ingesta-view');

    // Stats Elements
    const statTotalRec = document.getElementById('stat-total-rec');
    const statTotalCards = document.getElementById('stat-total-cards');
    const statAiProc = document.getElementById('stat-ai-proc');
    const statProgress = document.getElementById('stat-progress');

    // Initial Load
    fetchStats();

    // Navigation Logic
    document.querySelectorAll('.nav-item').forEach(item => {
        item.onclick = () => {
            const view = item.getAttribute('data-view');
            switchView(view);
        }
    });

    // Dashboard Buttons
    document.getElementById('btn-goto-explorer').onclick = () => switchView('explorer');
    document.getElementById('btn-goto-recall').onclick = () => switchView('recall');
    document.getElementById('btn-goto-pipeline').onclick = () => switchView('pipeline');
    document.getElementById('btn-goto-ingesta').onclick = () => switchView('ingesta');

    function switchView(view) {
        // Update Nav UI
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        const navItem = document.querySelector(`.nav-item[data-view="${view}"]`);
        if (navItem) navItem.classList.add('active');

        // Hide all views
        [dashboardView, explorerView, recallView, pipelineView, ingestaView].forEach(v => {
            if (v) v.classList.add('hidden');
        });

        // Show target view
        if (view === 'dashboard') {
            dashboardView.classList.remove('hidden');
            fetchStats();
        } else if (view === 'explorer') {
            explorerView.classList.remove('hidden');
            fetchRecords();
        } else if (view === 'recall') {
            recallView.classList.remove('hidden');
        } else if (view === 'pipeline') {
            pipelineView.classList.remove('hidden');
        } else if (view === 'ingesta') {
            ingestaView.classList.remove('hidden');
        }
    }

    // Ingesta Submission Logic
    const btnSubmitIngest = document.getElementById('btn-submit-ingest');
    const ingestStatus = document.getElementById('ingest-status');
    const ingestStatusText = document.getElementById('ingest-status-text');
    const btnCloseIngestStatus = document.getElementById('btn-close-ingest-status');

    if (btnSubmitIngest) {
        btnSubmitIngest.onclick = async () => {
            const url = document.getElementById('ingest-url').value.trim();
            const tagsStr = document.getElementById('ingest-tags').value.trim();

            if (!url) {
                alert("Por favor ingresa una URL válida.");
                return;
            }

            const tags = tagsStr ? tagsStr.split(',').map(t => t.trim()) : [];

            // Show loading
            ingestStatus.classList.remove('hidden');
            ingestStatusText.innerText = "Procesando recurso... esto puede tardar unos segundos.";
            btnCloseIngestStatus.classList.add('hidden');
            ingestStatus.querySelector('.loader').classList.remove('hidden');

            try {
                const response = await fetch('/api/ingest', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, tags })
                });

                const result = await response.json();

                ingestStatus.querySelector('.loader').classList.add('hidden');
                btnCloseIngestStatus.classList.remove('hidden');

                if (result.status === 'ok') {
                    ingestStatusText.innerHTML = `<span style="color:#69f0ae">✓ ${result.message}</span><br><br>ID: ${result.id}<br>Título: ${result.title}`;
                } else {
                    ingestStatusText.innerHTML = `<span style="color:#ff5252">❌ Error: ${result.message}</span>`;
                }
            } catch (err) {
                console.error("Error en ingesta:", err);
                ingestStatus.querySelector('.loader').classList.add('hidden');
                btnCloseIngestStatus.classList.remove('hidden');
                ingestStatusText.innerHTML = `<span style="color:#ff5252">❌ Error de conexión con el servidor.</span>`;
            }
        }
    }

    btnCloseIngestStatus.onclick = () => {
        ingestStatus.classList.add('hidden');
        if (ingestStatusText.innerText.includes('indexado')) {
            document.getElementById('ingest-url').value = '';
            document.getElementById('ingest-tags').value = '';
            fetchStats();
        }
    };

    async function fetchStats() {
        try {
            const response = await fetch('/api/stats');
            if (!response.ok) throw new Error("API Stats fail");
            const data = await response.json();

            statTotalRec.innerText = data.total_records || 0;
            statTotalCards.innerText = data.total_cards || 0;
            statAiProc.innerText = data.processed_ai || 0;

            if (data.total_cards > 0) {
                statProgress.innerText = Math.round((data.study_progress.mastered / data.total_cards) * 100) + '%';
            } else {
                statProgress.innerText = '0%';
            }
        } catch (err) {
            console.error("Error fetching stats:", err);
        }
    }

    // Omnibar logic
    omnibar.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            switchView('explorer');
            fetchRecords(omnibar.value);
        }
    });

    async function fetchRecords(query = "") {
        explorerGrid.innerHTML = '<div class="loader">Consultando al cerebro...</div>';
        try {
            const response = await fetch(`/api/records?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            renderRecords(data);
        } catch (err) {
            explorerGrid.innerHTML = `<div class="error">Error de conexion: ${err.message}</div>`;
        }
    }

    function renderRecords(records) {
        if (records.length === 0) {
            explorerGrid.innerHTML = '<div class="no-results">No se encontraron conocimientos relacionados.</div>';
            return;
        }

        explorerGrid.innerHTML = `
            <div class="terminal-list">
                <div class="terminal-header-row">
                    <div>ID</div>
                    <div>TIPO</div>
                    <div>TÍTULO</div>
                    <div style="text-align: right;">MODIFICADO</div>
                </div>
                <div id="list-body"></div>
            </div>
        `;

        const listBody = document.getElementById('list-body');
        records.forEach((reg, index) => {
            const row = document.createElement('div');
            row.className = 'terminal-row';
            row.style.animationDelay = `${index * 0.02}s`;

            row.innerHTML = `
                <div class="id-cell">${reg.id}</div>
                <div class="type-cell">${reg.type}</div>
                <div class="title-cell">${reg.title}</div>
                <div class="date-cell">${new Date(reg.modified_at).toLocaleString('es-ES', { year: '2-digit', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })}</div>
            `;

            row.onclick = () => showDetail(reg.id);
            listBody.appendChild(row);
        });
    }

    async function showDetail(id) {
        const overlay = document.getElementById('detail-overlay');
        const detailContent = document.getElementById('detail-content');

        try {
            const response = await fetch(`/api/records/${id}`);
            const reg = await response.json();

            detailContent.innerHTML = `
                <div class="detail-header">
                    <span class="card-type">${reg.type}</span>
                    <h2>${reg.title}</h2>
                </div>
                <div class="detail-body">
                    <div class="section">
                        <h4><i class="fas fa-align-left"></i> Resumen Inteligente</h4>
                        <p>${reg.summary || 'Generando resumen...'}</p>
                    </div>
                    <div class="section cards-section">
                        <h4><i class="fas fa-brain"></i> Flashcards (${reg.cards.length})</h4>
                        <div class="cards-list">
                            ${reg.cards.map(c => `
                                <div class="mini-card">
                                    <div class="q">Q: ${c.question}</div>
                                    <div class="a">A: ${c.answer}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                <div class="detail-footer">
                    <a href="${reg.path_url}" target="_blank" class="btn-primary">
                        <i class="fas fa-external-link-alt"></i> Abrir Fuente Original
                    </a>
                </div>
            `;
            overlay.classList.remove('hidden');
        } catch (err) {
            console.error("Error cargando detalle:", err);
        }
    }

    // Close Modal Logic
    document.querySelector('.close-btn').onclick = () => {
        document.getElementById('detail-overlay').classList.add('hidden');
    };

    window.onclick = (event) => {
        const overlay = document.getElementById('detail-overlay');
        if (event.target == overlay) {
            overlay.classList.add('hidden');
        }
    };

    // Active Recall Session Logic
    let sessionCards = [];
    let currentCardIndex = 0;

    async function startStudySession() {
        const studyArea = document.getElementById('study-area');
        const noCardsMsg = document.getElementById('no-cards-msg');
        const flashcard = document.getElementById('main-flashcard');
        const recallActions = document.getElementById('recall-actions');

        studyArea.classList.remove('hidden');
        noCardsMsg.classList.add('hidden');
        flashcard.classList.remove('flipped');
        recallActions.classList.add('hidden');

        try {
            const response = await fetch('/api/recall/cards?limit=10');
            sessionCards = await response.json();

            if (sessionCards.length === 0) {
                studyArea.classList.add('hidden');
                noCardsMsg.classList.remove('hidden');
                return;
            }

            currentCardIndex = 0;
            updateSessionUI();
        } catch (err) {
            console.error("Error al iniciar sesión:", err);
        }
    }

    function updateSessionUI() {
        const card = sessionCards[currentCardIndex];
        document.getElementById('current-card-index').innerText = currentCardIndex + 1;
        document.getElementById('total-session-cards').innerText = sessionCards.length;

        document.getElementById('card-context-text').innerText = card.parent_title;
        document.getElementById('card-q-text').innerText = card.question;
        document.getElementById('card-a-text').innerText = card.answer;

        const flashcard = document.getElementById('main-flashcard');
        flashcard.classList.remove('flipped');
        document.getElementById('recall-actions').classList.add('hidden');
    }

    document.getElementById('main-flashcard').onclick = function () {
        this.classList.toggle('flipped');
        if (this.classList.contains('flipped')) {
            document.getElementById('recall-actions').classList.remove('hidden');
        }
    };

    document.querySelectorAll('.rate-btn').forEach(btn => {
        btn.onclick = async () => {
            const quality = parseInt(btn.getAttribute('data-quality'));
            const card = sessionCards[currentCardIndex];

            try {
                await fetch(`/api/recall/answer?card_id=${card.id}&quality=${quality}`, { method: 'POST' });
                nextCard();
            } catch (err) {
                console.error("Error al guardar respuesta:", err);
            }
        };
    });

    function nextCard() {
        currentCardIndex++;
        if (currentCardIndex < sessionCards.length) {
            updateSessionUI();
        } else {
            document.getElementById('study-area').classList.add('hidden');
            document.getElementById('no-cards-msg').classList.remove('hidden');
        }
    }

    // Special switchView hook for Recall
    async function fetchPipelineStatus() {
        try {
            const response = await fetch('/api/pipeline/status');
            const data = await response.json();

            const connEl = document.getElementById('pipe-conn');
            if (data.staging_connected) {
                connEl.innerText = "CONECTADO";
                connEl.style.color = "#69f0ae";
            } else {
                connEl.innerText = "NO DISPONIBLE (G: DRIVE)";
                connEl.style.color = "#ff5252";
            }

            document.getElementById('pipe-blocked').innerText = data.blocked_count;
            document.getElementById('pipe-ready').innerText = data.ready_count;
            document.getElementById('pipe-total').innerText = data.queue_count;
        } catch (err) {
            console.error("Error fetching pipeline status:", err);
        }
    }

    // Special switchView hook for Recall & Pipeline
    const originalSwitchView = switchView;
    switchView = function (view) {
        originalSwitchView(view);
        if (view === 'recall') {
            startStudySession();
        } else if (view === 'pipeline') {
            fetchPipelineStatus();
        }
    };

    // Theme Switcher Logic
    const colorDots = document.querySelectorAll('.color-dot');
    colorDots.forEach(dot => {
        dot.onclick = () => {
            const color = dot.getAttribute('data-color');
            const cyan = dot.getAttribute('data-cyan');

            document.documentElement.style.setProperty('--accent', color);
            document.documentElement.style.setProperty('--cyan', cyan);

            // Adjust glow
            const r = parseInt(color.slice(1, 3), 16);
            const g = parseInt(color.slice(3, 5), 16);
            const b = parseInt(color.slice(5, 7), 16);
            document.documentElement.style.setProperty('--accent-glow', `rgba(${r}, ${g}, ${b}, 0.4)`);

            colorDots.forEach(d => d.classList.remove('active'));
            dot.classList.add('active');
        }
    });

    if (colorDots.length > 0) colorDots[0].classList.add('active');
});
