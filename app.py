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
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
from pathlib import Path

app = Flask(__name__, static_folder='.')
CORS(app)

# Logging inicial
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Aplicación Flask iniciada")

# Configuración
DATA_DIR = Path('data')
JIRA_CONFIG_FILE = 'jira_config.json'

# Crear directorio de datos si no existe
try:
    DATA_DIR.mkdir(exist_ok=True)
except Exception as e:
    print(f"Advertencia: No se pudo crear directorio data: {e}")

def get_month_file():
    """Obtiene el archivo JSON del mes actual"""
    month = datetime.now().strftime('%Y-%m')
    return DATA_DIR / f'tickets-{month}.json'

def load_month_data():
    """Carga los datos del mes actual"""
    month_file = get_month_file()
    if month_file.exists():
        with open(month_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "pendingTickets": 0,
        "totalTickets": 0,
        "resolvedTickets": 0,
        "month": datetime.now().strftime('%Y-%m'),
        "history": []
    }

def save_month_data(data):
    """Guarda los datos del mes actual"""
    month_file = get_month_file()
    data['month'] = datetime.now().strftime('%Y-%m')
    with open(month_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

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
    """Obtiene tickets de Jira usando la API"""
    config = load_jira_config(user_id)
    if not config:
        return None
    
    try:
        jira_url = config.get('url', '').rstrip('/')
        email = config.get('email', '')
        api_token = config.get('api_token', '')
        jql = config.get('jql', 'assignee = currentUser() AND status != Done')
        
        if not all([jira_url, email, api_token]):
            return None
        
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
        
        response = requests.get(search_url, headers=headers, auth=auth, params=params, timeout=10)
        
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
            }
        else:
            print(f"Error Jira API: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error obteniendo tickets de Jira: {e}")
        return None

# Rutas API
@app.route('/api/data', methods=['GET'])
def get_data():
    """Obtiene los datos del mes actual"""
    try:
        data = load_month_data()
    except Exception as e:
        logger.error(f"Error cargando datos: {e}")
        return jsonify({'error': str(e)}), 500
    
    # Obtener user_id si existe
    user_id = request.headers.get('X-User-ID') or request.cookies.get('user_id')
    
    # Si hay configuración de Jira, intentar sincronizar
    if load_jira_config(user_id):
        jira_data = fetch_jira_tickets(user_id)
        if jira_data:
            # Actualizar con datos de Jira si están disponibles
            data['jiraSync'] = jira_data
            # Opcional: actualizar contadores con datos de Jira
            # data['pendingTickets'] = jira_data['pendingTickets']
            # data['resolvedTickets'] = jira_data['resolvedTickets']
            # data['totalTickets'] = jira_data['totalTickets']
    
    return jsonify(data)

@app.route('/api/save', methods=['POST'])
def save_data():
    """Guarda los datos del mes actual"""
    try:
        data = request.get_json()
        current_data = load_month_data()
        
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
        
        save_month_data(current_data)
        
        return jsonify({'success': True, 'month': current_data['month']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/months', methods=['GET'])
def list_months():
    """Lista todos los meses disponibles"""
    months = []
    for file in DATA_DIR.glob('tickets-*.json'):
        month = file.stem.replace('tickets-', '')
        months.append(month)
    return jsonify(sorted(months, reverse=True))

@app.route('/api/month/<month>', methods=['GET'])
def get_month(month):
    """Obtiene datos de un mes específico"""
    month_file = DATA_DIR / f'tickets-{month}.json'
    if month_file.exists():
        with open(month_file, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify({'error': 'Month not found'}), 404

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
    user_id = request.headers.get('X-User-ID') or request.cookies.get('user_id')
    jira_data = fetch_jira_tickets(user_id)
    if jira_data:
        current_data = load_month_data()
        current_data.update({
            'pendingTickets': jira_data['pendingTickets'],
            'resolvedTickets': jira_data['resolvedTickets'],
            'totalTickets': jira_data['totalTickets']
        })
        save_month_data(current_data)
        return jsonify({'success': True, 'data': jira_data})
    return jsonify({'success': False, 'error': 'Failed to sync with Jira'}), 500

# Servir archivos estáticos
@app.route('/')
def index():
    try:
        return send_from_directory('.', 'index.html')
    except Exception as e:
        logger.error(f"Error sirviendo index.html: {e}")
        return jsonify({'error': 'Error loading page'}), 500

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('.', path)
    except Exception as e:
        logger.error(f"Error sirviendo archivo {path}: {e}")
        # Si no se encuentra el archivo, devolver 404
        return jsonify({'error': 'File not found'}), 404

# Health check endpoint para verificar que la app está funcionando
# CapRover usa este endpoint para verificar que la app está funcionando
@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de health check - usado por CapRover"""
    try:
        # Verificar que el directorio de datos existe y es accesible
        DATA_DIR.mkdir(exist_ok=True)
        # Intentar leer/escribir para verificar permisos
        test_file = DATA_DIR / '.health_check'
        test_file.write_text('ok')
        test_file.unlink()
        
        return jsonify({
            'status': 'ok',
            'service': 'tickets-counter',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Root endpoint también debe responder para health checks básicos
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    # Migrar datos antiguos al iniciar (solo si se ejecuta directamente)
    try:
        migrate_old_data()
    except Exception as e:
        print(f"Advertencia al migrar datos: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
