# Etapas (Stages)

> [!IMPORTANT]
> **Cambio Arquitectónico:** Los Stages ahora pertenecen a Topics, no directamente a Categories.
> - **Antes:** Category → Stages
> - **Ahora:** Category → Topics → Stages
>
> Para obtener stages, primero debes obtener los topics de una categoría, luego los stages de cada topic.
> Ver [Topics Documentation](topics.md) para más información.

## Descripción
Las Stages (Etapas) son las unidades individuales de aprendizaje dentro de un Topic. Cada stage contiene:
- Contenido educativo (texto, imágenes, videos)
- Descripción de desafío
- Configuración interactiva (quizzes, drag-and-drop, matching)

Los stages deben completarse secuencialmente: solo el primer stage de un topic está desbloqueado inicialmente.

## Flujo de Uso

1. Estudiante selecciona una **Category**
2. Ve los **Topics** aprobados en esa categoría (`GET /categories/{id}/topics`)
3. Selecciona un Topic
4. Obtiene los **Stages** del topic con progreso (`GET /topics/{id}/stages/progress`)
5. Completa stages secuencialmente (`POST /stages/{id}/complete`)

## Endpoints de Stages

### 1. Obtener Stages de un Topic con Progreso
**Ver:** `GET /topics/{topic_id}/stages/progress` en [Topics Documentation](topics.md)

Este es el endpoint principal para estudiantes. Reemplaza el antiguo `/categories/{id}/stages/progress`.

---

### 2. Completar Stage
**POST** `/stages/{stage_id}/complete`

Marca un stage como completado y desbloquea automáticamente el siguiente stage en la secuencia.

**Autenticación:** Requiere autenticación

**Path Parameters:**
- `stage_id` (int, requerido): ID del stage a completar

**Requisitos:**
- El stage debe estar desbloqueado para el usuario
- El usuario debe haber completado exitosamente el desafío


### 3. Obtener Stage Individual
**GET** `/stages/{stage_id}`

Obtiene el detalle de un stage específico.

**Autenticación:** Requiere autenticación

**Path Parameters:**
- `stage_id` (int, requerido): ID del stage

**Respuesta 200:**
```json
{
  "id": 2,
  "topic_id": 1,
  "order": 2,
  "title": "Variables",
  "description": "Tipos de datos y variables",
  "content": "En programación, las variables...",
  "challenge_description": "Declara una variable y asígnale un valor",
  "media_url": null,
  "media_type": null,
  "interactive_config": {
    "type": "drag_and_drop",
    "items": [...]
  },
  "is_active": true,
  "professor_id": 5
}
```

**Ejemplo:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/stages/2"
```

---

### 4. Crear Stage (Profesor)
**POST** `/stages`

Crea un nuevo stage. Debe pertenecer a un topic existente.

**Autenticación:** Requiere rol `professor`

**Request Body:**
```json
{
  "topic_id": 1,
  "order": 4,
  "title": "Funciones",
  "description": "Definiendo funciones en JavaScript",
  "content": "Contenido sobre funciones...",
  "challenge_description": "Escribe una función que sume dos números",
  "is_active": true,
  "interactive_config": {
    "type": "matching",
    "pairs": [
      {"left": "function", "right": "Palabra clave para definir funciones"}
    ]
  }
}
```

**Respuesta 200:**
```json
{
  "id": 150,
  "topic_id": 1,
  "order": 4,
  "title": "Funciones",
  "description": "Definiendo funciones en JavaScript",
  "content": "Contenido sobre funciones...",
  "is_active": true,
  "professor_id": 5
}
```

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/stages" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic_id": 1,
    "order": 4,
    "title": "Funciones",
    "description": "Definiendo funciones",
    "content": "Las funciones son...",
    "challenge_description": "Crea una función",
    "is_active": true
  }'
```

---

### 5. Actualizar Stage (Profesor)
**PUT** `/stages/{stage_id}`

Actualiza un stage existente. Solo el profesor propietario o admin pueden actualizar.

**Autenticación:** Requiere rol `professor`

**Path Parameters:**
- `stage_id` (int, requerido): ID del stage

**Request Body:**
```json
{
  "title": "Funciones y Scope",
  "content": "Nuevo contenido actualizado...",
  "is_active": true
}
```

