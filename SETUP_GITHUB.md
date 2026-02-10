# Configurar Repositorio en GitHub

## Paso 1: Crear Repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre del repositorio: `contador-tickets` (o el que prefieras)
3. Descripción: "Contador de tickets con integración Jira"
4. Visibilidad: **Private** (recomendado para MVP interno)
5. **NO** inicialices con README, .gitignore o licencia (ya los tenemos)
6. Click en **"Create repository"**

## Paso 2: Conectar Repositorio Local con GitHub

GitHub te mostrará comandos, pero aquí están adaptados:

```bash
cd "/home/josedowski/documentos/dev/idema/Contador de tickets"

# Agregar remote (reemplaza USERNAME con tu usuario de GitHub)
git remote add origin https://github.com/USERNAME/contador-tickets.git

# O si prefieres SSH:
# git remote add origin git@github.com:USERNAME/contador-tickets.git

# Verificar que está configurado
git remote -v
```

## Paso 3: Subir Código a GitHub

```bash
# Subir código
git push -u origin main

# Si tu branch se llama 'master' en lugar de 'main':
# git branch -M main
# git push -u origin main
```

## Paso 4: Verificar

Ve a tu repositorio en GitHub y verifica que todos los archivos estén ahí.

## Archivos que NO se suben (por seguridad)

Gracias al `.gitignore`, estos archivos NO se subirán:
- ✅ `data/` - Tus datos mensuales
- ✅ `jira_config.json` - Configuración de Jira (credenciales)
- ✅ `tickets-data.json` - Datos antiguos
- ✅ Archivos de servicio systemd (solo para local)

## Siguiente Paso: Deploy en CapRover

Una vez subido a GitHub, sigue las instrucciones en `CAPROVER.md` para hacer deploy en `contador-tickets.eirl.pe`.
