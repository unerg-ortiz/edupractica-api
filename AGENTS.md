# AGENTS.md

## Descripción del Proyecto
EduPractica API es una aplicación basada en FastAPI que utiliza SQLite para el desarrollo. Proporciona recursos de práctica educativa.

## Comandos de Configuración
- Instalar dependencias: `pip install -r requirements.txt`
- Iniciar servidor de desarrollo: `uvicorn app.main:app --reload`
- Verificar estado (health): `curl http://127.0.0.1:8000/health`

## Estructura de Directorios
- `app/`: Lógica principal de la aplicación
  - `api/`: Manejadores de rutas de la API
  - `core/`: Configuración de la aplicación (settings, etc.)
  - `db/`: Conexión a base de datos y gestión de sesiones
  - `models/`: Modelos de base de datos SQLAlchemy
  - `schemas/`: Esquemas Pydantic para validación
- `requirements.txt`: Dependencias del proyecto
- `README.md`: Documentación legible por humanos (en español)
- `AGENTS.md`: Documentación enfocada en agentes

## Stack Tecnológico
- **Framework**: FastAPI
- **Base de Datos**: SQLite (vía SQLAlchemy)
- **Configuración**: Pydantic Settings
- **Servidor**: Uvicorn

## Estilo de Código
- **Idioma**: El código (nombres de variables, funciones, clases y comentarios internos) debe estar estrictamente en **INGLÉS**.
- **Python**: Seguir PEP 8.
- **Type Hints**: Usar sugerencias de tipo (type hints) estándar de Python.
- **Async**: Usar `async def` para los manejadores de rutas.
