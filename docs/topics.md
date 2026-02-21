# Topics API Documentation

## Descripción
Los Topics (Temas) son colecciones de Stages (Etapas) creadas por profesores y aprobadas por administradores. Un Topic pertenece a una Categoría y contiene múltiples Stages secuenciales.

## Flujo de Trabajo
1. **Profesor** crea un Topic con sus Stages
2. Topic queda en estado `pending`
3. **Admin** revisa y aprueba/rechaza el Topic completo
4. Si se aprueba, **todos** los Stages del Topic se vuelven visibles para estudiantes
5. **Estudiantes** acceden a Topics aprobados y completan Stages secuencialmente

## Estructura de Datos

### Topic
```json
{
  "id": 1,
  "title": "Introducción a JavaScript",
  "description": "Aprende los fundamentos de JavaScript desde cero",
  "category_id": 2,
  "professor_id": 5,
  "approval_status": "approved",
  "approval_comment": null,
  "submitted_at": "2024-01-15T10:30:00Z",
  "is_active": true
}
```

### TopicReview (Para Admin)
```json
{
  "approved": true,
  "comment": "Excelente contenido, aprobado"
}
```

## Endpoints

### 1. Listar Mis Topics (Profesor)
**GET** `/topics/me`

Obtiene todos los topics creados por el profesor actual.

**Autenticación:** Requiere rol `professor`

**Query Parameters:**
- `skip` (int, opcional): Número de registros a omitir (default: 0)
- `limit` (int, opcional): Máximo de registros a retornar (default: 100)

**Respuesta 200:**
```json
[
  {
    "id": 1,
    "title": "Introducción a JavaScript",
    "description": "Aprende los fundamentos...",
    "category_id": 2,
    "professor_id": 5,
    "approval_status": "pending",
    "approval_comment": null,
    "submitted_at": "2024-01-15T10:30:00Z",
    "is_active": true
  }
]
```

**Ejemplo:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/topics/me?skip=0&limit=10"
```

---

### 2. Crear Topic (Profesor)
**POST** `/topics`

Crea un nuevo topic. El topic se crea con estado `pending` y debe ser aprobado por un admin antes de ser visible para estudiantes.

**Autenticación:** Requiere rol `professor`

**Request Body:**
```json
{
  "title": "Introducción a Python",
  "description": "Aprende Python desde cero con ejercicios prácticos",
  "category_id": 1
}
```

**Respuesta 200:**
```json
{
  "id": 10,
  "title": "Introducción a Python",
  "description": "Aprende Python desde cero...",
  "category_id": 1,
  "professor_id": 5,
  "approval_status": "pending",
  "approval_comment": null,
  "submitted_at": "2024-01-20T14:25:00Z",
  "is_active": true
}
```

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/topics" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Introducción a Python",
    "description": "Aprende Python desde cero",
    "category_id": 1
  }'
```

---

### 3. Obtener Topic Específico
**GET** `/topics/{topic_id}`

Obtiene un topic específico con todos sus stages.

**Autenticación:** Requiere autenticación

**Permisos:**
- **Estudiantes:** Solo pueden ver topics con `approval_status = "approved"`
- **Profesores:** Pueden ver sus propios topics (cualquier estado)
- **Admins:** Pueden ver todos los topics

**Path Parameters:**
- `topic_id` (int, requerido): ID del topic

**Respuesta 200:**
```json
{
  "id": 1,
  "title": "Introducción a JavaScript",
  "description": "Aprende los fundamentos...",
  "category_id": 2,
  "professor_id": 5,
  "approval_status": "approved",
  "approval_comment": null,
  "submitted_at": "2024-01-15T10:30:00Z",
  "is_active": true,
  "stages": [
    {
      "id": 101,
      "topic_id": 1,
      "order": 1,
      "title": "Variables y Tipos de Datos",
      "description": "Aprende sobre variables...",
      "content": "En JavaScript, las variables...",
      "is_active": true
    },
    {
      "id": 102,
      "topic_id": 1,
      "order": 2,
      "title": "Operadores",
      "description": "Operadores aritméticos...",
      "content": "Los operadores permiten...",
      "is_active": true
    }
  ]
}
```

**Respuesta 404:**
```json
{
  "detail": "Topic not found"
}
```

