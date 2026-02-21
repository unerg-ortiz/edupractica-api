# Guía de Migración: API Architecture Changes

## Resumen de Cambios

Se ha corregido la arquitectura del backend para seguir el modelo conceptual correcto:

**ANTES (Incorrecto):**
```
Category → Stages
```

**AHORA (Correcto):**
```
Category → Topics → Stages
```

### ¿Por qué este cambio?

El sistema requiere que:
1. **Profesores** crean **Topics** (temas completos con múltiples etapas)
2. **Admins** aprueban **Topics completos** (no etapas individuales)
3. **Estudiantes** acceden a Topics aprobados y completan Stages secuencialmente

Aprobar stages individuales no tenía sentido conceptual - se debe aprobar un tema completo con todas sus etapas.

## Cambios en el Backend

### 1. Schemas Actualizados

#### `StageBase` (stage.py)
```python
# ANTES
category_id: int
approval_status: str = "pending"
approval_comment: Optional[str] = None

# AHORA
topic_id: int
# (approval fields removidos - ahora están en Topic)
```

#### `TopicReview` (topic.py) - NUEVO
```python
class TopicReview(BaseModel):
    approved: bool
    comment: Optional[str] = None
```

### 2. Endpoints Eliminados/Movidos

#### ❌ Eliminados de `stages.py`:
- `GET /categories/{id}/stages` → Ver alternativa abajo
- `GET /categories/{id}/stages/progress` → Reemplazado por `GET /topics/{id}/stages/progress`
- `POST /categories/{id}/initialize` → Auto-inicialización en endpoints de topics
- `GET /review/pending` → Movido a `GET /topics/pending/review`
- `POST /stages/{id}/review` → Reemplazado por `POST /topics/{id}/review`

#### ✅ Nuevos en `topics.py`:
- `GET /categories/{category_id}/topics` - Lista topics aprobados de una categoría
- `GET /topics/{topic_id}/stages/progress` - Stages de un topic con progreso del usuario
- `GET /topics/pending/review` - Topics pendientes (Admin)
- `POST /topics/{topic_id}/review` - Aprobar/rechazar topic (Admin)

### 3. CRUD Functions Actualizadas

#### `crud_stage.py`:
- `get_stages_by_category()` → `get_stages_by_topic()`
- `get_user_progress_by_category()` → `get_user_progress_by_topic()`
- `initialize_user_progress_for_category()` → `initialize_user_progress_for_topic()`
- `get_pending_stages()` → Eliminado (ahora en topics)
- `set_approval_status()` → Eliminado (ahora en topics)

#### `crud_topic.py`:
- `get_topics_by_category()` - Ahora con paginación (skip, limit)
- `get_pending_topics()` - NUEVO
- `set_approval_status()` - NUEVO

## Migración del Frontend

### Servicios que Necesitan Actualización

#### 1. `studentService.ts`

**ANTES:**
```typescript
// ❌ Antiguo - Ya no funciona
async function getCategoryStages(categoryId: number) {
  const response = await apiFetch(`/categories/${categoryId}/stages/progress`);
  return response;
}
```

**AHORA:**
```typescript
// ✅ Nuevo - Flujo correcto

// 1. Obtener topics de la categoría
async function getCategoryTopics(categoryId: number) {
  const response = await apiFetch(`/categories/${categoryId}/topics`);
  return response;
}

// 2. Obtener stages de un topic específico con progreso
async function getTopicStages(topicId: number) {
  const response = await apiFetch(`/topics/${topicId}/stages/progress`);
  return response;
}
```

#### 2. Actualizar Dashboard de Estudiantes

**ANTES:**
```typescript
// ❌ Directo a stages desde category
const stages = await studentService.getCategoryStages(categoryId);
```

**AHORA:**
```typescript
// ✅ Primero topics, luego stages
const topics = await studentService.getCategoryTopics(categoryId);

// Mostrar lista de topics al estudiante
// Al seleccionar un topic:
const stages = await studentService.getTopicStages(selectedTopicId);
```

#### 3. Panel de Admin - Review

**ANTES:**
```typescript
// ❌ Revisar stages individuales
const pendingStages = await apiFetch('/review/pending');

// Aprobar stage individual
await apiFetch(`/stages/${stageId}/review`, {
  method: 'POST',
  body: JSON.stringify({ approved: true, comment: 'OK' })
});
```

**AHORA:**
```typescript
// ✅ Revisar topics completos
const pendingTopics = await apiFetch('/topics/pending/review');

// Cada topic muestra:
// - Título y descripción del topic
// - Lista de stages incluidos (topicWithStages.stages)
// - Información del profesor

// Aprobar topic completo (aprueba todos sus stages)
await apiFetch(`/topics/${topicId}/review`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    approved: true, 
    comment: 'Excelente contenido' 
  })
});
```

