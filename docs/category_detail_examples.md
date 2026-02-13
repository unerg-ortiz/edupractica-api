# Ejemplo de Uso: Detalle de Categoría

## Endpoint Principal
**GET** `/categories/{category_id}/detail`

---

## Ejemplo 1: Categoría con Etapas y Estudiantes

### Request
```http
GET /categories/1/detail HTTP/1.1
Host: api.edupractica.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response (200 OK)
```json
{
  "id": 1,
  "name": "Python Básico",
  "description": "Introducción a la programación con Python desde cero. Aprenderás los fundamentos necesarios para comenzar tu carrera como desarrollador.",
  "icon": "🐍",
  "stages": [
    {
      "id": 1,
      "order": 1,
      "title": "Instalación y Configuración",
      "description": "Aprende a instalar Python y configurar tu entorno de desarrollo",
      "is_active": true,
      "media_type": "video"
    },
    {
      "id": 2,
      "order": 2,
      "title": "Variables y Tipos de Datos",
      "description": "Conceptos básicos de variables, números, strings y booleanos",
      "is_active": true,
      "media_type": "image"
    },
    {
      "id": 3,
      "order": 3,
      "title": "Estructuras de Control",
      "description": "Aprende a usar if, else, elif y loops",
      "is_active": true,
      "media_type": "audio"
    },
    {
      "id": 4,
      "order": 4,
      "title": "Funciones",
      "description": "Crea y utiliza funciones para organizar tu código",
      "is_active": true,
      "media_type": null
    },
    {
      "id": 5,
      "order": 5,
      "title": "Listas y Diccionarios",
      "description": "Estructuras de datos fundamentales en Python",
      "is_active": true,
      "media_type": "video"
    }
  ],
  "metrics": {
    "total_stages": 5,
    "total_students": 127,
    "completion_rate": 45.67,
    "average_progress": 73.25
  }
}
```

### Interpretación de Métricas
- **127 estudiantes** han comenzado esta categoría
- **45.67%** de ellos (58 estudiantes) completaron las 5 etapas
- El **progreso promedio** es del 73.25% (los estudiantes completan ~3.7 de 5 etapas en promedio)

---

## Ejemplo 2: Categoría Nueva Sin Estudiantes

### Request
```http
GET /categories/5/detail HTTP/1.1
Host: api.edupractica.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response (200 OK)
```json
{
  "id": 5,
  "name": "Machine Learning Avanzado",
  "description": "Técnicas avanzadas de aprendizaje automático",
  "icon": "🤖",
  "stages": [
    {
      "id": 25,
      "order": 1,
      "title": "Redes Neuronales Profundas",
      "description": "Introducción a Deep Learning",
      "is_active": true,
      "media_type": "video"
    },
    {
      "id": 26,
      "order": 2,
      "title": "CNNs para Visión por Computadora",
      "description": "Redes Convolucionales",
      "is_active": true,
      "media_type": null
    }
  ],
  "metrics": {
    "total_stages": 2,
    "total_students": 0,
    "completion_rate": 0.0,
    "average_progress": 0.0
  }
}
```

---

## Ejemplo 3: Buscar Estudiantes en una Categoría

### Request (Sin búsqueda)
```http
GET /categories/1/students HTTP/1.1
Host: api.edupractica.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response (200 OK)
```json
[
  {
    "id": 15,
    "email": "carlos.mendez@example.com",
    "full_name": "Carlos Méndez",
    "completed_stages": 5,
    "total_stages": 5,
    "progress_percentage": 100.0
  },
  {
    "id": 23,
    "email": "laura.santos@example.com",
    "full_name": "Laura Santos",
    "completed_stages": 4,
    "total_stages": 5,
    "progress_percentage": 80.0
  },
  {
    "id": 8,
    "email": "miguel.torres@example.com",
    "full_name": "Miguel Torres",
    "completed_stages": 3,
    "total_stages": 5,
    "progress_percentage": 60.0
  },
  {
    "id": 42,
    "email": "sofia.ramirez@example.com",
    "full_name": "Sofía Ramírez",
    "completed_stages": 1,
    "total_stages": 5,
    "progress_percentage": 20.0
  }
]
```

### Request (Con búsqueda)
```http
GET /categories/1/students?search=laura HTTP/1.1
Host: api.edupractica.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response (200 OK)
```json
[
  {
    "id": 23,
    "email": "laura.santos@example.com",
    "full_name": "Laura Santos",
    "completed_stages": 4,
    "total_stages": 5,
    "progress_percentage": 80.0
  }
]
```

---