**Ejemplo:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/topics/1"
```

---

### 4. Actualizar Topic (Profesor)
**PUT** `/topics/{topic_id}`

Actualiza un topic existente. Solo el profesor propietario o un admin pueden actualizar.

**Autenticación:** Requiere rol `professor`

**Path Parameters:**
- `topic_id` (int, requerido): ID del topic

**Request Body:**
```json
{
  "title": "Introducción a JavaScript (Actualizado)",
  "description": "Nueva descripción más detallada"
}
```

**Respuesta 200:**
```json
{
  "id": 1,
  "title": "Introducción a JavaScript (Actualizado)",
  "description": "Nueva descripción más detallada",
  "category_id": 2,
  "professor_id": 5,
  "approval_status": "approved",
  "is_active": true
}
```

**Respuesta 403:**
```json
{
  "detail": "Not authorized"
}
```

---

### 5. Agregar Stage a Topic (Profesor)
**POST** `/topics/{topic_id}/stages`

Agrega una nueva stage (etapa) a un topic existente.

**⚠️ IMPORTANTE:** No incluyas `category_id` en el payload. Los stages heredan la categoría del topic al que pertenecen.

**Autenticación:** Requiere rol `professor`

**Path Parameters:**
- `topic_id` (int, requerido): ID del topic

**Request Body:**
```json
{
  "order": 3,
  "title": "Funciones en JavaScript",
  "description": "Aprende a crear y usar funciones",
  "content": "Las funciones son bloques de código reutilizables...",
  "challenge_description": "Crea una función que calcule el factorial",
  "media_type": "video",
  "media_url": "/uploads/stages/video123.mp4",
  "media_filename": "funciones-intro.mp4",
  "interactive_config": {
    "type": "drag_and_drop",
    "items": [
      {"id": "1", "text": "function", "correct_zone": "zone1"},
      {"id": "2", "text": "return", "correct_zone": "zone2"}
    ]
  }
}
```

**Respuesta 200:**
```json
{
  "id": 150,
  "topic_id": 1,
  "order": 3,
  "title": "Funciones en JavaScript",
  "description": "Aprende a crear y usar funciones",
  "content": "Las funciones son bloques...",
  "is_active": true,
  "professor_id": 5
}
```

---

### 6. Listar Topics Aprobados por Categoría (Estudiantes/Todos)
**GET** `/categories/{category_id}/topics`

Obtiene todos los topics de una categoría. Los estudiantes solo ven topics aprobados.

**Autenticación:** Requiere autenticación

**Path Parameters:**
- `category_id` (int, requerido): ID de la categoría

**Query Parameters:**
- `skip` (int, opcional): Número de registros a omitir (default: 0)
- `limit` (int, opcional): Máximo de registros a retornar (default: 100)

**Respuesta 200:**
```json
[
  {
    "id": 1,
    "title": "Introducción a JavaScript",
    "description": "Aprende los fundamentos...",
    "category_id": 2,
    "professor_id": 5,
    "approval_status": "approved",
    "is_active": true
  },
  {
    "id": 3,
    "title": "JavaScript Avanzado",
    "description": "Conceptos avanzados de JS...",
    "category_id": 2,
    "professor_id": 7,
    "approval_status": "approved",
    "is_active": true
  }
]
```

**Ejemplo:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/categories/2/topics"
```

---

### 7. Obtener Stages de un Topic con Progreso (Estudiantes)
**GET** `/topics/{topic_id}/stages/progress`

Obtiene todos los stages de un topic con información de progreso del usuario actual.

**Autenticación:** Requiere autenticación

**Path Parameters:**
- `topic_id` (int, requerido): ID del topic

**Comportamiento:**
- Inicializa progreso automáticamente si es la primera vez que el usuario accede
- Primera stage siempre desbloqueada (`is_unlocked: true`)
- Stages subsecuentes bloqueadas hasta completar la anterior
- Solo muestra topics con `approval_status = "approved"` para estudiantes

**Respuesta 200:**
```json
[
  {
    "id": 101,
    "topic_id": 1,
    "order": 1,
    "title": "Variables y Tipos de Datos",
    "description": "Aprende sobre variables...",
    "content": "En JavaScript, las variables...",
    "is_unlocked": true,
    "is_completed": true,
    "is_active": true
  },
  {
    "id": 102,
    "topic_id": 1,
    "order": 2,
    "title": "Operadores",
    "description": "Operadores aritméticos...",
    "content": "Los operadores permiten...",
    "is_unlocked": true,
    "is_completed": false,
    "is_active": true
  },
  {
    "id": 103,
    "topic_id": 1,
    "order": 3,
    "title": "Funciones",
    "description": "Funciones en JavaScript...",
    "content": "Las funciones son...",
    "is_unlocked": false,
    "is_completed": false,
    "is_active": true
  }
]
```

