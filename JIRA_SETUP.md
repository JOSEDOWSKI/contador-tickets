# Guía de Integración con Jira

## ¿Cómo Funciona?

La aplicación se conecta a la API de Jira para:

- ✅ Detectar automáticamente tus tickets pendientes
- ✅ Contar tickets resueltos/cerrados
- ✅ Sincronizar datos cada vez que cargas la página
- ✅ Sincronización manual con un botón

## Paso 1: Obtener API Token de Jira

### Si usas autenticación con Google:

1. Ve a: https://id.atlassian.com/manage-profile/security/api-tokens
2. Si te pide iniciar sesión, usa tu cuenta de Google
3. Click en **"Create API token"**
4. Dale un nombre (ej: "Contador de Tickets")
5. **Copia el token** generado (solo se muestra una vez)

**Nota importante:** Si usas Google para autenticarte en Jira:

- El **email** que debes usar en la configuración es el email de tu cuenta de Google asociada a Jira
- El **API token** funciona igual independientemente de cómo inicies sesión
- No necesitas la contraseña de Google, solo el API token

## Paso 2: Configurar la Integración

### Opción A: Archivo de Configuración (Local)

1. Copia el archivo de ejemplo:

   ```bash
   cp jira_config.json.example jira_config.json
   ```
2. Edita `jira_config.json` con tus datos:

   ```json
   {
     "url": "https://tu-empresa.atlassian.net",
     "email": "tu-email@gmail.com",
     "api_token": "TU_TOKEN_AQUI",
     "jql": "assignee = currentUser() AND status != Done"
   }
   ```

   **Campos:**

   - `url`: URL de tu instancia de Jira (ej: `https://miempresa.atlassian.net`)
   - `email`: Tu email de Google asociado a Jira (el mismo con el que inicias sesión)
   - `api_token`: El token que copiaste en el paso 1
   - `jql`: Query de Jira para filtrar tickets (opcional, tiene un valor por defecto)

   **Si usas Google para autenticarte:**

   - `email`: Usa el email de tu cuenta de Google (ej: `tu-nombre@gmail.com`)
   - No necesitas la contraseña de Google, solo el API token

### Opción B: Configuración vía API (Producción)

```bash
curl -X POST https://tu-app.caprover.com/api/jira/config \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://tu-empresa.atlassian.net",
    "email": "tu-email@empresa.com",
    "api_token": "TU_TOKEN_AQUI",
    "jql": "assignee = currentUser() AND status != Done"
  }'
```

## Paso 3: Personalizar la Búsqueda (JQL)

El campo `jql` permite personalizar qué tickets contar. Ejemplos:

### Solo mis tickets pendientes:

```json
"jql": "assignee = currentUser() AND status != Done"
```

### Tickets de mi equipo:

```json
"jql": "assignee in (user1@empresa.com, user2@empresa.com) AND status != Done"
```

### Tickets de un proyecto específico:

```json
"jql": "project = PROYECTO AND assignee = currentUser() AND status != Done"
```

### Tickets de alta prioridad:

```json
"jql": "assignee = currentUser() AND priority = High AND status != Done"
```

### Todos los tickets abiertos:

```json
"jql": "status != Done AND status != Closed"
```

## Paso 4: Usar la Integración

### Sincronización Automática

Cada vez que cargas la página, la aplicación:

1. Intenta conectarse a Jira (si está configurado)
2. Obtiene el conteo de tickets
3. Muestra los datos actualizados

### Sincronización Manual

- Click en el botón **"🔄 Sincronizar Jira"**
- O presiona `Ctrl+S` (o `Cmd+S` en Mac)

## Verificar la Configuración

Puedes verificar si Jira está configurado:

```bash
curl https://tu-app.com/api/jira/config
```

Respuesta si está configurado:

```json
{
  "configured": true,
  "url": "https://tu-empresa.atlassian.net",
  "email": "tu-email@empresa.com",
  "jql": "assignee = currentUser() AND status != Done"
}
```

## Troubleshooting

### Error: "Failed to sync with Jira"

**Causas comunes:**

1. **Token incorrecto**: Verifica que el API token sea correcto
2. **URL incorrecta**: Asegúrate de que la URL de Jira sea correcta (sin `/` al final)
3. **Email incorrecto**: Debe ser el email de tu cuenta de Jira
4. **JQL inválido**: Verifica que la query JQL sea válida

### Verificar Token

Puedes probar tu token manualmente:

```bash
# Si usas Google, usa tu email de Google:
curl -u "tu-email@gmail.com:TU_TOKEN" \
  "https://tu-empresa.atlassian.net/rest/api/3/myself"
```

Si funciona, deberías ver información de tu usuario.

**Nota para usuarios de Google:**

- Usa tu email de Google (el mismo con el que inicias sesión en Jira)
- El formato es: `email:token` (sin espacios)
- No necesitas la contraseña de Google

### Verificar JQL

Puedes probar tu JQL en Jira:

1. Ve a Jira
2. Click en "Issues" > "Search for issues"
3. Click en "Advanced"
4. Pega tu JQL
5. Verifica que funcione

## Seguridad

⚠️ **Importante:**

- El `jira_config.json` contiene credenciales sensibles
- **NO** lo subas a GitHub (está en `.gitignore`)
- En producción, usa variables de entorno o secretos de CapRover
- El token tiene acceso a tus tickets según los permisos de tu cuenta

## Ejemplo Completo

### Ejemplo con cuenta Google:

```json
{
  "url": "https://miempresa.atlassian.net",
  "email": "juan.perez@gmail.com",
  "api_token": "ATATT3xFfGF0...",
  "jql": "project = DEV AND assignee = currentUser() AND status in (\"In Progress\", \"To Do\")"
}
```

### Ejemplo con cuenta corporativa:

```json
{
  "url": "https://miempresa.atlassian.net",
  "email": "juan.perez@miempresa.com",
  "api_token": "ATATT3xFfGF0...",
  "jql": "project = DEV AND assignee = currentUser() AND status in (\"In Progress\", \"To Do\")"
}
```

**Importante:** Usa el email con el que inicias sesión en Jira, ya sea de Google o corporativo.
Esto contará solo los tickets del proyecto "DEV" que están asignados a ti y en estado "In Progress" o "To Do".
