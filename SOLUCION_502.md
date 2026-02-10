# Solución Inmediata para Error 502

## Problema Confirmado

Los logs muestran que:
- ✅ Gunicorn inicia correctamente
- ✅ La aplicación Flask se carga (`INFO:app:Aplicación Flask iniciada`)
- ❌ CapRover mata el contenedor después de ~3 segundos con señal `term`

**Esto significa que CapRover está haciendo un health check que está fallando.**

## Solución Rápida: Deshabilitar Health Check

### Paso 1: Ir a CapRover Dashboard

1. Abre tu CapRover dashboard
2. Ve a la app `contador-tickets`
3. Click en **"App Configs"** (o "HTTP Settings")

### Paso 2: Deshabilitar Health Check

1. Busca la sección **"Health Check"**
2. **Desmarca** la opción **"Enable Health Check"** (o "Health Check Enabled")
3. Click en **"Save & Update"** o **"Update"**

### Paso 3: Force Rebuild

1. Ve a la pestaña **"Deployment"**
2. Click en **"Force Rebuild"**
3. Espera 2-5 minutos

### Paso 4: Verificar

Después del rebuild, los logs deberían mostrar:
```
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:5000
[INFO] Booting worker with pid: X
```

**Y NO debería aparecer** `Handling signal: term` después de unos segundos.

## Alternativa: Configurar Health Check Correctamente

Si prefieres mantener el health check habilitado:

### Configuración Recomendada:

- **Health Check Path**: `/health`
- **Health Check Port**: `5000` (o déjalo vacío)
- **Health Check Interval**: `30` segundos (aumentar para dar más tiempo)
- **Health Check Timeout**: `10` segundos
- **Health Check Grace Period**: `60` segundos (tiempo antes de empezar a verificar)

### Verificar que `/health` funciona:

Después del deploy, prueba:
```bash
curl https://tickets.getdevtools.com/health
```

Debería responder:
```json
{"status": "ok", "service": "tickets-counter", "timestamp": "..."}
```

## Si el Problema Persiste

Si después de deshabilitar el health check sigue el 502:

1. **Verifica los logs completos** después del rebuild
2. **Verifica que el puerto 5000 está configurado correctamente** en CapRover:
   - App Configs → Port Mapping
   - Container Port: `5000`
3. **Verifica que no hay otros errores** en los logs (errores de Python, importación, etc.)

## Nota Importante

Deshabilitar el health check es una solución temporal válida. Una vez que la app esté funcionando, puedes volver a habilitarlo con la configuración correcta.
