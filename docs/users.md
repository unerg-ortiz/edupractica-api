# Usuarios

## GET /users/

**Descripción:**
Obtiene una lista de usuarios registrados. Requiere rol de superusuario.

**Parámetros:**
- `skip` (query, int): Número de registros a saltar (default: 0).
- `limit` (query, int): Número máximo de registros a retornar (default: 100).

**Ejemplo de Respuesta:**
```json
[
  {
    "email": "admin@example.com",
    "is_active": true,
    "is_superuser": true,
    "full_name": "Admin User",
    "id": 1,
    "is_blocked": false,
    "block_reason": null
  },
  {
    "email": "student@example.com",
    "is_active": true,
    "is_superuser": false,
    "full_name": "Student User",
    "id": 2,
    "is_blocked": false,
    "block_reason": null
  }
]
```

## POST /users/

**Descripción:**
Crea un nuevo usuario. Requiere rol de superusuario.

**Ejemplo de Entrada:**
```json
{
  "email": "nuevo@ejemplo.com",
  "password": "securepassword123",
  "full_name": "Nuevo Usuario",
  "is_superuser": false,
  "is_active": true
}
```

**Ejemplo de Respuesta:**
```json
{
  "email": "nuevo@ejemplo.com",
  "is_active": true,
  "is_superuser": false,
  "full_name": "Nuevo Usuario",
  "id": 3,
  "is_blocked": false,
  "block_reason": null
}
```

## POST /users/{user_id}/block

**Descripción:**
Bloquea a un usuario específico, impidiendo su acceso. Requiere rol de superusuario.

**Ejemplo de Entrada:**
```json
{
  "reason": "Comportamiento inapropiado en los foros"
}
```

**Ejemplo de Respuesta:**
```json
{
  "email": "student@example.com",
  "is_active": true,
  "is_superuser": false,
  "full_name": "Student User",
  "id": 2,
  "is_blocked": true,
  "block_reason": "Comportamiento inapropiado en los foros"
}
```

## DELETE /users/{user_id}

**Descripción:**
Elimina un usuario del sistema por su ID. Requiere rol de superusuario. Un superusuario no puede eliminarse a sí mismo mediante este endpoint.

## DELETE /users/me

**Descripción:**
Permite que el usuario autenticado elimine su propia cuenta y toda su información personal asociada (intentos de etapas, registros de auditoría y perfil), cumpliendo con las normativas de privacidad (GDPR).

**Ejemplo de Respuesta:**
```json
{
  "email": "mi-correo@ejemplo.com",
  "is_active": true,
  "is_superuser": false,
  "full_name": "Mi Nombre",
  "id": 5,
  "is_blocked": false,
  "block_reason": null
}
```
