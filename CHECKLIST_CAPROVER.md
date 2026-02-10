# Checklist para Resolver el 502 en CapRover

## ✅ Verificaciones Necesarias en CapRover

### 1. Verificar Configuración de Puerto

**En CapRover Dashboard:**
1. Ve a tu app `contador-tickets`
2. Click en **"App Configs"**
3. Ve a **"Port Mapping"** o **"HTTP Settings"**
4. Verifica:
   - **Container Port**: Debe ser `5000`
   - **HTTP Port**: Debe estar configurado (normalmente 80/443)

### 2. Deshabilitar Health Check (SOLUCIÓN INMEDIATA)

**En CapRover Dashboard:**
1. Ve a **"App Configs"** → **"Health Check"**
2. **DESMARCA** completamente la opción **"Enable Health Check"**
3. Click en **"Save & Update"** o **"Update"**

### 3. Verificar Variables de Entorno

**En CapRover Dashboard:**
1. Ve a **"App Configs"** → **"Environment Variables"**
2. Verifica que NO haya variables que puedan estar causando problemas
3. Si hay variables relacionadas con health check, elimínalas temporalmente

### 4. Verificar Volúmenes

**En CapRover Dashboard:**
1. Ve a **"App Configs"** → **"Volumes"**
2. Verifica que el volumen `/app/data` esté configurado correctamente
3. Si no está configurado, agrégalo:
   - **Volume Name**: `tickets-data` (o cualquier nombre)
   - **Mount Path**: `/app/data`

### 5. Force Rebuild

**Después de hacer los cambios anteriores:**
1. Ve a **"Deployment"**
2. Click en **"Force Rebuild"**
3. Espera 2-5 minutos
4. **NO cierres la pestaña de logs**

### 6. Verificar Logs Después del Rebuild

**Los logs deberían mostrar:**
```
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:5000
[INFO] Booting worker with pid: X
INFO:app:Aplicación Flask iniciada
```

**Y NO debería aparecer:**
- `Handling signal: term` después de unos segundos
- `Shutting down: Master` inmediatamente
- Errores de Python o importación

### 7. Probar Endpoints

**Después de que los logs muestren que la app está corriendo:**

```bash
# Health check
curl https://tickets.getdevtools.com/health

# Página principal
curl https://tickets.getdevtools.com/

# API de datos
curl https://tickets.getdevtools.com/api/data
```

## ⚠️ Si el Problema Persiste

Si después de deshabilitar el health check sigue el 502:

1. **Comparte los logs completos** después del rebuild
2. **Verifica la configuración del puerto** en CapRover
3. **Verifica que el Dockerfile esté correcto** (puerto 5000)
4. **Revisa si hay otros servicios** usando el puerto 5000

## 📝 Notas Importantes

- **Deshabilitar el health check es una solución válida** para aplicaciones simples
- Una vez que la app funcione, puedes volver a habilitar el health check con configuración correcta
- El health check necesita tiempo para que la app inicie completamente antes de empezar a verificar
