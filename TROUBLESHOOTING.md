# Troubleshooting - Error 502 Bad Gateway

## Error 502 en tickets.getdevtools.com

El error 502 Bad Gateway significa que CapRover no puede comunicarse con tu aplicación.

## Soluciones Comunes

### 1. Verificar que el contenedor esté corriendo

En CapRover:
1. Ve a tu app `contador-tickets`
2. Click en **"Logs"**
3. Verifica que el contenedor esté corriendo y sin errores

### 2. Verificar el puerto

El Dockerfile expone el puerto **5000**. En CapRover:
1. Ve a **"App Configs"**
2. Verifica que `PORT=5000` esté configurado
3. O asegúrate de que CapRover detecte automáticamente el puerto

### 3. Verificar el build

1. Ve a **"Deployment"**
2. Revisa los logs del último build
3. Verifica que no haya errores al construir la imagen

### 4. Reiniciar la aplicación

En CapRover:
1. Ve a tu app
2. Click en **"Restart"** o **"Rebuild"**

### 5. Verificar variables de entorno

Si necesitas configurar algo:
1. Ve a **"App Configs"**
2. Agrega: `PORT=5000`

### 6. Verificar logs detallados

```bash
# Desde CapRover CLI o panel web
# Ver logs en tiempo real
```

Los logs deberían mostrar:
- `✓ Servidor iniciado en http://0.0.0.0:5000`
- O errores específicos de Python/Flask

## Comandos Útiles

### Verificar que la app responde localmente

```bash
# Si tienes acceso SSH al servidor
docker ps | grep contador-tickets
docker logs contador-tickets
```

### Probar el contenedor localmente

```bash
cd "/home/josedowski/documentos/dev/idema/Contador de tickets"
docker build -t contador-tickets .
docker run -p 5000:5000 contador-tickets
```

Luego prueba: `curl http://localhost:5000/api/data`

## Problemas Comunes

### El puerto no coincide
- **Solución:** Verifica que el Dockerfile exponga el puerto 5000
- Verifica que CapRover esté configurado para usar el puerto 5000

### Dependencias faltantes
- **Solución:** Verifica que `requirements.txt` tenga todas las dependencias
- Revisa los logs del build

### Error en el código
- **Solución:** Revisa los logs de la aplicación
- Verifica que `app.py` no tenga errores de sintaxis

### Volumen no montado
- **Solución:** Verifica que el volumen `/app/data` esté configurado
- Los datos se guardan ahí, pero la app debería funcionar sin él

## Verificación Rápida

1. ✅ ¿El build completó exitosamente?
2. ✅ ¿El contenedor está corriendo?
3. ✅ ¿El puerto 5000 está expuesto?
4. ✅ ¿Los logs muestran que Flask inició?
5. ✅ ¿El dominio está configurado correctamente?

## Si nada funciona

1. **Rebuild completo:**
   - En CapRover, haz un "Force Rebuild"
   - Espera a que termine completamente

2. **Verificar Dockerfile:**
   - Asegúrate de que el CMD sea correcto
   - Verifica que gunicorn esté instalado

3. **Contactar soporte:**
   - Revisa los logs completos
   - Comparte los errores específicos
