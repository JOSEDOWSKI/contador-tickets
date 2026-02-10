# Configuración de Health Check en CapRover

## Problema Detectado

Los logs muestran que gunicorn se inicia correctamente pero recibe una señal `term` (terminación) después de ~3 segundos. Esto indica que **CapRover está matando el contenedor** porque el health check está fallando o no está configurado.

## Solución: Configurar Health Check en CapRover

### Paso 1: Ir a la Configuración de la App

1. En CapRover, ve a tu app `contador-tickets`
2. Click en **"App Configs"** (o "HTTP Settings")
3. Busca la sección **"Health Check"**

### Paso 2: Configurar el Health Check

Configura lo siguiente:

- **Health Check Path**: `/health`
- **Health Check Port**: `5000` (o déjalo vacío si usa el puerto por defecto)
- **Health Check Interval**: `10` (segundos)
- **Health Check Timeout**: `5` (segundos)
- **Health Check Grace Period**: `30` (segundos)

### Paso 3: Verificar Configuración de Puerto

En **"App Configs"** → **"Port Mapping"**:
- **Container Port**: `5000`
- **HTTP Port**: (el puerto que CapRover asigna, normalmente 80/443)

### Paso 4: Deshabilitar Health Check Temporalmente (si es necesario)

Si el problema persiste, puedes **deshabilitar temporalmente el health check**:
- En **"App Configs"** → **"Health Check"**
- Desmarca **"Enable Health Check"**
- Guarda y haz rebuild

Esto permitirá que la app se inicie sin ser matada, y luego puedes volver a habilitarlo.

## Verificar que el Health Check Funciona

Después del rebuild, prueba:

```bash
curl https://tickets.getdevtools.com/health
```

Debería responder:
```json
{
  "status": "ok",
  "service": "tickets-counter",
  "timestamp": "2026-02-10T..."
}
```

## Logs Esperados Después del Fix

Después de configurar el health check correctamente, los logs deberían mostrar:
- Gunicorn iniciando
- Workers iniciando
- **NO** debería aparecer `Handling signal: term` inmediatamente
- La app debería seguir corriendo

## Si el Problema Persiste

Si después de configurar el health check sigue el problema:

1. **Deshabilita el health check temporalmente** para que la app pueda iniciar
2. Verifica que la app responde en `/health` manualmente
3. Una vez que funcione, vuelve a habilitar el health check con los valores correctos
