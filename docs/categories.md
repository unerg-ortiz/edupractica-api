# Categories API Documentation

## Overview
This document describes the endpoints for managing educational categories in the EduPractica API.

## Endpoints

### 1. Create Category
**POST** `/categories/`

Create a new category (Admin only).

**Authentication:** Required (Superuser)

**Request Body:**
```json
{
  "name": "Python Básico",
  "description": "Introducción a la programación con Python",
  "icon": "🐍"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Python Básico",
  "description": "Introducción a la programación con Python",
  "icon": "🐍"
}
```

---

### 2. List Categories
**GET** `/categories/`

Get all categories with pagination.

**Authentication:** Required (Any user)

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Python Básico",
    "description": "Introducción a la programación con Python",
    "icon": "🐍"
  },
  {
    "id": 2,
    "name": "JavaScript Avanzado",
    "description": "Conceptos avanzados de JavaScript",
    "icon": "⚡"
  }
]
```

---

### 3. Get Category (Basic)
**GET** `/categories/{category_id}`

Get basic information about a specific category.

**Authentication:** Required (Any user)

**Path Parameters:**
- `category_id` (int): ID of the category

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Python Básico",
  "description": "Introducción a la programación con Python",
  "icon": "🐍"
}
```

**Error Responses:**
- `404 Not Found`: Category not found

---

### 4. Get Category Detail (Enhanced)
**GET** `/categories/{category_id}/detail`

Get detailed information about a category including stages and metrics.

**Authentication:** Required (Superuser/Admin)

**Path Parameters:**
- `category_id` (int): ID of the category

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Python Básico",
  "description": "Introducción a la programación con Python",
  "icon": "🐍",
  "stages": [
    {
      "id": 1,
      "order": 1,
      "title": "Instalación de Python",
      "description": "Aprende a instalar Python en tu computadora",
      "is_active": true,
      "media_type": "video"
    },
    {
      "id": 2,
      "order": 2,
      "title": "Variables y Tipos de Datos",
      "description": "Conceptos básicos de variables",
      "is_active": true,
      "media_type": "image"
    },
    {
      "id": 3,
      "order": 3,
      "title": "Estructuras de Control",
      "description": "If, else, loops",
      "is_active": true,
      "media_type": null
    }
  ],
  "metrics": {
    "total_stages": 3,
    "total_students": 45,
    "completion_rate": 68.89,
    "average_progress": 82.22
  }
}
```

**Metrics Explanation:**
- `total_stages`: Number of active stages in this category
- `total_students`: Number of unique students who have started this category
- `completion_rate`: Percentage of students who completed ALL stages (0-100)
- `average_progress`: Average completion percentage across all students (0-100)

**Error Responses:**
- `404 Not Found`: Category not found
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: User is not an administrator

---

### 5. Get Category Students
**GET** `/categories/{category_id}/students`

Get list of students who have accessed this category with their progress.

**Authentication:** Required (Superuser/Admin)

**Path Parameters:**
- `category_id` (int): ID of the category

**Query Parameters:**
- `search` (string, optional): Search students by name or email

**Response (200 OK):**
```json
[
  {
    "id": 5,
    "email": "maria.garcia@example.com",
    "full_name": "María García",
    "completed_stages": 3,
    "total_stages": 3,
    "progress_percentage": 100.0
  },
  {
    "id": 8,
    "email": "juan.perez@example.com",
    "full_name": "Juan Pérez",
    "completed_stages": 2,
    "total_stages": 3,
    "progress_percentage": 66.67
  },
  {
    "id": 12,
    "email": "ana.rodriguez@example.com",
    "full_name": "Ana Rodríguez",
    "completed_stages": 1,
    "total_stages": 3,
    "progress_percentage": 33.33
  }
]
```

**Example with Search:**
```
GET /categories/1/students?search=maria
```

**Error Responses:**
- `404 Not Found`: Category not found
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: User is not an administrator

---

### 6. Update Category
**PUT** `/categories/{category_id}`

Update an existing category (Admin only).

**Authentication:** Required (Superuser)

**Path Parameters:**
- `category_id` (int): ID of the category

**Request Body:**
```json
{
  "name": "Python Básico - Actualizado",
  "description": "Nueva descripción mejorada",
  "icon": "🐍"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Python Básico - Actualizado",
  "description": "Nueva descripción mejorada",
  "icon": "🐍"
}
```

**Error Responses:**
- `404 Not Found`: Category not found
- `400 Bad Request`: Category name already exists

---

### 7. Delete Category
**DELETE** `/categories/{category_id}`

Delete a category (Admin only).

**Authentication:** Required (Superuser)

**Path Parameters:**
- `category_id` (int): ID of the category

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Python Básico",
  "description": "Introducción a la programación con Python",
  "icon": "🐍"
}
```

**Error Responses:**
- `404 Not Found`: Category not found

---

## Use Cases

### Admin Dashboard - Category Review
The `/categories/{category_id}/detail` endpoint is specifically designed for administrators to review comprehensive category information before making changes:

1. **View all stages/topics** in the category
2. **Check metrics** to understand student engagement
3. **Identify problematic categories** with low completion rates
4. **Make data-driven decisions** about content updates

### Student Search Integration
The `/categories/{category_id}/students` endpoint supports the search functionality:

```javascript
// Frontend example
async function searchStudentsInCategory(categoryId, searchTerm) {
  const response = await fetch(
    `/categories/${categoryId}/students?search=${encodeURIComponent(searchTerm)}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  return await response.json();
}
```

### Responsive UI Integration
All endpoints return JSON data that can be easily consumed by responsive frontends:

```html
<!-- Desktop view: Full table -->
<table class="desktop-table">
  <thead>
    <tr>
      <th>Stage</th>
      <th>Description</th>
      <th>Media</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    <!-- Render stages -->
  </tbody>
</table>

<!-- Mobile view: Card layout -->
<div class="mobile-cards">
  <div class="stage-card" *ngFor="let stage of stages">
    <h3>{{ stage.title }}</h3>
    <p>{{ stage.description }}</p>
    <span class="media-badge" *ngIf="stage.media_type">
      {{ stage.media_type }}
    </span>
  </div>
</div>
```

---

## Error Handling

All endpoints follow standard HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message description"
}
```
