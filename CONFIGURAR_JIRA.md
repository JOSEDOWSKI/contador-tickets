# Configurar Jira - Guía Rápida

## Ya tienes tu API Token ✅

Tu token está listo. Ahora necesitas completar la configuración.

## Información que necesitas

1. **URL de tu instancia de Jira:**
   - Ejemplo: `https://tu-empresa.atlassian.net`
   - La encuentras en la URL cuando abres Jira en el navegador

2. **Tu email de Google:**
   - El mismo con el que inicias sesión en Jira
   - Ejemplo: `tu-nombre@gmail.com`

## Crear archivo de configuración

Una vez que tengas esos datos, crea `jira_config.json`:

```json
{
  "url": "https://TU-INSTANCIA.atlassian.net",
  "email": "tu-email@gmail.com",
  "api_token": "TU_TOKEN_AQUI",
  "jql": "assignee = currentUser() AND status != Done"
}
```

## Para uso local

1. Crea el archivo `jira_config.json` con los datos de arriba
2. Ejecuta la aplicación: `python3 app.py`
3. La sincronización con Jira será automática

## Para producción (CapRover)

Una vez deployado, configura vía API:

```bash
curl -X POST https://tickets.getdevtools.com/api/jira/config \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://TU-INSTANCIA.atlassian.net",
    "email": "tu-email@gmail.com",
    "api_token": "TU_TOKEN",
    "jql": "assignee = currentUser() AND status != Done"
  }'
```

## ⚠️ Seguridad

- El archivo `jira_config.json` NO se subirá a GitHub (está en .gitignore)
- No compartas tu API token públicamente
- Si comprometes el token, revócalo y crea uno nuevo
