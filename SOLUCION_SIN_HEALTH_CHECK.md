# Solución para CapRover Sin Opción de Health Check

## Problema

Tu CapRover no tiene la opción de configurar health check en la UI, pero está usando un health check automático que mata el contenedor después de ~3 segundos.

## Solución Implementada

He hecho dos cambios importantes:

### 1. Health Check Inmediato

El health check ahora se registra **inmediatamente** después de crear la app Flask, antes de cualquier otra inicialización. Esto asegura que responda incluso durante la inicialización.

### 2. Script de Inicio

He creado un script `start.sh` que:
- Espera 2 segundos antes de iniciar gunicorn (para que el contenedor esté listo)
- Inicia gunicorn con la configuración correcta

### 3. Rutas Tempranas

Las rutas `/health` y `/` se registran dos veces:
- Una vez inmediatamente después de crear la app (para respuesta temprana)
- Una vez después de la inicialización completa (para funcionalidad completa)

## Próximos Pasos

### 1. Force Rebuild

1. Ve a CapRover Dashboard
2. Ve a tu app `contador-tickets`
3. Click en **"Deployment"**
4. Click en **"Force Rebuild"**
5. Espera 2-5 minutos

### 2. Verificar Logs

Después del rebuild, los logs deberían mostrar:
```
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:5000
[INFO] Booting worker with pid: X
Aplicación Flask iniciada correctamente
```

**Y NO debería aparecer** `Handling signal: term` después de unos segundos.

### 3. Probar Endpoints

Una vez que los logs muestren que la app está corriendo:

```bash
# Health check
curl https://tickets.getdevtools.com/health

# Debería responder:
# {"status":"ok"}

# Root
curl https://tickets.getdevtools.com/

# Debería responder con HTML
```

## Si el Problema Persiste

Si después de este cambio sigue el 502:

1. **Verifica las variables de entorno** en CapRover:
   - Ve a "App Configs" → "Environment Variables"
   - Verifica que NO haya variables relacionadas con health check
   - Si hay `HEALTH_CHECK_*` o similares, elimínalas

2. **Verifica la configuración del puerto**:
   - En "App Configs" → "Port Mapping" (o donde esté)
   - Container Port: debe ser `5000`

3. **Comparte los logs completos** desde el último rebuild

## Nota sobre Health Check Automático

CapRover puede tener un health check automático que:
- Verifica el puerto después de ~3 segundos
- Si no responde, mata el contenedor
- No se puede deshabilitar desde la UI

La solución es hacer que la app responda **inmediatamente**, incluso durante la inicialización, que es lo que hemos implementado.
