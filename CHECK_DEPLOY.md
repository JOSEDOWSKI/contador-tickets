# Checklist de Deploy - Error 502

## Pasos para Diagnosticar

### 1. Verificar Logs en CapRover

En el panel de CapRover:
1. Ve a tu app `contador-tickets`
2. Click en **"Logs"** o **"App Logs"**
3. Busca errores como:
   - `ModuleNotFoundError`
   - `ImportError`
   - `Address already in use`
   - Errores de conexión

### 2. Verificar Build

1. Ve a **"Deployment"** > **"Build Logs"**
2. Verifica que el build completó sin errores
3. Busca mensajes como:
   - `Successfully built`
   - `Successfully tagged`

### 3. Verificar Configuración del Puerto

En CapRover:
1. Ve a **"App Configs"**
2. Verifica que NO haya variables de entorno que cambien el puerto
3. El Dockerfile ya expone el puerto 5000, CapRover debería detectarlo automáticamente

### 4. Verificar que el Contenedor Esté Corriendo

En CapRover:
1. Ve a **"App Details"**
2. Verifica el estado: debería decir "Running" o "Healthy"

### 5. Reiniciar la Aplicación

1. Click en **"Restart"** o **"Rebuild"**
2. Espera a que termine completamente
3. Verifica los logs nuevamente

## Solución Rápida

Si el problema persiste, intenta:

1. **Force Rebuild:**
   - En CapRover, haz un "Force Rebuild"
   - Esto reconstruye la imagen desde cero

2. **Verificar el dominio:**
   - Asegúrate de que `tickets.getdevtools.com` esté correctamente configurado
   - Verifica que apunte al servidor correcto

3. **Verificar DNS:**
   - Asegúrate de que el DNS de `tickets.getdevtools.com` apunte a tu servidor CapRover

## Comandos para Verificar Localmente

Si tienes acceso SSH al servidor:

```bash
# Ver contenedores corriendo
docker ps | grep tickets

# Ver logs del contenedor
docker logs contador-tickets --tail 50

# Ver si el puerto está expuesto
docker port contador-tickets
```

## Verificación del Código

El código está correcto y probado. El problema es probablemente de configuración en CapRover.
