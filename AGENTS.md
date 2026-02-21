# AGENTS.md

## Descripción del Proyecto
EduPractica API es una aplicación basada en FastAPI que utiliza SQLite para el desarrollo. Proporciona recursos de práctica educativa.

## Ubicación de Archivos Generados por IA
> [!NOTE]
> Para mantener limpio el código fuente, sigue estas reglas estrictas para archivos generados por IA:

- **Pruebas y Tests**: Todo código generado únicamente para pruebas debe ir en `.vibe/tests/`. Si el directorio no existe, CRÉALO.
- **Documentación**: Documentos, notas o explicaciones extendidas generadas van en `.vibe/docs/`.
- **Otros**: Cualquier archivo que no sea parte del producto final debe ubicarse dentro de `.vibe/`.
- **Excepción**: Los archivos de implementación real (features, bugfixes) sí van en su estructura correspondiente (`app/`, `components/`, etc).

## Comandos de Configuración
- Instalar dependencias: `pip install -r requirements.txt`
- Iniciar servidor de desarrollo: `uvicorn app.main:app --reload` o `poe dev`
- Verificar estado (health): `curl http://127.0.0.1:8000/health`
- **Inicializar/Migrar base de datos**: `poe init-db`

## Migraciones de Base de Datos
> [!IMPORTANT]
> Este proyecto NO utiliza scripts temporales de migración. Las migraciones permanentes se manejan en `init_db.py`.

**Proceso correcto para agregar/modificar columnas:**

1. **Actualizar el modelo** en `app/models/`:
   ```python
   # Ejemplo: app/models/stage.py
   new_column = Column(String, nullable=True)
   ```

2. **Actualizar el schema** en `app/schemas/`:
   ```python
   # Ejemplo: app/schemas/stage.py
   new_column: Optional[str] = None
   ```

3. **Agregar migración** en `init_db.py` dentro del array `migrations`:
   ```python
   {
       "table": "stages",
       "column": "new_column",
       "sql": "ALTER TABLE stages ADD COLUMN new_column TEXT",
   },
   ```

4. **Ejecutar migración**: `poe init-db`

**❌ NO CREAR:**
- Scripts como `add_column_x.py`, `fix_migration.py`, etc.
- Estos son parches temporales y no son mantenibles

**✅ USAR:**
- `init_db.py` para todas las migraciones
- Considerar Alembic para proyectos más grandes en el futuro

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
- La Respuesta de la IA SIEMPRE debe ir en español.
- Cada vez que se cree un nuevo endpoint se debe documentar en `docs/` y debes incluir en la documentación el propósito del endpoint, los datos que espera y los datos o respuesta que retorna, junto con un ejemplo de uso.