#### 4. Panel de Profesor - Crear Contenido

**ANTES:**
```typescript
// ❌ Crear stages directamente
await apiFetch('/stages', {
  method: 'POST',
  body: JSON.stringify({
    category_id: 1,
    order: 1,
    title: 'Etapa 1',
    content: '...'
  })
});
```

**AHORA:**
```typescript
// ✅ Crear topic primero, luego agregar stages

// 1. Crear topic
const topic = await apiFetch('/topics', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: 'Introducción a JavaScript',
    description: 'Aprende JS desde cero',
    category_id: 1
  })
});

// 2. Agregar stages al topic
await apiFetch(`/topics/${topic.id}/stages`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    order: 1,
    title: 'Variables',
    description: 'Aprende sobre variables',
    content: 'Las variables son...',
    challenge_description: 'Crea una variable',
    interactive_config: { ... }
  })
});

// Repetir paso 2 para cada stage del topic
```

### Componentes que Necesitan Cambios

#### 1. `student/dashboard/page.tsx`

**Estructura Antigua:**
```typescript
Categories
  └─ Stages (click → ver stage)
```

**Estructura Nueva:**
```typescript
Categories
  └─ Topics (click → ver topics de categoría)
      └─ Stages (click → ver stages de topic)
```

**Implementación:**
```typescript
// En dashboard
const categories = await getCategories();

// Al click en categoría → mostrar topics
const topics = await getCategoryTopics(categoryId);

// Al click en topic → mostrar stages
const stages = await getTopicStages(topicId);
```

#### 2. `admin/content-review/page.tsx`

**Cambios Necesarios:**
```typescript
// Obtener topics pendientes (no stages)
const pendingTopics = await fetch('/topics/pending/review');

// Mostrar tarjetas de topics con:
// - Título y descripción del topic
// - Nombre del profesor
// - Cantidad de stages incluidos
// - Lista expandible de stages
// - Botones: Aprobar / Rechazar

// Al aprobar/rechazar:
await fetch(`/topics/${topicId}/review`, {
  method: 'POST',
  body: { approved: true/false, comment: '...' }
});
```

#### 3. `professor/topics/` (NUEVO - Crear)

Necesitas crear una interfaz para que profesores:
1. Creen un topic (título, descripción, categoría)
2. Agreguen stages al topic
3. Vean el estado de aprobación de sus topics

**Estructura sugerida:**
```
professor/
  topics/
    page.tsx          # Lista de mis topics con estados
    create/
      page.tsx        # Formulario crear topic
    [id]/
      page.tsx        # Ver/editar topic
      stages/
        create.tsx    # Agregar stage al topic
```

### Rutas de Navegación Actualizadas

**Estudiantes:**
```
/student/dashboard
  → Click categoría
/student/category/[id]        # Muestra topics de la categoría
  → Click topic
/student/topic/[topicId]      # Muestra stages del topic con progreso
  → Click stage desbloqueado
/student/stage/[stageId]      # Contenido y desafío del stage
```

**Profesores:**
```
/professor/topics             # Mis topics y su estado de aprobación
  → Click "Crear Topic"
/professor/topics/create      # Formulario crear topic
  → Después de crear
/professor/topics/[id]        # Ver topic con lista de stages
  → Click "Agregar Stage"
/professor/topics/[id]/stages/create
```

**Admins:**
```
/admin/content-review         # Lista de topics pendientes
  → Click topic para expandir stages
  → Aprobar/Rechazar topic completo
```

## Checklist de Migración

### Backend (✅ Completado)
- [x] Actualizar schemas (stage.py, topic.py)
- [x] Actualizar endpoints (stages.py, topics.py)
- [x] Actualizar CRUDs (crud_stage.py, crud_topic.py)
- [x] Documentar cambios (topics.md, stages.md)

### Frontend (⏳ Pendiente)
- [ ] Actualizar `services/studentService.ts`
  - [ ] Renombrar `getCategoryStages` → `getCategoryTopics`
  - [ ] Crear nuevo `getTopicStages(topicId)`
- [ ] Crear `services/topicService.ts` para profesores
  - [ ] `createTopic()`
  - [ ] `addStageToTopic()`
  - [ ] `getMyTopics()`
- [ ] Crear `services/adminService.ts` para review
  - [ ] `getPendingTopics()`
  - [ ] `reviewTopic()`
