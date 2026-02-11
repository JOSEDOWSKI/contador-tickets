// Estado de la aplicación
let state = {
    pendingTickets: 0,
    totalTickets: 0,
    resolvedTickets: 0
};

const API_BASE = window.location.origin;
let authToken = localStorage.getItem('auth_token');
let currentUser = null;

// Funciones de autenticación
async function checkAuth() {
    if (!authToken) {
        showLoginModal();
        return false;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/auth/me`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.authenticated) {
                currentUser = data.user;
                hideLoginModal();
                updateUserHeader();
                return true;
            }
        }
    } catch (e) {
        console.error('Error verificando autenticación:', e);
    }
    
    // Si falla, mostrar login
    authToken = null;
    localStorage.removeItem('auth_token');
    showLoginModal();
    return false;
}

function showLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) {
        modal.style.display = 'flex';
        document.getElementById('loginEmail').focus();
    }
}

function hideLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function updateUserHeader() {
    const header = document.getElementById('userHeader');
    const emailEl = document.getElementById('userEmail');
    if (header && currentUser) {
        header.style.display = 'block';
        if (emailEl) {
            emailEl.textContent = currentUser.email;
        }
    }
}

async function login(email) {
    try {
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        });
        
        const result = await response.json();
        if (result.success) {
            authToken = result.token;
            currentUser = result.user;
            localStorage.setItem('auth_token', authToken);
            hideLoginModal();
            updateUserHeader();
            await loadData();
            return true;
        } else {
            const errorEl = document.getElementById('loginError');
            if (errorEl) {
                errorEl.textContent = result.error || 'Error al iniciar sesión';
                errorEl.style.display = 'block';
            }
            return false;
        }
    } catch (e) {
        console.error('Error en login:', e);
        const errorEl = document.getElementById('loginError');
        if (errorEl) {
            errorEl.textContent = 'Error de conexión';
            errorEl.style.display = 'block';
        }
        return false;
    }
}

async function logout() {
    try {
        await fetch(`${API_BASE}/api/auth/logout`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
    } catch (e) {
        console.error('Error en logout:', e);
    }
    
    authToken = null;
    currentUser = null;
    localStorage.removeItem('auth_token');
    showLoginModal();
    state = { pendingTickets: 0, totalTickets: 0, resolvedTickets: 0 };
    updateUI();
}

function getAuthHeaders() {
    const headers = {
        'Content-Type': 'application/json'
    };
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    return headers;
}

// Cargar datos desde la API
async function loadData() {
    try {
        const response = await fetch(`${API_BASE}/api/data`, {
            headers: getAuthHeaders()
        });
        if (response.ok) {
            const data = await response.json();
            state = {
                pendingTickets: data.pendingTickets || 0,
                totalTickets: data.totalTickets || 0,
                resolvedTickets: data.resolvedTickets || 0
            };
            console.log('✓ Datos cargados desde servidor');
            
            // Mostrar información de sincronización Jira si está disponible
            if (data.jiraSync) {
                console.log('✓ Sincronizado con Jira:', data.jiraSync.lastSync);
                updateJiraStatus(data.jiraSync);
            } else {
                checkJiraConfig();
            }
            
            updateUI();
            return;
        }
    } catch (e) {
        console.error('Error al cargar datos:', e);
        // Fallback a localStorage
        const savedData = localStorage.getItem('ticketCounter');
        if (savedData) {
            try {
                state = JSON.parse(savedData);
                console.log('✓ Datos cargados desde localStorage (fallback)');
            } catch (err) {
                console.error('Error al cargar desde localStorage:', err);
            }
        }
    }
    
    updateUI();
}

// Guardar datos en el servidor
async function saveData(action = 'manual_update') {
    // Si no hay autenticación, solo guardar en localStorage
    if (!authToken) {
        localStorage.setItem('ticketCounter', JSON.stringify(state));
        return false;
    }
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // Timeout de 5 segundos
        
        const response = await fetch(`${API_BASE}/api/save`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                ...state,
                action: action
            }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
            const result = await response.json();
            console.log('✓ Datos guardados:', result.month);
            // También guardar en localStorage como respaldo
            localStorage.setItem('ticketCounter', JSON.stringify(state));
            return true;
        } else {
            console.error('Error al guardar:', response.status);
            localStorage.setItem('ticketCounter', JSON.stringify(state));
        }
    } catch (e) {
        if (e.name === 'AbortError') {
            console.warn('Guardado cancelado (timeout o navegación)');
        } else {
            console.error('Error al guardar datos:', e);
        }
        // Fallback a localStorage
        localStorage.setItem('ticketCounter', JSON.stringify(state));
    }
    return false;
}

// Actualizar la interfaz de usuario
function updateUI() {
    document.getElementById('pendingTickets').textContent = state.pendingTickets;
    document.getElementById('totalTickets').textContent = state.totalTickets;
    document.getElementById('resolvedTickets').textContent = state.resolvedTickets;

    // Actualizar estado del botón de resolución
    const resolveBtn = document.getElementById('resolveTicketBtn');
    if (resolveBtn) {
        resolveBtn.disabled = state.pendingTickets === 0;
    }
}

// Agregar nuevo ticket
async function addNewTicket() {
    state.pendingTickets++;
    state.totalTickets++;
    await saveData('new_ticket');
    updateUI();
}

// Resolver ticket
async function resolveTicket() {
    if (state.pendingTickets === 0) {
        return;
    }

    state.pendingTickets--;
    state.resolvedTickets++;
    await saveData('ticket_resolved');
    updateUI();
}

// Reiniciar contador
async function resetCounter() {
    if (confirm('¿Estás seguro de que quieres reiniciar todos los contadores?')) {
        state = {
            pendingTickets: 0,
            totalTickets: 0,
            resolvedTickets: 0
        };
        await saveData('reset');
        updateUI();
    }
}

// Obtener o crear user_id
function getUserId() {
    let userId = localStorage.getItem('user_id');
    if (!userId) {
        userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('user_id', userId);
    }
    return userId;
}

// Verificar configuración de Jira
async function checkJiraConfig() {
    try {
        const userId = getUserId();
        const response = await fetch(`${API_BASE}/api/jira/config`, {
            headers: {
                'X-User-ID': userId
            }
        });
        if (response.ok) {
            const config = await response.json();
            const statusEl = document.getElementById('jiraStatus');
            if (statusEl) {
                if (config.configured) {
                    const source = config.user_specific ? ' (tu configuración)' : ' (global)';
                    statusEl.textContent = '✓ Jira configurado' + source;
                    statusEl.style.color = '#888';
                } else {
                    statusEl.textContent = '⚠ Jira no configurado';
                    statusEl.style.color = '#666';
                }
            }
        }
    } catch (e) {
        console.error('Error verificando configuración Jira:', e);
    }
}

// Mostrar modal de configuración
function showJiraConfigModal() {
    const modal = document.getElementById('jiraConfigModal');
    if (modal) {
        modal.style.display = 'flex';
        
        // Cargar configuración actual si existe
        loadCurrentJiraConfig();
    }
}

// Cargar configuración actual en el modal
async function loadCurrentJiraConfig() {
    try {
        const userId = getUserId();
        const response = await fetch(`${API_BASE}/api/jira/config`, {
            headers: {
                'X-User-ID': userId
            }
        });
        if (response.ok) {
            const config = await response.json();
            if (config.configured) {
                // Cargar valores (sin token por seguridad)
                document.getElementById('jiraUrl').value = config.url || '';
                document.getElementById('jiraEmail').value = config.email || '';
                document.getElementById('jiraJql').value = config.jql || 'assignee = currentUser() AND status != Done';
            }
        }
    } catch (e) {
        console.error('Error cargando configuración:', e);
    }
}

// Guardar configuración de Jira
async function saveJiraConfig(event) {
    event.preventDefault();
    
    const config = {
        url: document.getElementById('jiraUrl').value.trim(),
        email: document.getElementById('jiraEmail').value.trim(),
        api_token: document.getElementById('jiraToken').value.trim(),
        jql: document.getElementById('jiraJql').value.trim() || 'assignee = currentUser() AND status != Done'
    };
    
    if (!config.url || !config.email || !config.api_token) {
        alert('Por favor completa todos los campos requeridos');
        return;
    }
    
    try {
        const userId = getUserId();
        const response = await fetch(`${API_BASE}/api/jira/config`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': userId
            },
            body: JSON.stringify(config)
        });
        
        if (response.ok) {
            const result = await response.json();
            if (result.success) {
                alert('✓ Configuración de Jira guardada correctamente');
                closeJiraConfigModal();
                checkJiraConfig();
                // Sincronizar automáticamente
                syncJira();
            } else {
                alert('Error al guardar la configuración');
            }
        } else {
            alert('Error al guardar la configuración');
        }
    } catch (e) {
        console.error('Error guardando configuración:', e);
        alert('Error al guardar la configuración');
    }
}

// Cerrar modal
function closeJiraConfigModal() {
    const modal = document.getElementById('jiraConfigModal');
    if (modal) {
        modal.style.display = 'none';
        // Limpiar formulario
        document.getElementById('jiraConfigForm').reset();
    }
}

// Actualizar estado de Jira en la UI
function updateJiraStatus(jiraSync) {
    const statusEl = document.getElementById('jiraStatus');
    if (statusEl && jiraSync) {
        const date = new Date(jiraSync.lastSync);
        const timeStr = date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
        statusEl.textContent = `✓ Jira sincronizado ${timeStr}`;
        statusEl.style.color = '#888';
    }
}

// Cargar estadísticas
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats/summary`, {
            headers: getAuthHeaders()
        });
        if (response.ok) {
            const data = await response.json();
            return data;
        }
    } catch (e) {
        console.error('Error cargando estadísticas:', e);
    }
    return null;
}