**Ejemplo:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/topics/1/stages/progress"
```

---

### 8. Listar Topics Pendientes de Aprobación (Admin)
**GET** `/topics/pending/review`

Lista todos los topics que están esperando aprobación.

**Autenticación:** Requiere rol `admin`

**Query Parameters:**
- `skip` (int, opcional): Número de registros a omitir (default: 0)
- `limit` (int, opcional): Máximo de registros a retornar (default: 100)

**Respuesta 200:**
```json
[
  {
    "id": 10,
    "title": "Introducción a Python",
    "description": "Aprende Python desde cero...",
    "category_id": 1,
    "professor_id": 5,
    "approval_status": "pending",
    "approval_comment": null,
    "submitted_at": "2024-01-20T14:25:00Z",
    "is_active": true,
    "stages": [
      {
        "id": 200,
        "topic_id": 10,
        "order": 1,
        "title": "Instalación de Python",
        "is_active": true
      },
      {
        "id": 201,
        "topic_id": 10,
        "order": 2,
        "title": "Variables en Python",
        "is_active": true
      }
    ]
  }
]
```

**Ejemplo:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/topics/pending/review"
```

---

### 9. Aprobar/Rechazar Topic (Admin)
**POST** `/topics/{topic_id}/review`

Aprueba o rechaza un topic. Cuando se aprueba, todos los stages del topic se vuelven visibles para estudiantes.

**Autenticación:** Requiere rol `admin`

**Path Parameters:**
- `topic_id` (int, requerido): ID del topic a revisar

**Request Body:**
```json
{
  "approved": true,
  "comment": "Excelente contenido educativo, aprobado"
}
```

O para rechazar:
```json
{
  "approved": false,
  "comment": "El contenido necesita más ejemplos prácticos"
}
```

**Respuesta 200:**
```json
{
  "id": 10,
  "title": "Introducción a Python",
  "description": "Aprende Python desde cero...",
  "category_id": 1,
  "professor_id": 5,
  "approval_status": "approved",
  "approval_comment": "Excelente contenido educativo, aprobado",
  "submitted_at": "2024-01-20T14:25:00Z",
  "is_active": true
}
```

**Respuesta 404:**
```json
{
  "detail": "Topic not found"
}
```

**Ejemplo (Aprobar):**
```bash
curl -X POST "http://localhost:8000/topics/10/review" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "comment": "Contenido aprobado"
  }'
```

**Ejemplo (Rechazar):**
```bash
curl -X POST "http://localhost:8000/topics/10/review" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "approved": false,
    "comment": "Necesita más ejemplos"
  }'
```

---

## Estados de Aprobación

| Estado | Descripción |
|--------|-------------|
| `pending` | Topic recién creado, esperando revisión del admin |
| `approved` | Topic aprobado, visible para estudiantes |
| `rejected` | Topic rechazado, incluye comentarios de feedback |

## Notas Importantes

1. **Aprobación a Nivel de Topic:** La revisión se hace sobre el topic completo (con todos sus stages), no sobre stages individuales.

2. **Visibilidad para Estudiantes:** Los estudiantes solo pueden ver topics con `approval_status = "approved"`.

3. **Progreso del Usuario:** El progreso se inicializa automáticamente la primera vez que un estudiante accede a un topic.

4. **Secuencialidad:** Los stages deben completarse en orden. Solo el primer stage está desbloqueado inicialmente.

5. **Permisos:**
   - **Profesores:** Pueden crear topics y agregar stages
   - **Admins:** Pueden aprobar/rechazar topics y ver todos los topics
   - **Estudiantes:** Solo ven topics aprobados y completan stages secuencialmente

## Migración desde Category-Based Architecture

Si estabas usando endpoints antiguos:
- ❌ `GET /categories/{id}/stages` → ✅ `GET /categories/{id}/topics` + `GET /topics/{id}/stages/progress`
- ❌ `GET /categories/{id}/stages/progress` → ✅ `GET /topics/{id}/stages/progress`
- ❌ `POST /stages/{id}/review` → ✅ `POST /topics/{id}/review`
- ❌ `GET /review/pending` (stages) → ✅ `GET /topics/pending/review`
