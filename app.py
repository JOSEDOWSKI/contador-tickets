#!/usr/bin/env python3
"""
Backend Flask para el contador de tickets
- Almacenamiento mensual de datos
- Integración con Jira
- API RESTful
"""

import json
import os
import sys
import hashlib
import secrets
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
from pathlib import Path

app = Flask(__name__, static_folder='.')
CORS(app)

# Registrar health check INMEDIATAMENTE después de crear la app
# Esto asegura que responda incluso durante la inicialización
@app.route('/health', methods=['GET', 'HEAD', 'OPTIONS'])
@app.route('/api/health', methods=['GET', 'HEAD', 'OPTIONS'])
def _early_health_check():
    """Health check temprano - responde inmediatamente sin importar nada"""
    return '{"status":"ok"}', 200, {'Content-Type': 'application/json'}

# Root se registra más abajo después de la inicialización completa

# Logging inicial
import logging
import sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
logger.info("=" * 50)
logger.info("Aplicación Flask iniciada correctamente")
logger.info(f"Puerto: 5000")
logger.info(f"Workers: 2")
logger.info("Health check disponible en: /health")
logger.info("=" * 50)

# Configuración
DATA_DIR = Path('data')
USERS_DIR = DATA_DIR / 'users'
SESSIONS_FILE = DATA_DIR / 'sessions.json'
JIRA_CONFIG_FILE = 'jira_config.json'

# Crear directorios de datos si no existen
try:
    DATA_DIR.mkdir(exist_ok=True)
    USERS_DIR.mkdir(exist_ok=True)
except Exception as e:
    print(f"Advertencia: No se pudo crear directorio data: {e}")

# Cargar sesiones
def load_sessions():
    """Carga las sesiones activas"""
    if SESSIONS_FILE.exists():
        try:
            with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_sessions(sessions):
    """Guarda las sesiones activas"""
    with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, indent=2)

def get_session_from_token(token):
    """Obtiene la sesión desde un token."""
    if not token:
        return None
    sessions = load_sessions()
    session = sessions.get(token)
    if isinstance(session, dict):
        return session
    # Compatibilidad con formato antiguo: token -> user_id
    if isinstance(session, str):
        return {'user_id': session, 'email': ''}
    return None

def get_user_id_from_token(token):
    """Obtiene el user_id desde un token"""
    session = get_session_from_token(token)
    if not session:
        return None
    return session.get('user_id')

