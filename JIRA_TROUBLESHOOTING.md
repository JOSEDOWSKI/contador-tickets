# Solución de Problemas con Jira

## Problemas Comunes en Espacios Compartidos

### 1. El JQL por defecto no funciona

**Problema**: `assignee = currentUser() AND status != Done` no encuentra tickets.

**Soluciones**:

#### Opción A: Filtrar por proyecto específico
```
project = "NOMBRE_DEL_PROYECTO" AND assignee = currentUser() AND status != Done
```

#### Opción B: Sin filtrar por estado
```
assignee = currentUser()
```
Esto traerá todos tus tickets, y la app los contará automáticamente.

#### Opción C: Filtrar por estados específicos
```
assignee = currentUser() AND status IN ("To Do", "In Progress", "En Revisión")
```

### 2. Verificar que el JQL funciona

Puedes probar tu JQL directamente en Jira:

1. Ve a tu espacio de Jira
2. Click en "Filtros" → "Búsqueda avanzada"
3. Pega tu JQL en el campo de búsqueda
4. Verifica que encuentre los tickets correctos

### 3. Verificar permisos del API Token

El API Token necesita permisos para:
- ✅ Leer issues (tickets)
- ✅ Ver proyectos
- ✅ Ver estados

Si tu espacio tiene restricciones de permisos, puede que necesites:
- Solicitar permisos adicionales al administrador del espacio
- O usar un JQL que solo busque en proyectos donde tienes acceso

### 4. Estados personalizados

Si tu espacio usa estados personalizados (no "Done"), ajusta el JQL:

**Ejemplo para estados en español:**
```
assignee = currentUser() AND status != "Completado" AND status != "Cerrado"
```

**Ejemplo para múltiples estados resueltos:**
```
assignee = currentUser() AND status NOT IN ("Done", "Completado", "Cerrado", "Resuelto")
```

### 5. Probar la configuración

Una vez configurado, prueba sincronizar:

1. Click en "🔄 Sincronizar Jira"
2. Revisa el mensaje de estado debajo del botón
3. Si hay error, revisa la consola del navegador (F12) para ver el mensaje completo

### 6. Logs del servidor

Si el problema persiste, revisa los logs del servidor en CapRover:
- Ve a los logs de la aplicación
- Busca mensajes que contengan "Jira API" o "Error obteniendo tickets"

## JQL Recomendado para Espacios Compartidos

### Solo tus tickets en un proyecto específico:
```
project = "MI_PROYECTO" AND assignee = currentUser()
```

### Todos tus tickets sin filtrar por estado:
```
assignee = currentUser()
```

### Tickets pendientes con estados específicos:
```
assignee = currentUser() AND status IN ("To Do", "In Progress", "En Progreso", "Pendiente")
```

## ¿Necesitas ayuda?

Si después de probar estos JQL sigue sin funcionar:

1. Comparte el mensaje de error exacto que aparece
2. Comparte el JQL que estás usando
3. Verifica que el JQL funciona en Jira directamente
