# Guía de Deploy en CapRover

## Requisitos Previos

1. CapRover instalado y funcionando
2. Repositorio en GitHub
3. Acceso a tu servidor CapRover

## Pasos para Deploy

### 1. Preparar el Repositorio

```bash
# Asegúrate de tener todos los archivos necesarios
git add .
git commit -m "Preparar para deploy en CapRover"
git push origin main
```

### 2. Migrar Datos Locales (Importante)

Antes de hacer deploy, migra tus datos actuales:

```bash
python3 migrate_data.py
```

Esto creará:
- `data/tickets-YYYY-MM.json` con tus datos actuales
- `tickets-data.json.backup` como respaldo

### 3. Configurar en CapRover

1. **Crear nueva app en CapRover:**
   - Ve a tu panel de CapRover
   - Click en "One-Click Apps/Databases" o "Apps"
   - Click en "Create New App"
   - Nombre: `tickets-counter`

2. **Conectar con GitHub:**
   - En la sección "Deployment Method"
   - Selecciona "GitHub"
   - Conecta tu repositorio
   - Branch: `main` (o tu branch principal)
   - Dockerfile Path: `./Dockerfile`

3. **Configurar Variables de Entorno:**
   - `PORT=5000` (ya está en el Dockerfile, pero puedes cambiarlo)

4. **Configurar Volúmenes Persistentes:**
   - Click en "Volumes"
   - Agregar volumen:
     - Container Path: `/app/data`
     - Host Path: (dejar vacío para que CapRover lo maneje)
   - Esto preservará tus datos entre deploys

### 4. Configurar Jira (Opcional)

1. **Obtener API Token de Jira:**
   - Ve a: https://id.atlassian.com/manage-profile/security/api-tokens
   - Click en "Create API token"
   - Copia el token generado

2. **Configurar en la app:**
   - Una vez deployada, accede a la aplicación
   - Usa la API para configurar Jira:
   ```bash
   curl -X POST https://tu-app.caprover.com/api/jira/config \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://tu-empresa.atlassian.net",
       "email": "tu-email@empresa.com",
       "api_token": "tu-api-token",
       "jql": "assignee = currentUser() AND status != Done"
     }'
   ```

   O crea `jira_config.json` localmente y súbelo como volumen:
   ```json
   {
     "url": "https://tu-empresa.atlassian.net",
     "email": "tu-email@empresa.com",
     "api_token": "tu-api-token",
     "jql": "assignee = currentUser() AND status != Done"
   }
   ```

### 5. Deploy

1. Click en "Deploy" en CapRover
2. Espera a que termine el build
3. Tu app estará disponible en: `https://tickets-counter.tu-dominio.com`

## Migrar Datos Existentes

Si ya tienes datos en producción local y quieres migrarlos:

1. **Exportar datos locales:**
   ```bash
   # En tu máquina local
   tar -czf tickets-data-backup.tar.gz data/ tickets-data.json
   ```

2. **Subir a CapRover:**
   ```bash
   # Usar CapRover CLI o panel web para subir el archivo
   # O usar scp si tienes acceso SSH
   ```

3. **Restaurar en el contenedor:**
   ```bash
   # Conectarse al contenedor
   caprover exec -a tickets-counter
   
   # Dentro del contenedor, restaurar datos
   # (los datos deberían estar en /app/data)
   ```

## Estructura de Datos

Los datos se guardan mensualmente en:
```
data/
  ├── tickets-2026-02.json
  ├── tickets-2026-03.json
  └── ...
```

Cada archivo contiene:
```json
{
  "pendingTickets": 0,
  "totalTickets": 51,
  "resolvedTickets": 51,
  "month": "2026-02",
  "history": [...]
}
```

## API Endpoints

- `GET /api/data` - Obtiene datos del mes actual
- `POST /api/save` - Guarda datos
- `GET /api/months` - Lista meses disponibles
- `GET /api/month/<month>` - Obtiene datos de un mes específico
- `GET /api/jira/config` - Obtiene configuración de Jira
- `POST /api/jira/config` - Configura Jira
- `POST /api/jira/sync` - Sincroniza manualmente con Jira

## Troubleshooting

### Los datos no persisten

- Verifica que el volumen esté configurado correctamente
- Revisa los logs: `caprover logs -a tickets-counter`

### Error al conectar con Jira

- Verifica que el API token sea correcto
- Revisa que la URL de Jira sea correcta
- Verifica que el JQL sea válido

### Build falla

- Verifica que `requirements.txt` esté presente
- Revisa los logs de build en CapRover