**Respuesta 200:**
```json
{
  "id": 150,
  "topic_id": 1,
  "order": 4,
  "title": "Funciones y Scope",
  "content": "Nuevo contenido actualizado...",
  "is_active": true
}
```

**Respuesta 403:**
```json
{
  "detail": "You can only update your own stages"
}
```

---

### 6. Eliminar Stage (Profesor)
**DELETE** `/stages/{stage_id}`

Elimina (soft delete) un stage. Solo el profesor propietario o admin pueden eliminar.

**Autenticación:** Requiere rol `professor`

**Path Parameters:**
- `stage_id` (int, requerido): ID del stage

**Respuesta 204:** No content (éxito)

**Respuesta 403:**
```json
{
  "detail": "You can only delete your own stages"
}
```

**Ejemplo:**
```bash
curl -X DELETE "http://localhost:8000/stages/150" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 7. Configurar Desafío Interactivo (Profesor)
**POST** `/stages/{stage_id}/interactive`

Configura o actualiza el desafío interactivo (drag-and-drop, matching) de un stage.

**Autenticación:** Requiere rol `professor`

**Path Parameters:**
- `stage_id` (int, requerido): ID del stage

**Request Body:**
```json
{
  "type": "drag_and_drop",
  "description": "Arrastra los elementos a su zona correcta",
  "items": [
    {
      "id": "1",
      "text": "let",
      "correct_zone": "zone1"
    },
    {
      "id": "2",
      "text": "const",
      "correct_zone": "zone2"
    }
  ],
  "zones": [
    {"id": "zone1", "label": "Variables mutables"},
    {"id": "zone2", "label": "Variables inmutables"}
  ]
}
```

**Respuesta 200:**
```json
{
  "id": 150,
  "topic_id": 1,
  "order": 4,
  "title": "Funciones y Scope",
  "interactive_config": {
    "type": "drag_and_drop",
    "description": "Arrastra los elementos...",
    "items": [...]
  },
  "is_active": true
}
```

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/stages/150/interactive" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "matching",
    "pairs": [
      {"left": "Variable", "right": "Almacena un valor"}
    ]
  }'
```

---

## Notas Importantes

1. **Pertenencia a Topics:** Cada stage debe tener un `topic_id`. Los stages no pertenecen directamente a categorías.

2. **Aprobación:** La aprobación NO se hace a nivel de stage individual, sino a nivel de **Topic completo**. Ver [Topics Documentation](topics.md).

3. **Progreso Secuencial:** Los stages deben completarse en orden. Solo el primer stage está desbloqueado inicialmente.

4. **Soft Delete:** La eliminación de stages es lógica (`is_active = false`), no física.

5. **Desafíos Interactivos:** Cada stage puede tener un desafío interactivo configurado en `interactive_config`. Tipos soportados:
   - `drag_and_drop`: Arrastrar elementos a zonas
   - `matching`: Emparejar elementos

## Endpoints Obsoletos (Removidos)

Los siguientes endpoints ya NO existen:

- ❌ `GET /categories/{id}/stages` → Use `GET /categories/{id}/topics` + `GET /topics/{id}/stages/progress`
- ❌ `GET /categories/{id}/stages/progress` → Use `GET /topics/{id}/stages/progress`
- ❌ `POST /categories/{id}/initialize` → Inicialización automática al acceder a stages
- ❌ `GET /review/pending` (stages) → Use `GET /topics/pending/review`
- ❌ `POST /stages/{id}/review` → Use `POST /topics/{id}/review`

## Migración

Si tu código usaba los endpoints antiguos, debes actualizar a:

**Antes:**
```javascript
// ❌ Antiguo
const stages = await fetch(`/api/categories/${categoryId}/stages/progress`)
```

**Ahora:**
```javascript
// ✅ Nuevo
// 1. Obtener topics de la categoría
const topics = await fetch(`/api/categories/${categoryId}/topics`)

// 2. Para cada topic, obtener sus stages con progreso
const stages = await fetch(`/api/topics/${topicId}/stages/progress`)
```

## Ver También

- [Topics Documentation](topics.md) - Sistema de revisión y aprobación
- [Interactive Challenges](interactive_challenges.md) - Configuración de desafíos
- [Category Documentation](categories.md) - Gestión de categorías