def get_current_user():
    """Obtiene el usuario actual desde el token en el header"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        token = request.cookies.get('auth_token')
    if token:
        return get_user_id_from_token(token)
    return None

def get_user_dir(user_id):
    """Obtiene el directorio de datos del usuario"""
    if not user_id:
        return None
    user_dir = USERS_DIR / user_id
    user_dir.mkdir(exist_ok=True)
    return user_dir

def get_month_file(user_id=None, month=None):
    """Obtiene el archivo JSON del mes actual para un usuario"""
    if month is None:
        month = datetime.now().strftime('%Y-%m')
    if user_id:
        user_dir = get_user_dir(user_id)
        if user_dir:
            return user_dir / f'tickets-{month}.json'
    # Fallback a formato antiguo (sin usuario)
    return DATA_DIR / f'tickets-{month}.json'

def load_month_data(user_id=None, month=None):
    """Carga los datos del mes actual para un usuario"""
    if month is None:
        month = datetime.now().strftime('%Y-%m')
    
    try:
        month_file = get_month_file(user_id, month)
        if month_file and month_file.exists():
            with open(month_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error cargando datos del mes: {e}")
    
    return {
        "pendingTickets": 0,
        "totalTickets": 0,
        "resolvedTickets": 0,
        "month": month,
        "history": []
    }

def save_month_data(data, user_id=None):
    """Guarda los datos del mes actual para un usuario"""
    try:
        month_file = get_month_file(user_id)
        if not month_file:
            raise Exception("No se pudo obtener archivo del mes")
        data['month'] = datetime.now().strftime('%Y-%m')
        with open(month_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error guardando datos del mes: {e}")
        raise

def migrate_old_data():
    """Migra datos del archivo antiguo tickets-data.json al formato mensual"""
    try:
        old_file = Path('tickets-data.json')
        if old_file.exists():
            try:
                with open(old_file, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                
                # Crear entrada de historial
                history_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "action": "migrated_from_old_format",
                    "data": old_data
                }
                
                # Cargar datos del mes actual
                current_data = load_month_data()
                
                # Si el mes actual está vacío, usar datos antiguos
                if current_data['totalTickets'] == 0:
                    current_data.update({
                        "pendingTickets": old_data.get('pendingTickets', 0),
                        "totalTickets": old_data.get('totalTickets', 0),
                        "resolvedTickets": old_data.get('resolvedTickets', 0)
                    })
                
                # Agregar al historial
                if 'history' not in current_data:
                    current_data['history'] = []
                current_data['history'].append(history_entry)
                
                save_month_data(current_data)
                
                # Renombrar archivo antiguo como backup
                backup_file = Path('tickets-data.json.backup')
                if backup_file.exists():
                    backup_file.unlink()
                old_file.rename(backup_file)
                print(f"✓ Datos migrados desde tickets-data.json")
                return True
            except Exception as e:
                print(f"Error migrando datos: {e}")
                return False
        return False
    except Exception as e:
        print(f"Error en migrate_old_data: {e}")
        return False

def load_jira_config(user_id=None):
    """Carga la configuración de Jira (por usuario o global)"""
    # Si hay user_id, intentar cargar configuración del usuario
    if user_id:
        user_config_file = DATA_DIR / f'jira_config_{user_id}.json'
        if user_config_file.exists():
            with open(user_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    # Fallback a configuración global
    if os.path.exists(JIRA_CONFIG_FILE):
        with open(JIRA_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def fetch_jira_tickets(user_id=None):
    """Obtiene tickets de Jira usando la API. Retorna (datos, None) o (None, mensaje_error)."""
    config = load_jira_config(user_id)
    if not config:
        return None, 'No hay configuración de Jira. Usa "Configurar Jira" y guarda tus datos.'
    
    try:
        jira_url = config.get('url', '').rstrip('/')
        email = config.get('email', '')
        api_token = config.get('api_token', '')
        jql = config.get('jql', 'assignee = currentUser() AND status != Done')
        
        if not all([jira_url, email, api_token]):
            return None, 'Faltan URL, email o API token en la configuración.'
        
        # Construir URL de búsqueda
        search_url = f"{jira_url}/rest/api/3/search"
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        auth = (email, api_token)
        
        params = {
            'jql': jql,
            'maxResults': 100
        }
        
        response = requests.get(search_url, headers=headers, auth=auth, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            issues = data.get('issues', [])
            
            # Contar tickets por estado
            pending = 0
            resolved = 0
            
            for issue in issues:
                status = issue.get('fields', {}).get('status', {}).get('name', '').lower()
                if 'done' in status or 'resolved' in status or 'closed' in status:
                    resolved += 1
                else:
                    pending += 1
            
            return {
                'pendingTickets': pending,
                'resolvedTickets': resolved,
                'totalTickets': len(issues),
                'lastSync': datetime.now().isoformat()
            }, None
        elif response.status_code == 401:
            return None, 'Credenciales incorrectas. Revisa tu email y API token en "Configurar Jira".'
        elif response.status_code == 403:
            return None, 'Sin permiso para acceder a Jira. Revisa que el API token sea válido.'
        elif response.status_code == 404:
            return None, f'URL de Jira no encontrada. Revisa que {jira_url} sea correcta.'
        else:
            try:
                err_body = response.json()
                msg = err_body.get('errorMessages', err_body.get('errors', [str(response.text)]))
                if isinstance(msg, list):
                    msg = msg[0] if msg else response.text
            except Exception:
                msg = response.text[:200] if response.text else f'HTTP {response.status_code}'
            logger.error(f"Jira API: {response.status_code} - {msg}")
            return None, f'Jira respondió con error: {msg}'
            
    except requests.exceptions.Timeout:
        return None, 'Tiempo de espera agotado al conectar con Jira.'
    except requests.exceptions.ConnectionError:
        return None, 'No se pudo conectar con Jira. Revisa la URL y tu conexión.'
    except Exception as e:
        logger.exception("Error obteniendo tickets de Jira")
        return None, f'Error inesperado: {str(e)}'

# Rutas de Autenticación
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Inicia sesión con email/username"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'success': False, 'error': 'Email requerido'}), 400
        
        # Generar token de sesión
        user_id = hashlib.sha256(email.encode()).hexdigest()[:16]
        token = secrets.token_urlsafe(32)
        
        # Guardar sesión
        sessions = load_sessions()
        sessions[token] = {
            'user_id': user_id,
            'email': email,
            'created_at': datetime.now().isoformat()
        }
        save_sessions(sessions)
        
        # Crear directorio del usuario si no existe
        get_user_dir(user_id)
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user_id,
                'email': email
            }
        })
    except Exception as e:
        logger.exception("Error en login")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Cierra sesión"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            token = request.cookies.get('auth_token')
        
        if token:
            sessions = load_sessions()
            if token in sessions:
                del sessions[token]
                save_sessions(sessions)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.exception("Error en logout")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_current_user_info():
    """Obtiene información del usuario actual"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '') or request.cookies.get('auth_token')
    session = get_session_from_token(token)
    if not session:
        return jsonify({'authenticated': False}), 401

    return jsonify({
        'authenticated': True,
        'user': {
            'id': session.get('user_id'),
            'email': session.get('email', '')
        }
    })