// Mostrar estadísticas
async function showStats() {
    const modal = document.getElementById('statsModal');
    const content = document.getElementById('statsContent');
    if (!modal || !content) return;
    
    modal.style.display = 'flex';
    content.innerHTML = '<p style="text-align: center;">Cargando estadísticas...</p>';
    
    const stats = await loadStats();
    if (!stats) {
        content.innerHTML = '<p style="text-align: center; color: #888;">Error al cargar estadísticas</p>';
        return;
    }
    
    let html = `
        <div style="margin-bottom: 30px; padding: 20px; background: #111; border: 1px solid #333;">
            <h3 style="color: #fff; font-size: 18px; font-weight: 300; margin-bottom: 20px;">Resumen Total</h3>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                <div>
                    <div style="color: #888; font-size: 11px; text-transform: uppercase; margin-bottom: 5px;">Total</div>
                    <div style="color: #fff; font-size: 32px; font-weight: 300;">${stats.totalTickets}</div>
                </div>
                <div>
                    <div style="color: #888; font-size: 11px; text-transform: uppercase; margin-bottom: 5px;">Pendientes</div>
                    <div style="color: #fff; font-size: 32px; font-weight: 300;">${stats.pendingTickets}</div>
                </div>
                <div>
                    <div style="color: #888; font-size: 11px; text-transform: uppercase; margin-bottom: 5px;">Resueltos</div>
                    <div style="color: #fff; font-size: 32px; font-weight: 300;">${stats.resolvedTickets}</div>
                </div>
            </div>
        </div>
    `;
    
    if (stats.months && stats.months.length > 0) {
        html += '<h3 style="color: #fff; font-size: 18px; font-weight: 300; margin-bottom: 20px;">Por Mes</h3>';
        html += '<div style="display: flex; flex-direction: column; gap: 15px;">';
        
        for (const month of stats.months) {
            const monthName = new Date(month.month + '-01').toLocaleDateString('es-ES', { month: 'long', year: 'numeric' });
            html += `
                <div style="padding: 20px; background: #111; border: 1px solid #333;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h4 style="color: #fff; font-size: 16px; font-weight: 300; text-transform: capitalize;">${monthName}</h4>
                        <span style="color: #888; font-size: 12px;">${month.month}</span>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                        <div>
                            <div style="color: #888; font-size: 10px; text-transform: uppercase; margin-bottom: 5px;">Total</div>
                            <div style="color: #fff; font-size: 24px; font-weight: 300;">${month.totalTickets}</div>
                        </div>
                        <div>
                            <div style="color: #888; font-size: 10px; text-transform: uppercase; margin-bottom: 5px;">Pendientes</div>
                            <div style="color: #fff; font-size: 24px; font-weight: 300;">${month.pendingTickets}</div>
                        </div>
                        <div>
                            <div style="color: #888; font-size: 10px; text-transform: uppercase; margin-bottom: 5px;">Resueltos</div>
                            <div style="color: #fff; font-size: 24px; font-weight: 300;">${month.resolvedTickets}</div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
    } else {
        html += '<p style="text-align: center; color: #888;">No hay datos históricos disponibles</p>';
    }
    
    content.innerHTML = html;
}

// Sincronizar con Jira
async function syncJira() {
    const statusEl = document.getElementById('jiraStatus');
    if (statusEl) {
        statusEl.textContent = 'Sincronizando...';
        statusEl.style.color = '#888';
    }
    
    try {
        const userId = getUserId();
        const headers = getAuthHeaders();
        headers['X-User-ID'] = userId;
        const response = await fetch(`${API_BASE}/api/jira/sync`, {
            method: 'POST',
            headers: headers
        });
        
        const result = await response.json().catch(() => ({}));
        if (response.ok && result.success) {
            state = {
                pendingTickets: result.data.pendingTickets,
                totalTickets: result.data.totalTickets,
                resolvedTickets: result.data.resolvedTickets
            };
            updateUI();
            if (typeof updateJiraStatus === 'function') updateJiraStatus(result.data);
            if (statusEl) {
                statusEl.textContent = '✓ Sincronizado';
                statusEl.style.color = '#888';
            }
        } else {
            const msg = result.error || 'Error al sincronizar';
            if (statusEl) {
                statusEl.textContent = '✗ ' + msg;
                statusEl.style.color = '#888';
            }
            console.error('Sync Jira:', msg);
        }
    } catch (e) {
        console.error('Error al sincronizar con Jira:', e);
        if (statusEl) {
            statusEl.textContent = '✗ Error de conexión';
            statusEl.style.color = '#666';
        }
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', async () => {
    // Verificar autenticación primero
    const authenticated = await checkAuth();
    if (!authenticated) {
        return; // Esperar a que el usuario inicie sesión
    }
    
    await loadData();
    
    const newTicketBtn = document.getElementById('newTicketBtn');
    const resolveTicketBtn = document.getElementById('resolveTicketBtn');
    const resetBtn = document.getElementById('resetBtn');
    const syncJiraBtn = document.getElementById('syncJiraBtn');
    const configJiraBtn = document.getElementById('configJiraBtn');
    const jiraConfigForm = document.getElementById('jiraConfigForm');
    const cancelConfigBtn = document.getElementById('cancelConfigBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const statsBtn = document.getElementById('statsBtn');
    const closeStatsBtn = document.getElementById('closeStatsBtn');
    const loginForm = document.getElementById('loginForm');
    
    if (newTicketBtn) {
        newTicketBtn.addEventListener('click', addNewTicket);
    }
    if (resolveTicketBtn) {
        resolveTicketBtn.addEventListener('click', resolveTicket);
    }
    if (resetBtn) {
        resetBtn.addEventListener('click', resetCounter);
    }
    if (syncJiraBtn) {
        syncJiraBtn.addEventListener('click', syncJira);
    }
    if (configJiraBtn) {
        configJiraBtn.addEventListener('click', showJiraConfigModal);
    }
    if (jiraConfigForm) {
        jiraConfigForm.addEventListener('submit', saveJiraConfig);
    }
    if (cancelConfigBtn) {
        cancelConfigBtn.addEventListener('click', closeJiraConfigModal);
    }
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
    if (statsBtn) {
        statsBtn.addEventListener('click', showStats);
    }
    if (closeStatsBtn) {
        closeStatsBtn.addEventListener('click', () => {
            document.getElementById('statsModal').style.display = 'none';
        });
    }
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('loginEmail').value.trim();
            if (email) {
                await login(email);
            }
        });
    }
    
    // Cerrar modal al hacer click fuera
    const modal = document.getElementById('jiraConfigModal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeJiraConfigModal();
            }
        });
    }
    
    // Verificar configuración de Jira después de cargar
    setTimeout(checkJiraConfig, 1000);
    
    // Atajos de teclado
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + N para nuevo ticket
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            addNewTicket();
        }
        // Ctrl/Cmd + R para resolver ticket
        if ((e.ctrlKey || e.metaKey) && e.key === 'r' && !e.shiftKey) {
            e.preventDefault();
            resolveTicket();
        }
        // Ctrl/Cmd + S para sincronizar con Jira
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            syncJira();
        }
    });
});

// Guardar datos antes de cerrar la página (usar sendBeacon para mayor confiabilidad)
window.addEventListener('beforeunload', () => {
    if (authToken && navigator.sendBeacon) {
        // Usar sendBeacon que es más confiable para beforeunload
        const data = JSON.stringify({
            ...state,
            action: 'beforeunload'
        });
        navigator.sendBeacon(
            `${API_BASE}/api/save`,
            new Blob([data], { type: 'application/json' })
        );
    } else {
        // Fallback: guardar en localStorage
        localStorage.setItem('ticketCounter', JSON.stringify(state));
    }
});
