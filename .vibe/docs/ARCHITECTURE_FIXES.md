# Correcciones de Arquitectura - EduPractica

## 📊 Análisis del Problema

### Estructura Incorrecta Actual:
```
Category ←→ Stage (con approval_status)
```

### Estructura Correcta Requerida:
```
Category → Topic (con approval_status) → Stage → Quiz/Reto (interactive_config)
```

## 🔴 Problemas Identificados

### 1. **Inconsistencia en Relaciones**
- ❌ `Stage.topic_id` existe en modelo pero no se usa
- ❌ Schemas usan `category_id` en vez de `topic_id`
- ❌ Endpoints trabajan con `categories/{id}/stages` en vez de `topics/{id}/stages`
- ❌ CRUDs probablemente también

tienen esta inconsistencia

### 2. **Sistema de Aprobación**
- ✅ `Topic` tiene `approval_status` (correcto)
- ❌ `Stage` schema tiene `approval_status` (duplicado e innecesario)
- ❌ Endpoints de review operan sobre stages individuales (debería ser sobre topics)

### 3. **Gestión de Categorías**
- ✅ Categories tienen `unique=True`
- ❌ No hay endpoint para que profesores creen categorías
- ❌ No hay validación de unicidad en el frontend

### 4. **Flujo de Trabajo Incorrecto**
**Actual:**
1. Profesor crea Stage → Admin aprueba Stage

**Correcto:**
1. Profesor crea Topic con múltiples Stages
2. Admin aprueba/rechaza el Topic completo
3. Si aprobado, todos los stages del topic son visibles para estudiantes
4. Estudiante progresa secuencialmente por los stages

## 🔧 Correcciones Necesarias

### Backend:

1. **Schemas** (`app/schemas/stage.py`):
   - Cambiar `category_id` → `topic_id`
   - Eliminar `approval_status` de Stage (solo Topic lo tiene)
   - Eliminar `professor_id` duplicado de Stage

2. **Endpoints** (`app/api/endpoints/stages.py`):
   - Cambiar `/categories/{id}/stages` → `/topics/{id}/stages`
   - Mover endpoints de review a topics.py
   - Ajustar lógica de visibilidad (usar approval_status del Topic)

3. **Endpoints** (`app/api/endpoints/topics.py`):
   - Añadir endpoint para listar topics aprobados (estudiantes)
   - Añadir endpoints de review (admin)
   - Añadir endpoint para topics por categoría

4. **CRUDs** (`app/crud/crud_stage.py`):
   - Revisar funciones que usan category_id
   - Actualizar queries para usar topic_id
   - Filtrar por approval_status del topic padre

5. **Endpoints de Categorías** (`app/api/endpoints/categories.py`):
   - Añadir endpoint POST para profesores (con validación de unicidad)

### Frontend:

1. **Servicios** (`services/studentService.ts`):
   - Cambiar de categories a topics
   - Obtener topics aprobados por categoría
   - Obtener stages por topic

2. **Dashboard Estudiante**:
   - Mostrar categorías con topics aprobados
   - Al clickear mostrar topics de esa categoría
   - Al clickear topic, mostrar sus stages

3. **Panel Profesor**:
   - Cambiar de "Contenido" a "Mis Temas"
   - Formulario para crear Topic con múltiples Stages
   - Mostrar status de aprobación por Topic

4. **Panel Admin**:
   - Revisar Topics completos (no stages individuales)
   - Mostrar preview de todos los stages del topic
   - Aprobar/Rechazar topic completo

## 📋 Plan de Implementación

### Fase 1: Backend Core ✓
- [ ] Corregir schemas de Stage
- [ ] Actualizar endpoints de stages
- [ ] Mover lógica de review a topics
- [ ] Actualizar CRUDs

### Fase 2: Backend Categorías
- [ ] Añadir endpoint para crear categorías (profesor)
- [ ] Validación de unicidad

### Fase 3: Frontend Estudiante
- [ ] Actualizar servicios
- [ ] Corregir flujo de navegación
- [ ] Categoria → Topics → Stages

### Fase 4: Frontend Profesor
- [ ] Interfaz para crear Topic completo
- [ ] Gestión de stages dentro del topic
- [ ] Configuración de quizzes/retos

### Fase 5: Frontend Admin
- [ ] Panel de revisión de Topics
- [ ] Preview de stages
- [ ] Aprobación/Rechazo con comentarios

## 🎯 Estructura Final

```
┌─────────────┐
│  Category   │ (Matemáticas, Ciencias)
│  - Admin    │
│  - Profesor*│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Topic    │ (Álgebra Lineal)
│  - Profesor │ ← approval_status
│  - pending  │   (pending/approved/rejected)
│  - approved │
│  - rejected │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Stage    │ (Etapa 1: Vectores)
│  - Orden    │
│  - Secuencial│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Quiz/Reto   │ (interactive_config)
│  - Drag&Drop│
│  - Matching │
│  - MCQ      │
└─────────────┘
```

## ✅ Criterios de Éxito

1. Profesor puede crear un Topic con múltiples Stages
2. Admin ve Topics completos para aprobar (no stages individuales)
3. Una vez aprobado el Topic, todos sus stages son visibles para estudiantes
4. Estudiante navega: Categoría → Topics → Stages (secuencial)
5. Estudiante debe completar quiz/reto de stage N para acceder a stage N+1
6. Categorías son únicas y pueden ser creadas por admin o profesor