# Rutas API
@app.route('/api/data', methods=['GET'])
def get_data():
    """Obtiene los datos del mes actual"""
    user_id = get_current_user()
    
    try:
        data = load_month_data(user_id)
    except Exception as e:
        logger.error(f"Error cargando datos: {e}")
        # Retornar datos por defecto en lugar de error 500
        data = {
            "pendingTickets": 0,
            "totalTickets": 0,
            "resolvedTickets": 0,
            "month": datetime.now().strftime('%Y-%m'),
            "history": []
        }
    
    # Obtener user_id si existe (para compatibilidad con Jira)
    try:
        jira_user_id = request.headers.get('X-User-ID') or request.cookies.get('user_id') or user_id
        
        # Si hay configuración de Jira, intentar sincronizar (sin bloquear si falla)
        try:
            if load_jira_config(jira_user_id):
                jira_data, _ = fetch_jira_tickets(jira_user_id)
                if jira_data:
                    data['jiraSync'] = jira_data
        except Exception as e:
            logger.error(f"Error sincronizando con Jira: {e}")
            # Continuar sin datos de Jira
    except Exception as e:
        logger.error(f"Error procesando request: {e}")
    
    return jsonify(data)

@app.route('/api/save', methods=['POST'])
def save_data():
    """Guarda los datos del mes actual"""
    user_id = get_current_user()
    
    # Si no hay usuario autenticado, retornar error
    if not user_id:
        return jsonify({'success': False, 'error': 'No autenticado'}), 401
    
    try:
        # Manejar tanto JSON como Blob (para sendBeacon)
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
        else:
            # Para sendBeacon, leer el body directamente
            data = json.loads(request.data.decode('utf-8'))
        
        current_data = load_month_data(user_id)
        
        # Actualizar contadores
        current_data.update({
            'pendingTickets': data.get('pendingTickets', current_data.get('pendingTickets', 0)),
            'totalTickets': data.get('totalTickets', current_data.get('totalTickets', 0)),
            'resolvedTickets': data.get('resolvedTickets', current_data.get('resolvedTickets', 0))
        })
        
        # Agregar al historial
        if 'history' not in current_data:
            current_data['history'] = []
        
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': data.get('action', 'manual_update'),
            'pendingTickets': current_data['pendingTickets'],
            'totalTickets': current_data['totalTickets'],
            'resolvedTickets': current_data['resolvedTickets']
        }
        current_data['history'].append(history_entry)
        
        # Mantener solo últimos 1000 registros
        if len(current_data['history']) > 1000:
            current_data['history'] = current_data['history'][-1000:]
        
        save_month_data(current_data, user_id)
        
        return jsonify({'success': True, 'month': current_data['month']})
    except Exception as e:
        logger.exception("Error guardando datos")
        return jsonify({'success': False, 'error': str(e)}), 500

# Rutas de Estadísticas
@app.route('/api/stats/months', methods=['GET'])
def list_months():
    """Lista todos los meses disponibles para el usuario actual"""
    user_id = get_current_user()
    months = []
    
    if user_id:
        user_dir = get_user_dir(user_id)
        if user_dir:
            for file in user_dir.glob('tickets-*.json'):
                month = file.stem.replace('tickets-', '')
                months.append(month)
    else:
        # Fallback a formato antiguo
        for file in DATA_DIR.glob('tickets-*.json'):
            month = file.stem.replace('tickets-', '')
            months.append(month)
    
    return jsonify(sorted(months, reverse=True))

@app.route('/api/stats/month/<month>', methods=['GET'])
def get_month_stats(month):
    """Obtiene datos de un mes específico para el usuario actual"""
    user_id = get_current_user()
    data = load_month_data(user_id, month)
    return jsonify(data)

