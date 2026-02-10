# 🚀 Inicio Rápido - Deploy a contador-tickets.eirl.pe

## Pasos Rápidos

### 1. Crear Repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre: `contador-tickets`
3. Visibilidad: **Private**
4. **NO** marques ninguna opción (README, .gitignore, etc.)
5. Click en **"Create repository"**

### 2. Conectar y Subir Código

```bash
cd "/home/josedowski/documentos/dev/idema/Contador de tickets"

# Agregar remote (reemplaza USERNAME)
git remote add origin https://github.com/USERNAME/contador-tickets.git

# Subir código
git push -u origin main
```

Si tu branch se llama `master`:
```bash
git branch -M main
git push -u origin main
```

### 3. Deploy en CapRover

1. **Crear App:**
   - CapRover > Apps > Create New App
   - Nombre: `contador-tickets`

2. **Configurar Dominio:**
   - App > HTTP Settings
   - Custom Domain: `contador-tickets.eirl.pe`
   - Save

3. **Conectar GitHub:**
   - App > Deployment
   - Selecciona GitHub
   - Repositorio: `contador-tickets`
   - Branch: `main`
   - Dockerfile Path: `./Dockerfile`
   - Save & Update

4. **Configurar Volumen (IMPORTANTE):**
   - App > Volumes
   - Add Volume
   - Container Path: `/app/data`
   - Host Path: (vacío)
   - Save

5. **Deploy:**
   - Click en "Deploy"
   - Espera el build
   - ✅ Listo en: https://contador-tickets.eirl.pe

### 4. Configurar Jira (Opcional)

```bash
curl -X POST https://contador-tickets.eirl.pe/api/jira/config \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://tu-empresa.atlassian.net",
    "email": "tu-email@empresa.com",
    "api_token": "TU_TOKEN",
    "jql": "assignee = currentUser() AND status != Done"
  }'
```

## ✅ Verificar

```bash
# Verificar que funciona
curl https://contador-tickets.eirl.pe/api/data

# Debería responder con JSON de tus datos
```

## 📚 Documentación Completa

- `SETUP_GITHUB.md` - Guía detallada de GitHub
- `CAPROVER.md` - Guía detallada de CapRover
- `JIRA_SETUP.md` - Guía de integración con Jira
- `DEPLOY.md` - Guía general de deploy