- [ ] Actualizar rutas de estudiantes
  - [ ] Crear `/student/category/[id]` - Lista topics
  - [ ] Renombrar `/student/category/[id]` actual a `/student/topic/[id]`
- [ ] Crear panel de profesor
  - [ ] `/professor/topics` - Lista de topics
  - [ ] `/professor/topics/create` - Crear topic
  - [ ] `/professor/topics/[id]` - Ver/editar topic
  - [ ] `/professor/topics/[id]/stages/create` - Agregar stage
- [ ] Actualizar panel de admin
  - [ ] `/admin/content-review` usar `GET /topics/pending/review`
  - [ ] Mostrar stages dentro de cada topic
  - [ ] Aprobar/rechazar topic completo

## Ejemplos de Código Completos

### Ejemplo: Flujo de Estudiante (Componente)

```typescript
// app/[lang]/student/category/[id]/page.tsx
export default function CategoryTopicsPage({ params }: { params: { id: string } }) {
  const [topics, setTopics] = useState([]);
  
  useEffect(() => {
    async function loadTopics() {
      const data = await fetch(`/api/categories/${params.id}/topics`, {
        headers: { 'Authorization': `Bearer ${token}` }
      }).then(r => r.json());
      setTopics(data);
    }
    loadTopics();
  }, [params.id]);
  
  return (
    <div>
      <h1>Topics en esta Categoría</h1>
      {topics.map(topic => (
        <TopicCard 
          key={topic.id} 
          topic={topic}
          onClick={() => router.push(`/student/topic/${topic.id}`)}
        />
      ))}
    </div>
  );
}

// app/[lang]/student/topic/[id]/page.tsx
export default function TopicStagesPage({ params }: { params: { id: string } }) {
  const [stages, setStages] = useState([]);
  
  useEffect(() => {
    async function loadStages() {
      const data = await fetch(`/api/topics/${params.id}/stages/progress`, {
        headers: { 'Authorization': `Bearer ${token}` }
      }).then(r => r.json());
      setStages(data);
    }
    loadStages();
  }, [params.id]);
  
  return (
    <div>
      <h1>Etapas del Topic</h1>
      {stages.map(stage => (
        <StageCard 
          key={stage.id}
          stage={stage}
          isLocked={!stage.is_unlocked}
        />
      ))}
    </div>
  );
}
```

### Ejemplo: Review de Admin

```typescript
// app/[lang]/admin/content-review/page.tsx
export default function ContentReviewPage() {
  const [pendingTopics, setPendingTopics] = useState([]);
  
  useEffect(() => {
    async function loadPending() {
      const data = await fetch('/api/topics/pending/review', {
        headers: { 'Authorization': `Bearer ${token}` }
      }).then(r => r.json());
      setPendingTopics(data);
    }
    loadPending();
  }, []);
  
  async function handleReview(topicId: number, approved: boolean, comment: string) {
    await fetch(`/api/topics/${topicId}/review`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ approved, comment })
    });
    
    // Recargar lista
    setPendingTopics(prev => prev.filter(t => t.id !== topicId));
  }
  
  return (
    <div>
      <h1>Topics Pendientes de Aprobación</h1>
      {pendingTopics.map(topic => (
        <TopicReviewCard
          key={topic.id}
          topic={topic}
          stages={topic.stages}  // TopicWithStages incluye stages
          onApprove={(comment) => handleReview(topic.id, true, comment)}
          onReject={(comment) => handleReview(topic.id, false, comment)}
        />
      ))}
    </div>
  );
}
```

## Preguntas Frecuentes

**Q: ¿Por qué no puedo acceder a `/categories/{id}/stages` anymore?**
A: Los stages ahora pertenecen a topics, no directamente a categorías. Usa `/categories/{id}/topics` para obtener los topics, luego `/topics/{id}/stages/progress` para los stages.

**Q: ¿Dónde quedó la aprobación de stages?**
A: La aprobación ahora es a nivel de topic completo usando `POST /topics/{id}/review`.

**Q: ¿Cómo creo stages ahora?**
A: Primero crea un topic con `POST /topics`, luego agrega stages con `POST /topics/{id}/stages`.

**Q: ¿Qué pasa con los datos existentes?**
A: Necesitarás una migración de base de datos para actualizar `stages.category_id` → `stages.topic_id` y mover campos de aprobación de stages a topics.

**Q: ¿El frontend antiguo dejará de funcionar?**
A: Sí, los endpoints antiguos ya no existen. Debes actualizar el frontend siguiendo esta guía.

## Recursos

- [Topics API Documentation](../docs/topics.md)
- [Stages API Documentation](../docs/stages.md)
- [Architecture Fixes](ARCHITECTURE_FIXES.md)
