// --- DOM Elements ---
const loginScreen = document.getElementById('login-screen');
const appScreen = document.getElementById('app-screen');
const modal = document.getElementById('record-modal');

const loginForm = document.getElementById('login-form');
const recordForm = document.getElementById('record-form');
const btnLogout = document.getElementById('btn-logout');
const btnNew = document.getElementById('btn-new-record');
const btnCancelModal = document.getElementById('btn-cancel-modal');

const searchInput = document.getElementById('search-input');
const tbody = document.getElementById('records-tbody');
const pageIndicator = document.getElementById('page-indicator');
const btnPrev = document.getElementById('btn-prev');
const btnNext = document.getElementById('btn-next');

const loginError = document.getElementById('login-error');
const globalError = document.getElementById('global-error');
const modalError = document.getElementById('modal-error');

// --- State ---
let currentPage = 0;
const LIMIT = 50;

// --- Interceptor de Fetch Blindado (Network & 401 Protected) ---
async function apiFetch(url, options = {}) {
    try {
        const res = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${sessionStorage.getItem('nexus_token')}`,
                ...options.headers
            }
        });

        if (res.status === 401) {
            sessionStorage.removeItem('nexus_token');
            showScreen('login');
            return null; // Sesión expirada
        }
        return res;
    } catch (err) {
        showGlobalError('Sin conexión. Verifica tu internet e intenta nuevamente.');
        return null;
    }
}

// --- Utils UI ---
function showScreen(screen) {
    if (screen === 'login') {
        appScreen.classList.add('hidden');
        loginScreen.classList.remove('hidden');
        document.getElementById('email').focus();
    } else {
        loginScreen.classList.add('hidden');
        appScreen.classList.remove('hidden');
        loadRecords();
        searchInput.focus();
    }
}

function showGlobalError(msg) {
    globalError.textContent = msg;
    globalError.classList.remove('hidden');
    setTimeout(() => globalError.classList.add('hidden'), 5000);
}

function formatDate(ds) {
    if (!ds) return '-';
    const d = new Date(ds);
    return `${d.toLocaleDateString()} ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
}

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
    if (sessionStorage.getItem('nexus_token')) {
        showScreen('app');
    } else {
        showScreen('login');
    }
});

// --- Auth ---
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    loginError.textContent = '';

    const data = new URLSearchParams();
    data.append('username', document.getElementById('email').value);
    data.append('password', document.getElementById('password').value);

    try {
        const res = await fetch('/auth/login', {
            method: 'POST',
            body: data
        });

        if (!res.ok) {
            loginError.textContent = 'Credenciales incorrectas o red caída.';
            return;
        }

        const json = await res.json();
        sessionStorage.setItem('nexus_token', json.access_token);
        showScreen('app');
    } catch (err) {
        loginError.textContent = 'Error de conexión con el servidor.';
    }
});

btnLogout.addEventListener('click', async () => {
    await apiFetch('/auth/logout', { method: 'POST' });
    sessionStorage.removeItem('nexus_token');
    showScreen('login');
});

// --- Data Fetching ---
async function loadRecords() {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center">Cargando...</td></tr>';

    const query = searchInput.value.trim();
    const url = `/api/records/?q=${encodeURIComponent(query)}&limit=${LIMIT}&offset=${currentPage * LIMIT}`;

    const res = await apiFetch(url);
    if (!res) return; // intercepted (401 or network drop)

    if (res.ok) {
        const records = await res.json();
        renderTable(records);
        pageIndicator.textContent = `Pág. ${currentPage + 1}`;
        btnPrev.disabled = currentPage === 0;
        btnNext.disabled = records.length < LIMIT;
    } else {
        showGlobalError('Error al cargar registros.');
    }
}

function renderTable(records) {
    tbody.innerHTML = '';
    if (records.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center">No hay resultados.</td></tr>';
        return;
    }

    records.forEach(r => {
        const tr = document.createElement('tr');
        tr.className = 'cursor-pointer';
        // (Click handler simulado para ver detalles en futuras mejoras)
        tr.innerHTML = `
            <td>${r.id}</td>
            <td><span class="type-badge">${r.type}</span></td>
            <td><strong>${r.title}</strong></td>
            <td><small>${formatDate(r.created_at)}</small></td>
            <td><small>${formatDate(r.last_viewed_at) || '-'}</small></td>
            <td>${(r.content_raw || '').substring(0, 30)}...</td>
        `;
        tbody.appendChild(tr);
    });
}

// --- Search & Pagination ---
let searchTimeout;
searchInput.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        currentPage = 0;
        loadRecords();
    }, 400); // debounce 400ms
});

btnPrev.addEventListener('click', () => {
    if (currentPage > 0) { currentPage--; loadRecords(); }
});
btnNext.addEventListener('click', () => {
    currentPage++; loadRecords();
});

// --- Modal Create ---
btnNew.addEventListener('click', () => {
    recordForm.reset();
    modalError.textContent = '';
    modal.classList.remove('hidden');
    document.getElementById('form-title').focus();
});

btnCancelModal.addEventListener('click', () => {
    modal.classList.add('hidden');
});

recordForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    modalError.textContent = '';

    const payload = {
        title: document.getElementById('form-title').value,
        type: document.getElementById('form-type').value,
        content_raw: document.getElementById('form-content').value,
        description: document.getElementById('form-desc').value,
        is_flashcard_source: false,
        tags: document.getElementById('form-tags').value.split(',').map(t => t.trim()).filter(t => t)
    };

    const res = await apiFetch('/api/records/', {
        method: 'POST',
        body: JSON.stringify(payload)
    });

    if (!res) return;

    if (res.ok) {
        modal.classList.add('hidden');
        currentPage = 0;
        loadRecords();
    } else {
        const errorData = await res.json();
        modalError.textContent = errorData.detail || 'Error al guardar el registro en la nube.';
    }
});
