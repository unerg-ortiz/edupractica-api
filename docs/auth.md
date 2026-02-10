# Autenticación

## POST /login/access-token

**Descripción:**
Obtiene un token de acceso OAuth2 para futuras peticiones. Se utiliza para iniciar sesión en la aplicación mediante correo y contraseña.

**Ejemplo de Entrada (Form-urlencoded):**
```
username: user@example.com
password: password123
```

**Ejemplo de Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
  "token_type": "bearer"
}
```

## GET /auth/google/login

**Descripción:**
Redirige al usuario a la página de inicio de sesión de Google.

## GET /auth/microsoft/login

**Descripción:**
Redirige al usuario a la página de inicio de sesión de Microsoft.

## Flujo OAuth

1. El frontend redirige al usuario a `/auth/google/login` o `/auth/microsoft/login`.
2. El usuario autoriza la aplicación en Google/Microsoft.
3. El proveedor redirige de vuelta a `/auth/google/callback` o `/auth/microsoft/callback`.
4. La API verifica los datos, registra al usuario si es nuevo (vía email) y redirige al frontend con un token en la URL: `FRONTEND_URL/login/success?token=...`.
5. El frontend extrae el token y lo guarda en el local storage.
