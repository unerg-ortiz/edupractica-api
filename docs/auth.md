# Autenticación

## POST /login/access-token

**Descripción:**
Obtiene un token de acceso OAuth2 para futuras peticiones. Se utiliza para iniciar sesión en la aplicación.

**Ejemplo de Entrada (Form-urlencoded):**
```
username: admin@example.com
password: admin123
```

**Ejemplo de Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
  "token_type": "bearer"
}
```