@app.route('/api/stats/summary', methods=['GET'])
def get_stats_summary():
    """Obtiene resumen de estadísticas de todos los meses"""
    user_id = get_current_user()
    months = []
    
    if user_id:
        user_dir = get_user_dir(user_id)
        if user_dir:
            for file in sorted(user_dir.glob('tickets-*.json'), reverse=True):
                month = file.stem.replace('tickets-', '')
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        month_data = json.load(f)
                        months.append({
                            'month': month,
                            'totalTickets': month_data.get('totalTickets', 0),
                            'pendingTickets': month_data.get('pendingTickets', 0),
                            'resolvedTickets': month_data.get('resolvedTickets', 0)
                        })
                except Exception as e:
                    logger.error(f"Error leyendo {file}: {e}")
    
    # Calcular totales
    totals = {
        'totalTickets': sum(m['totalTickets'] for m in months),
        'pendingTickets': sum(m['pendingTickets'] for m in months),
        'resolvedTickets': sum(m['resolvedTickets'] for m in months),
        'months': months
    }
    
    return jsonify(totals)

@app.route('/api/jira/config', methods=['GET'])
def get_jira_config():
    """Obtiene la configuración de Jira (sin token)"""
    # Primero intentar obtener de la sesión del usuario (si existe)
    user_id = request.headers.get('X-User-ID') or request.cookies.get('user_id')
    
    if user_id:
        user_config_file = DATA_DIR / f'jira_config_{user_id}.json'
        if user_config_file.exists():
            with open(user_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                safe_config = {k: v for k, v in config.items() if k != 'api_token'}
                safe_config['configured'] = True
                safe_config['user_specific'] = True
                return jsonify(safe_config)
    
    # Fallback a configuración global (solo para uso personal)
    config = load_jira_config()
    if config:
        safe_config = {k: v for k, v in config.items() if k != 'api_token'}
        safe_config['configured'] = True
        safe_config['user_specific'] = False
        return jsonify(safe_config)
    return jsonify({'configured': False})

@app.route('/api/jira/config', methods=['POST'])
def set_jira_config():
    """Configura Jira (por usuario o global)"""
    try:
        config = request.get_json()
        user_id = request.headers.get('X-User-ID') or request.cookies.get('user_id')
        
        # Si hay user_id, guardar configuración por usuario
        if user_id:
            user_config_file = DATA_DIR / f'jira_config_{user_id}.json'
            with open(user_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            return jsonify({'success': True, 'user_specific': True})
        else:
            # Fallback: configuración global (solo para uso personal)
            with open(JIRA_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            return jsonify({'success': True, 'user_specific': False})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/jira/sync', methods=['POST'])
def sync_jira():
    """Sincroniza manualmente con Jira"""
    try:
        user_id = get_current_user() or request.headers.get('X-User-ID') or request.cookies.get('user_id')
        jira_data, error_msg = fetch_jira_tickets(user_id)
        if error_msg:
            return jsonify({'success': False, 'error': error_msg}), 200
        current_data = load_month_data(user_id)
        current_data.update({
            'pendingTickets': jira_data['pendingTickets'],
            'resolvedTickets': jira_data['resolvedTickets'],
            'totalTickets': jira_data['totalTickets']
        })
        save_month_data(current_data, user_id)
        return jsonify({'success': True, 'data': jira_data})
    except Exception as e:
        logger.exception("Error en sync_jira")
        return jsonify({'success': False, 'error': str(e)}), 200

# Health check endpoint ya está registrado arriba (_early_health_check)
# Sobrescribir con versión completa después de que todo esté inicializado
@app.route('/health', methods=['GET', 'HEAD', 'OPTIONS'])
@app.route('/api/health', methods=['GET', 'HEAD', 'OPTIONS'])
def health_check():
    """Endpoint de health check - respuesta inmediata sin verificaciones"""
    return '{"status":"ok"}', 200, {'Content-Type': 'application/json'}

# Servir archivos estáticos
@app.route('/', methods=['GET', 'HEAD'])
def root():
    """Root endpoint - sirve index.html"""
    try:
        return send_from_directory('.', 'index.html')
    except Exception as e:
        logger.error(f"Error sirviendo index.html: {e}")
        # Retornar respuesta básica en lugar de error
        return '<!DOCTYPE html><html><head><title>Contador de Tickets</title></head><body><h1>Contador de Tickets</h1><p>Error cargando página</p></body></html>', 200

# Ruta catch-all para archivos estáticos - DEBE estar AL FINAL
@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('.', path)
    except Exception as e:
        logger.error(f"Error sirviendo archivo {path}: {e}")
        # Si no se encuentra el archivo, devolver 404
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    # Migrar datos antiguos al iniciar (solo si se ejecuta directamente)
    try:
        migrate_old_data()
    except Exception as e:
        print(f"Advertencia al migrar datos: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
