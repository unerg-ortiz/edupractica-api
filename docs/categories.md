# Categorías (Categories)

## GET /categories/

**Descripción:**
Obtiene una lista de categorías disponibles.

**Parámetros:**
- `skip` (query, int): Número de registros a saltar.
- `limit` (query, int): Número de registros a retornar.
- `q` (query, str): Filtro opcional por nombre (búsqueda).

**Ejemplo de Respuesta:**
```json
[
  {
    "id": 1,
    "name": "Python Básico",
    "description": "Introducción a la programación con Python",
    "icon": "🐍"
  },
  {
    "id": 2,
    "name": "Algoritmos",
    "description": "Estructuras de datos y algoritmos",
    "icon": "📐"
  }
]
```

## POST /categories/

**Descripción:**
Crea una nueva categoría. Requiere rol de superusuario.

**Ejemplo de Entrada:**
```json
{
  "name": "Ciencia de Datos",
  "description": "Análisis de datos con Pandas y NumPy",
  "icon": "📊"
}
```

**Ejemplo de Respuesta:**
```json
{
  "id": 3,
  "name": "Ciencia de Datos",
  "description": "Análisis de datos con Pandas y NumPy",
  "icon": "📊"
}
```

## GET /categories/{category_id}

**Descripción:**
Obtiene los detalles de una categoría específica por su ID.

**Ejemplo de Respuesta:**
```json
{
  "id": 3,
  "name": "Ciencia de Datos",
  "description": "Análisis de datos con Pandas y NumPy",
  "icon": "📊"
}
```

## PUT /categories/{category_id}

**Descripción:**
Actualiza los detalles de una categoría existente. Requiere rol de superusuario.

**Ejemplo de Entrada:**
```json
{
  "name": "Data Science Avanzado"
}
```

**Ejemplo de Respuesta:**
```json
{
  "id": 3,
  "name": "Data Science Avanzado",
  "description": "Análisis de datos con Pandas y NumPy",
  "icon": "📊"
}
```

## DELETE /categories/{category_id}

**Descripción:**
Elimina una categoría del sistema. Requiere rol de superusuario.

**Ejemplo de Respuesta:**
```json
{
  "id": 3,
  "name": "Data Science Avanzado",
  "description": "Análisis de datos con Pandas y NumPy",
  "icon": "📊"
}
```

## POST /categories/{category_id}/initialize

**Descripción:**
Inicializa el progreso del usuario para todas las etapas de una categoría. Desbloquea la primera etapa y bloquea las demás.

**Ejemplo de Respuesta:**
```json
[
  {
    "id": 10,
    "user_id": 5,
    "stage_id": 1,
    "is_completed": false,
    "is_unlocked": true
  },
  {
    "id": 11,
    "user_id": 5,
    "stage_id": 2,
    "is_completed": false,
    "is_unlocked": false
  }
]
```
