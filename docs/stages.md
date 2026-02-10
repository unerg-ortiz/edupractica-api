# Etapas (Stages)

## GET /api/categories/{category_id}/stages

**Descripción:**
Obtiene todas las etapas asociadas a una categoría específica, ordenadas secuencialmente.

**Parámetros:**
- `category_id` (path, int): ID de la categoría.

**Ejemplo de Respuesta:**
```json
[
  {
    "id": 1,
    "category_id": 1,
    "order": 1,
    "title": "Introducción",
    "description": "Conceptos básicos",
    "content": "Contenido educativo...",
    "challenge_description": "Desafío...",
    "is_active": true
  },
  {
    "id": 2,
    "category_id": 1,
    "order": 2,
    "title": "Variables",
    "description": "Tipos de datos",
    "content": "Contenido...",
    "challenge_description": "Desafío...",
    "is_active": true
  }
]
```

## GET /api/categories/{category_id}/stages/progress

**Descripción:**
Obtiene todas las etapas de una categoría junto con el progreso del usuario actual (si están desbloqueadas o completadas). La primera etapa siempre está desbloqueada por defecto.

**Ejemplo de Respuesta:**
```json
[
  {
    "id": 1,
    "category_id": 1,
    "order": 1,
    "title": "Introducción",
    "is_unlocked": true,
    "is_completed": true,
    "content": "...",
    "is_active": true
  },
  {
    "id": 2,
    "category_id": 1,
    "order": 2,
    "title": "Variables",
    "is_unlocked": true,
    "is_completed": false,
    "content": "...",
    "is_active": true
  },
  {
    "id": 3,
    "category_id": 1,
    "order": 3,
    "title": "Bucles",
    "is_unlocked": false,
    "is_completed": false,
    "content": "...",
    "is_active": true
  }
]
```

## GET /api/stages/{stage_id}

**Descripción:**
Obtiene el detalle de una sola etapa.

**Ejemplo de Respuesta:**
```json
{
  "id": 2,
  "category_id": 1,
  "order": 2,
  "title": "Variables",
  "description": "Tipos de datos",
  "content": "...",
  "challenge_description": "...",
  "is_active": true
}
```

## POST /api/stages

**Descripción:**
Crea una nueva etapa. Requiere rol de superusuario (Admin).

**Ejemplo de Entrada:**
```json
{
  "category_id": 1,
  "order": 4,
  "title": "Funciones",
  "description": "Definiendo funciones",
  "content": "Contenido sobre funciones...",
  "challenge_description": "Escribe una función que...",
  "is_active": true
}
```

**Ejemplo de Respuesta:**
```json
{
  "id": 4,
  "category_id": 1,
  "order": 4,
  "title": "Funciones",
  "is_active": true,
  ...
}
```

## PUT /api/stages/{stage_id}

**Descripción:**
Actualiza una etapa existente. Requiere rol de superusuario (Admin).

**Ejemplo de Entrada:**
```json
{
  "title": "Funciones y Scope",
  "is_active": false
}
```

**Ejemplo de Respuesta:**
```json
{
  "id": 4,
  "title": "Funciones y Scope",
  "is_active": false,
  ...
}
```

## DELETE /api/stages/{stage_id}

**Descripción:**
Elimina una etapa (soft delete). Requiere rol de superusuario (Admin).

**Respuesta:**
Status 204 No Content

## POST /api/stages/{stage_id}/complete

**Descripción:**
Marca una etapa como completada para el usuario actual y desbloquea automáticamente la siguiente etapa en la secuencia.
Requisitos:
- La etapa actual debe estar desbloqueada.
- El usuario debe haber completado el desafío (validación implícita o previa).

**Ejemplo de Respuesta:**
```json
{
  "id": 15,
  "user_id": 5,
  "stage_id": 2,
  "is_completed": true,
  "is_unlocked": true
}
```
