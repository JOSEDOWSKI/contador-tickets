# Deploy en CapRover - tickets.getdevtools.com

## Configuración Específica para getdevtools.com

### 1. Crear App en CapRover

1. Accede a tu panel de CapRover
2. Click en **"Apps"** > **"One-Click Apps/Databases"**
3. Click en **"Create New App"**
4. Nombre de la app: `contador-tickets` (o `tickets`)

### 2. Configurar Dominio

1. En la app `contador-tickets`, ve a **"HTTP Settings"**
2. En **"Custom Domain"**, agrega: `tickets.getdevtools.com`
3. Click en **"Save"**

### 3. Conectar con GitHub

1. En la app `contador-tickets`, ve a **"Deployment"**
2. Selecciona **"GitHub"**
3. Autoriza CapRover si es necesario
4. Selecciona tu repositorio
5. Branch: `main` (o tu branch principal)
6. Dockerfile Path: `./Dockerfile`
7. Click en **"Save & Update"**

### 4. Configurar Volumen Persistente

**IMPORTANTE:** Para que los datos no se pierdan:

1. En la app `contador-tickets`, ve a **"Volumes"**
2. Click en **"Add Volume"**
3. Container Path: `/app/data`
4. Host Path: (dejar vacío - CapRover lo maneja automáticamente)
5. Click en **"Save"**

### 5. Variables de Entorno (Opcional)

Si necesitas configurar algo específico:

1. Ve a **"App Configs"**
2. Agrega variables si es necesario:
   - `PORT=5000` (ya está en Dockerfile)

### 6. Deploy

1. Click en **"Deploy"**
2. Espera a que termine el build
3. Tu app estará disponible en: **https://tickets.getdevtools.com**

## Configurar Jira en Producción

Una vez deployado, configura Jira usando la API:

```bash
curl -X POST https://tickets.getdevtools.com/api/jira/config \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://tu-empresa.atlassian.net",
    "email": "tu-email@empresa.com",
    "api_token": "TU_API_TOKEN",
    "jql": "assignee = currentUser() AND status != Done"
  }'
```

O crea `jira_config.json` localmente y súbelo como volumen en CapRover.

## Verificar Deploy

```bash
# Verificar que la app responde
curl https://tickets.getdevtools.com/api/data

# Ver logs
# Desde CapRover: App > Logs
```

## Troubleshooting

### Los datos no persisten
- Verifica que el volumen `/app/data` esté configurado
- Revisa los logs en CapRover

### Error 502 Bad Gateway
- Verifica que el puerto sea 5000
- Revisa los logs de la app

### Dominio no funciona
- Verifica DNS: `tickets.getdevtools.com` debe apuntar a tu servidor CapRover
- Verifica configuración en CapRover HTTP Settings
