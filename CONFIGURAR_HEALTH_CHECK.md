# Configurar Health Check en CapRover

## Problema Confirmado

Los logs muestran que la app se inicia correctamente pero CapRover la mata después de **~3 segundos**. Esto significa que **el health check está fallando o es demasiado agresivo**.

## Solución: Configurar Health Check Correctamente

### Paso 1: Ir a CapRover Dashboard

1. Ve a tu app `contador-tickets`
2. Click en **"App Configs"**
3. Ve a la sección **"Health Check"**

### Paso 2: Configurar Health Check (NO Deshabilitar)

**IMPORTANTE**: En lugar de deshabilitar, configura el health check con estos valores:

- ✅ **Enable Health Check**: **MARCADO** (habilitado)
- **Health Check Path**: `/health`
- **Health Check Port**: `5000` (o déjalo vacío)
- **Health Check Interval**: `30` segundos (tiempo entre verificaciones)
- **Health Check Timeout**: `10` segundos (tiempo máximo para responder)
- **Health Check Grace Period**: `120` segundos (**MUY IMPORTANTE**: tiempo antes de empezar a verificar)

### Paso 3: Guardar y Rebuild

1. Click en **"Save & Update"** o **"Update"**
2. Ve a **"Deployment"**
3. Click en **"Force Rebuild"**
4. Espera 2-5 minutos

### Paso 4: Verificar Logs

Después del rebuild, los logs deberían mostrar:
```
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:5000
[INFO] Booting worker with pid: X
Aplicación Flask iniciada correctamente
```

**Y NO debería aparecer** `Handling signal: term` después de unos segundos.

## ¿Por Qué Grace Period de 120 Segundos?

El **Grace Period** es el tiempo que CapRover espera **antes de empezar a hacer health checks**. 

- Si es muy corto (ej: 5 segundos), CapRover empezará a verificar antes de que la app esté lista
- Con 120 segundos, damos tiempo suficiente para que:
  - El contenedor inicie
  - Gunicorn se inicie
  - Los workers se inicien
  - Flask termine de inicializar
  - La app esté lista para responder

## Si el Problema Persiste

Si después de configurar el health check con estos valores sigue el problema:

1. **Aumenta el Grace Period** a 180 segundos (3 minutos)
2. **Verifica que el puerto 5000 esté configurado correctamente** en Port Mapping
3. **Comparte los logs completos** después del rebuild

## Alternativa: Verificar Health Check Manualmente

Después del rebuild, espera ~30 segundos y luego prueba:

```bash
curl https://tickets.getdevtools.com/health
```

Debería responder:
```json
{"status":"ok"}
```

Si responde correctamente pero CapRover sigue matando el contenedor, el problema está en la configuración del health check en CapRover.
