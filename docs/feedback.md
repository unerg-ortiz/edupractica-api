# Feedback y Pistas

## POST /api/stages/{stage_id}/feedback

**Descripción:**
Crea un nuevo feedback (pista, corrección o mensaje de ánimo) para una etapa. Solo profesores/Admin.

**Ejemplo de Entrada:**
```json
{
  "stage_id": 5,
  "feedback_type": "hint",
  "sequence_order": 1,
  "max_hints_per_attempt": 3,
  "title": "Revisa los tipos de datos",
  "text_content": "Recuerda que input() devuelve siempre un string.",
  "is_active": true
}
```

**Ejemplo de Respuesta:**
```json
{
  "id": 1,
  "stage_id": 5,
  "feedback_type": "hint",
  "text_content": "Recuerda que input() devuelve siempre un string.",
  "media_url": null,
  "created_at": "2026-02-09T10:00:00"
}
```

## GET /api/stages/{stage_id}/feedback

**Descripción:**
- **Admin/Profesor**: Obtiene todo el feedback configurado para la etapa.
- **Estudiantes**: (Nota: Para estudiantes existe la ruta `/stages/{stage_id}/hints` que gestiona el desbloqueo progresivo, aunque esta ruta base podría retornar lista completa dependiendo de la lógica de negocio actual).

**Ejemplo de Respuesta:**
```json
[
  {
    "id": 1,
    "feedback_type": "hint",
    "title": "Pista 1",
    ...
  },
  {
    "id": 2,
    "feedback_type": "error_correction",
    "title": "Error común",
    ...
  }
]
```

## PUT /api/feedback/{feedback_id}

**Descripción:**
Actualiza un feedback existente.

**Ejemplo de Entrada:**
```json
{
  "text_content": "Texto actualizado de la pista."
}
```

## DELETE /api/feedback/{feedback_id}

**Descripción:**
Elimina un feedback.

## POST /api/feedback/{feedback_id}/media

**Descripción:**
Sube un archivo multimedia (imagen o audio) para un feedback.
Debe enviarse como `multipart/form-data`.

**Ejemplo de Entrada (Form-Data):**
- `file`: (Archivo binario: imagen.png o audio.mp3)
- `media_type`: "image" o "audio"

**Ejemplo de Respuesta:**
```json
{
  "id": 1,
  "media_type": "image",
  "media_url": "uploads/feedback/5/123456_imagen.png",
  ...
}
```

## GET /api/stages/{stage_id}/analytics

**Descripción:**
Obtiene métricas de rendimiento de una etapa (intentos, fallos, tasa de éxito).

**Ejemplo de Respuesta:**
```json
{
  "stage_id": 5,
  "total_attempts": 150,
  "failed_attempts": 45,
  "successful_attempts": 105,
  "success_rate": 70.0,
  "avg_hints_used": 1.5,
  "most_common_errors": []
}
```

## POST /api/stages/{stage_id}/attempts

**Descripción:**
Registra un intento de solución de un estudiante.

**Ejemplo de Entrada:**
```json
{
  "stage_id": 5,
  "is_successful": false,
  "error_details": { "msg": "SyntaxError en línea 3" },
  "time_spent_seconds": 120
}
```

**Ejemplo de Respuesta:**
```json
{
  "id": 101,
  "attempt_number": 1,
  "is_successful": false,
  ...
}
```

## POST /api/attempts/{attempt_id}/view-hint/{feedback_id}

**Descripción:**
Registra que un estudiante ha visto una pista específica. Controla el límite de pistas por intento.

**Ejemplo de Respuesta:**
```json
{
  "id": 50,
  "attempt_id": 101,
  "feedback_id": 1,
  "viewed_at": "2026-02-09T10:05:00"
}
```
