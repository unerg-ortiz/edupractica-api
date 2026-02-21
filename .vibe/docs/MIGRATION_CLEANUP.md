# Scripts de Migración - Limpieza Recomendada

## Scripts Temporales Detectados

Los siguientes scripts en la raíz del proyecto parecen ser parches temporales de migración:

### Scripts de Migración Temporal
- `fix_migration.py`
- `fix_migration_v2.py`
- `migrate_add_role.py`
- `sync_professor_field.py`
- `update_db.py`

### Scripts de Debug/Utilidades
- `check_professors.py`
- `check_sa.py`
- `list_cols.py`
- `list_cols_v2.py`
- `debug_db.py`
- `debug_schema.py`
- `test_pending.py`
- `test_ser.py`

### Scripts de Seeding/Población
- `create_test_students.py`
- `populate_analytics.py`
- `populate_stages.py`
- `update_user_to_professor.py`

### Scripts Legítimos (Mantener)
- `init_db.py` - ✅ Sistema oficial de migraciones y seeding
- `export_openapi.py` - ✅ Exportar especificación API
- `list_all_users.py` - ⚠️ Evaluar si es necesario

## Recomendaciones

### Acción Inmediata
1. **Consolidar lógica de seeding** en `init_db.py`
2. **Mover scripts de debug** a `.vibe/tests/` o `.vibe/utils/`
3. **Eliminar scripts obsoletos** de migración temporal

### Estructura Propuesta
```
edupractica-api/
├── init_db.py              # ✅ Único script de migración/seeding
├── export_openapi.py       # ✅ Utilidad de exportación
├── app/                    # ✅ Código de aplicación
└── .vibe/
    ├── utils/              # Scripts de utilidad (debug, check)
    └── tests/              # Scripts de testing
```

### Migración Futura: Alembic

Para un sistema de migraciones más robusto, considerar implementar Alembic:

```bash
# Instalación
pip install alembic

# Inicialización
alembic init alembic

# Crear migración
alembic revision --autogenerate -m "Add challenge_description"

# Aplicar migraciones
alembic upgrade head
```

#### Ventajas de Alembic
- ✅ Migraciones versionadas
- ✅ Rollback automático
- ✅ Detección automática de cambios
- ✅ Soporte multi-base de datos
- ✅ Historial de migraciones

#### Cuándo Migrar a Alembic
- Cuando el proyecto crezca significativamente
- Cuando necesites revertir migraciones
- Cuando trabajes en equipo con múltiples desarrolladores
- Cuando muevas a producción con múltiples entornos

## Proceso de Limpieza

### Paso 1: Mover Scripts de Debug
```bash
mkdir -p .vibe/utils
mv check_*.py list_*.py debug_*.py test_*.py .vibe/utils/
```

### Paso 2: Consolidar Seeding
Revisar scripts como `create_test_students.py` y `populate_*.py` para integrar su lógica en `init_db.py`.

### Paso 3: Eliminar Scripts Obsoletos
Una vez verificado que `init_db.py` tiene toda la funcionalidad:
```bash
rm fix_migration*.py migrate_add_role.py sync_professor_field.py update_db.py
```

### Paso 4: Actualizar Documentación
Actualizar `README.md` y `AGENTS.md` para reflejar el proceso limpio de migraciones.

---

**Fecha:** 2026-02-21  
**Estado:** Propuesta pendiente de revisión
