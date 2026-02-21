# Guía de Debugging con Logs

## Logging Agregado al Endpoint `/api/topics/{topic_id}/stages`

Se ha agregado logging detallado para identificar errores 500 en el endpoint de creación de stages.

---

## 🔍 ¿Qué se está registrando?

### 1. Middleware Global (Todas las peticiones)
```
→ POST /api/topics/6/stages
← POST /api/topics/6/stages - 201 (0.145s)
```

En caso de error:
```
✗ POST /api/topics/6/stages - ERROR (0.082s)
Exception: TypeError: 'NoneType' object is not iterable
[Traceback completo]
```

### 2. Endpoint Específico (POST /topics/{id}/stages)

**Información registrada:**
- ✅ Topic ID y User ID al recibir la petición
- ✅ Datos del stage recibidos (title, description, content, etc.)
- ✅ Validación de topic existente
- ✅ Validación de permisos (professor_id)
- ✅ Datos finales antes de guardar en BD
- ✅ ID del stage creado exitosamente
- ✅ Errores con tipo de excepción y traceback completo

**Ejemplo de logs:**
```
[ADD_STAGE] Request received - Topic ID: 6, User: 5
[ADD_STAGE] Stage data: {'title': 'Etapa 1', 'description': '...', 'order': 1, ...}
[ADD_STAGE] Topic found - Professor ID: 5, Category: 2
[ADD_STAGE] Original stage data keys: dict_keys(['title', 'description', ...])
[ADD_STAGE] Final stage data: {'title': 'Etapa 1', 'topic_id': 6, 'professor_id': 5, ...}
[ADD_STAGE] Stage 42 created successfully for topic 6
```

En caso de error:
```
[ADD_STAGE] Error creating stage for topic 6: TypeError: 'NoneType' object is not iterable
Full traceback:
Traceback (most recent call last):
  File "app/api/endpoints/topics.py", line 95, in add_stage_to_topic
    db_stage = Stage(**stage_data)
  ...
```

---

## 🚀 Cómo usar los logs

### 1. Reiniciar el servidor
```bash
# En la terminal del servidor
poe dev
```

### 2. Hacer la petición que falla
Desde el frontend o con curl:
```bash
curl -X POST "http://localhost:8000/api/topics/6/stages" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Etapa Test",
    "description": "Descripción",
    "content": "Contenido",
    "order": 1
  }'
```

### 3. Revisar los logs en la consola
Busca líneas con:
- `[ADD_STAGE]` - Logs específicos del endpoint
- `✗ POST /api/topics/6/stages - ERROR` - Errores generales
- `Exception:` - Tipo de error
- `Traceback` - Stack trace completo

---

## 🐛 Errores Comunes y Soluciones

### Error: "column X does not exist"
**Causa:** Falta una columna en la base de datos  
**Solución:** Ejecutar `poe init-db` para aplicar migraciones

### Error: "'NoneType' object is not iterable"
**Causa:** Un campo esperado tiene valor `None` cuando debería ser una lista  
**Solución:** Verificar valores por defecto en el schema o modelo

### Error: "Stage() got an unexpected keyword argument 'X'"
**Causa:** El frontend envía un campo que no existe en el modelo  
**Solución:** Remover el campo del payload o agregarlo al modelo

### Error: "Topic not found"
**Causa:** El topic ID no existe en la base de datos  
**Solución:** Verificar que el topic fue creado correctamente

### Error: "Not authorized"
**Causa:** El usuario no es el profesor dueño del topic  
**Solución:** Verificar que el usuario tiene permisos correctos

---

## 📊 Nivel de Logs

Los logs están configurados en nivel **INFO**, lo que muestra:
- ✅ Peticiones HTTP (INFO)
- ✅ Operaciones importantes (INFO)
- ✅ Errores (ERROR)
- ✅ Advertencias (WARNING)
- ❌ Debug detallado (DEBUG) - desactivado por defecto

Para ver logs de DEBUG, cambia en `app/main.py`:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Cambiar a DEBUG
    ...
)
```

---

## 🔧 Desactivar Logs (Producción)

En producción, puedes reducir el nivel de logs:

```python
# app/main.py
logging.basicConfig(
    level=logging.WARNING,  # Solo advertencias y errores
    ...
)
```

O eliminar el middleware de logging si no es necesario.

---

## 📝 Próximos Pasos

1. ✅ Reinicia el servidor con `poe dev`
2. ✅ Reproduce el error 500
3. ✅ Copia los logs de la consola
4. ✅ Identifica el tipo de error y el traceback
5. ✅ Aplica la solución correspondiente

Los logs ahora te dirán exactamente qué está causando el error 500.
