// Estado de la aplicación
let state = {
    pendingTickets: 0,
    totalTickets: 0,
    resolvedTickets: 0
};

const API_BASE = window.location.origin;

// Cargar datos desde la API
async function loadData() {
    try {
        const response = await fetch(`${API_BASE}/api/data`);
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
    try {
        const response = await fetch(`${API_BASE}/api/save`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ...state,
                action: action
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('✓ Datos guardados:', result.month);
            // También guardar en localStorage como respaldo
            localStorage.setItem('ticketCounter', JSON.stringify(state));
            return true;
        }
    } catch (e) {
        console.error('Error al guardar datos:', e);
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

// Sincronizar con Jira
async function syncJira() {
    const statusEl = document.getElementById('jiraStatus');
    if (statusEl) {
        statusEl.textContent = 'Sincronizando...';
        statusEl.style.color = '#888';
    }
    
    try {
        const userId = getUserId();
        const response = await fetch(`${API_BASE}/api/jira/sync`, {
            method: 'POST',
            headers: {
                'X-User-ID': userId
            }
        });
        
        if (response.ok) {
            const result = await response.json();
            if (result.success) {
                state = {
                    pendingTickets: result.data.pendingTickets,
                    totalTickets: result.data.totalTickets,
                    resolvedTickets: result.data.resolvedTickets
                };
                updateUI();
                updateJiraStatus(result.data);
            } else {
                if (statusEl) {
                    statusEl.textContent = '✗ Error al sincronizar';
                    statusEl.style.color = '#666';
                }
            }
        } else {
            if (statusEl) {
                statusEl.textContent = '✗ Error al sincronizar';
                statusEl.style.color = '#666';
            }
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
    await loadData();
    
    const newTicketBtn = document.getElementById('newTicketBtn');
    const resolveTicketBtn = document.getElementById('resolveTicketBtn');
    const resetBtn = document.getElementById('resetBtn');
    const syncJiraBtn = document.getElementById('syncJiraBtn');
    const configJiraBtn = document.getElementById('configJiraBtn');
    const jiraConfigForm = document.getElementById('jiraConfigForm');
    const cancelConfigBtn = document.getElementById('cancelConfigBtn');
    
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

// Guardar datos antes de cerrar la página
window.addEventListener('beforeunload', async () => {
    await saveData();
});
