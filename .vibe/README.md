# .vibe/ - Scripts de Desarrollo

Este directorio contiene scripts auxiliares que no forman parte del código de producción.

## 📂 Estructura

### `/utils/` - Utilidades y Debug
Scripts para verificar y debuggear el estado de la base de datos:

- `check_professors.py` - Verificar profesores en la BD
- `check_sa.py` - Verificar superadministradores
- `debug_db.py` - Herramientas de debug de BD
- `debug_schema.py` - Verificar esquema de BD
- `list_all_users.py` - Listar todos los usuarios
- `list_cols.py` / `list_cols_v2.py` - Listar columnas de tablas

**Uso:**
```bash
python .vibe/utils/check_professors.py
python .vibe/utils/list_all_users.py
```

### `/tests/` - Scripts de Testing y Seeding
Scripts para popular la base de datos con datos de prueba:

- `create_test_students.py` - Crear estudiantes de prueba
- `populate_analytics.py` - Popular datos de analytics
- `populate_stages.py` - Popular stages de ejemplo
- `test_pending.py` - Testing de funcionalidad pending
- `test_ser.py` - Testing de serialización

**Uso:**
```bash
python .vibe/tests/create_test_students.py
python .vibe/tests/populate_stages.py
```

### `/docs/` - Documentación Interna
Documentación técnica y propuestas de mejora:

- `MIGRATION_CLEANUP.md` - Plan de limpieza de migraciones

## ⚠️ Importante

**NO** utilices estos scripts en producción. Están pensados únicamente para desarrollo y testing local.

## 🔧 Scripts de Producción

Los únicos scripts que deben ejecutarse en producción están en la raíz:

- `init_db.py` - Sistema oficial de migraciones y seeding
- `export_openapi.py` - Exportar especificación OpenAPI

**Uso en producción:**
```bash
poe init-db  # Migrar y seed de BD
```

## 📝 Agregar Nuevos Scripts

Al crear nuevos scripts auxiliares:

1. **Debug/Utilidades** → Agregar a `.vibe/utils/`
2. **Testing/Seeding** → Agregar a `.vibe/tests/`
3. **Documentación** → Agregar a `.vibe/docs/`
4. **NUNCA** crear scripts de migración temporal en la raíz

Para migraciones permanentes, usar siempre `init_db.py`:
```python
# En init_db.py, agregar a migrations[]
{
    "table": "nombre_tabla",
    "column": "nueva_columna",
    "sql": "ALTER TABLE nombre_tabla ADD COLUMN nueva_columna TEXT",
}
```

## 🧹 Limpieza Realizada

### Eliminados (2026-02-21)
Scripts temporales de migración que fueron consolidados en `init_db.py`:
- ❌ `fix_migration.py`
- ❌ `fix_migration_v2.py`
- ❌ `migrate_add_role.py`
- ❌ `sync_professor_field.py`
- ❌ `update_db.py`
- ❌ `update_user_to_professor.py`
- ❌ `add_challenge_description.py`

Estos scripts aplicaban parches temporales. Su funcionalidad fue integrada permanentemente en `init_db.py`.