## Ejemplo 4: Categoría No Encontrada

### Request
```http
GET /categories/999/detail HTTP/1.1
Host: api.edupractica.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response (404 Not Found)
```json
{
  "detail": "Category not found"
}
```

---

## Ejemplo 5: Usuario Sin Permisos

### Request (Usuario estudiante intentando acceder)
```http
GET /categories/1/detail HTTP/1.1
Host: api.edupractica.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.student_token...
```

### Response (403 Forbidden)
```json
{
  "detail": "The user doesn't have enough privileges"
}
```

---

## Integración Frontend (Ejemplo React)

```jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

function CategoryDetailPage() {
  const { categoryId } = useParams();
  const navigate = useNavigate();
  const [category, setCategory] = useState(null);
  const [students, setStudents] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCategoryDetail();
  }, [categoryId]);

  const fetchCategoryDetail = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/categories/${categoryId}/detail`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setCategory(data);
      }
    } catch (error) {
      console.error('Error fetching category:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchStudents = async () => {
    try {
      const url = searchTerm 
        ? `http://localhost:8000/categories/${categoryId}/students?search=${searchTerm}`
        : `http://localhost:8000/categories/${categoryId}/students`;
        
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setStudents(data);
      }
    } catch (error) {
      console.error('Error searching students:', error);
    }
  };

  if (loading) return <div>Cargando...</div>;
  if (!category) return <div>Categoría no encontrada</div>;

  return (
    <div className="category-detail-container">
      {/* Header Section */}
      <header className="category-header">
        <button onClick={() => navigate('/categories')} className="back-button">
          ← Volver al listado
        </button>
        <h1>{category.icon} {category.name}</h1>
        <p>{category.description}</p>
      </header>

      {/* Metrics Section */}
      <section className="metrics-grid">
        <div className="metric-card">
          <h3>Total de Etapas</h3>
          <p className="metric-value">{category.metrics.total_stages}</p>
        </div>
        <div className="metric-card">
          <h3>Estudiantes</h3>
          <p className="metric-value">{category.metrics.total_students}</p>
        </div>
        <div className="metric-card">
          <h3>Tasa de Completitud</h3>
          <p className="metric-value">{category.metrics.completion_rate}%</p>
        </div>
        <div className="metric-card">
          <h3>Progreso Promedio</h3>
          <p className="metric-value">{category.metrics.average_progress}%</p>
        </div>
      </section>

      {/* Stages Section */}
      <section className="stages-section">
        <h2>Etapas Asociadas</h2>
        <div className="stages-list">
          {category.stages.map(stage => (
            <div key={stage.id} className="stage-item">
              <span className="stage-order">{stage.order}</span>
              <div className="stage-info">
                <h3>{stage.title}</h3>
                <p>{stage.description}</p>
              </div>
              {stage.media_type && (
                <span className={`media-badge ${stage.media_type}`}>
                  {stage.media_type}
                </span>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Students Search Section */}
      <section className="students-section">
        <h2>Estudiantes que Usan esta Categoría</h2>
        <div className="search-box">
          <input
            type="text"
            placeholder="Buscar por nombre o email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button onClick={searchStudents}>Buscar</button>
        </div>
        
        <div className="students-list">
          {students.map(student => (
            <div key={student.id} className="student-item">
              <div className="student-info">
                <h4>{student.full_name}</h4>
                <p>{student.email}</p>
              </div>
              <div className="student-progress">
                <span>{student.completed_stages}/{student.total_stages} etapas</span>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${student.progress_percentage}%` }}
                  />
                </div>
                <span>{student.progress_percentage}%</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default CategoryDetailPage;
```

---

## CSS Responsive (Mobile-First)

```css
/* Mobile First */
.category-detail-container {
  padding: 1rem;
  max-width: 100%;
}

.category-header {
  margin-bottom: 2rem;
}

.back-button {
  background: none;
  border: 1px solid #ddd;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 1rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
}

.metric-value {
  font-size: 2rem;
  font-weight: bold;
  color: #007bff;
}

.stages-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.stage-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.media-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
}

.media-badge.video { background: #e3f2fd; color: #1976d2; }
.media-badge.audio { background: #f3e5f5; color: #7b1fa2; }
.media-badge.image { background: #e8f5e9; color: #388e3c; }

/* Tablet (768px and up) */
@media (min-width: 768px) {
  .category-detail-container {
    padding: 2rem;
  }

  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop (1024px and up) */
@media (min-width: 1024px) {
  .category-detail-container {
    max-width: 1200px;
    margin: 0 auto;
  }

  .metrics-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
```
