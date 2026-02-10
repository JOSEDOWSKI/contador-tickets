# Contador de Tickets

Aplicación web para contar tickets pendientes y resueltos con integración con Jira.

## Características

- ✅ Contador de tickets pendientes y resueltos
- ✅ Almacenamiento mensual de datos (no se pierden datos históricos)
- ✅ Integración con Jira para sincronización automática
- ✅ API RESTful completa
- ✅ Interfaz minimalista estilo npmx.dev
- ✅ Listo para deploy en producción (CapRover, Docker)

## Uso Local

### Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Migrar datos antiguos (si los tienes)
python3 migrate_data.py

# Ejecutar servidor
python3 app.py
```

La aplicación estará disponible en `http://localhost:5000`

### Como Servicio Systemd (Linux)

```bash
./install-service.sh
```

## Deploy en Producción (CapRover)

Ver [DEPLOY.md](DEPLOY.md) para instrucciones completas.

### Resumen Rápido

1. **Migrar datos locales:**
   ```bash
   python3 migrate_data.py
   ```

2. **Subir a GitHub:**
   ```bash
   git add .
   git commit -m "Deploy a producción"
   git push origin main
   ```

3. **Configurar en CapRover:**
   - Crear nueva app
   - Conectar con GitHub
   - Configurar volumen para `/app/data`
   - Deploy

## Integración con Jira

### Configuración

1. Obtén tu API Token de Jira:
   - https://id.atlassian.com/manage-profile/security/api-tokens

2. Crea `jira_config.json`:
   ```json
   {
     "url": "https://tu-empresa.atlassian.net",
     "email": "tu-email@empresa.com",
     "api_token": "tu-api-token",
     "jql": "assignee = currentUser() AND status != Done"
   }
   ```

3. Configura vía API:
   ```bash
   curl -X POST http://localhost:5000/api/jira/config \
     -H "Content-Type: application/json" \
     -d @jira_config.json
   ```

### Sincronización

- **Automática:** Los datos de Jira se cargan automáticamente al acceder a `/api/data`
- **Manual:** Click en "Sincronizar Jira" o `Ctrl+S`

## Estructura de Datos

Los datos se guardan mensualmente en:
```
data/
  ├── tickets-2026-02.json
  ├── tickets-2026-03.json
  └── ...
```

Cada archivo contiene:
- Contadores del mes
- Historial completo de cambios
- Metadatos de sincronización con Jira

## API Endpoints

- `GET /api/data` - Obtiene datos del mes actual (con sync Jira si está configurado)
- `POST /api/save` - Guarda datos manualmente
- `GET /api/months` - Lista todos los meses disponibles
- `GET /api/month/<month>` - Obtiene datos de un mes específico
- `GET /api/jira/config` - Obtiene configuración de Jira
- `POST /api/jira/config` - Configura Jira
- `POST /api/jira/sync` - Sincroniza manualmente con Jira

## Migración de Datos

Si tienes datos en el formato antiguo (`tickets-data.json`):

```bash
python3 migrate_data.py
```

Esto:
- Migra los datos al formato mensual
- Crea `data/tickets-YYYY-MM.json`
- Hace backup del archivo antiguo

## Desarrollo

### Requisitos

- Python 3.11+
- Flask
- requests

### Estructura del Proyecto

```
.
├── app.py                 # Backend Flask
├── index.html            # Frontend
├── script.js            # Lógica del frontend
├── styles.css           # Estilos
├── requirements.txt     # Dependencias Python
├── Dockerfile          # Para Docker/CapRover
├── migrate_data.py     # Script de migración
├── data/              # Datos mensuales (no en git)
└── jira_config.json   # Configuración Jira (no en git)
```

## Licencia

Uso interno - MVP para equipo
