# Stage Approval Workflow (Admin Documentation)

## Overview
This document describes the process through which administrators supervise and approve educational stages (temas) uploaded by professors. Only approved stages are visible to students.

## Workflow Statuses
- **`pending`**: Default status when a stage is created. Invisible to students.
- **`approved`**: The stage is verified and accessible to students.
- **`rejected`**: The stage requires changes. It remains invisible, and feedback is provided to the professor.

---

## 1. List Pending Stages
**GET** `/api/stages/review/pending`

Returns a list of all stages waiting for administrator approval.

**Authentication:** Required (Superuser/Admin)

**Response:**
```json
[
  {
    "id": 15,
    "title": "Introducción a Grafo",
    "professor_id": 5,
    "approval_status": "pending",
    "submitted_at": "2026-02-13T01:50:00Z",
    ...
  }
]
```

---

## 2. Approve or Reject a Stage
**POST** `/api/stages/review/{stage_id}`

The administrator reviews the content and decides whether to approve or reject it.

**Authentication:** Required (Superuser/Admin)

**Request Body (Approve):**
```json
{
  "approved": true,
  "comment": "Perfecto, el contenido es claro y las imágenes son adecuadas."
}
```

**Request Body (Reject):**
```json
{
  "approved": false,
  "comment": "Por favor, mejora la calidad del audio en el reto interactivo."
}
```

**Response (200 OK):**
Returns the updated `Stage` object with the new status and comment.

---

## Professor Experience (Notifications)
When a stage is created via `POST /api/stages`, it is automatically assigned the `pending` status.

### Status Tracking
Professors can track their stages' status via the standard `GET /api/stages/{id}` endpoint.

### Dashboard (Waitlist)
The Admin Dashboard should display a "Review queue" using the `/review/pending` endpoint.

---

## Visibility Rules
- **Students**: Can only see stages where `approval_status == 'approved'`.
- **Admins/Superusers**: Can see ALL stages regardless of status.

---

## Email/Push Notifications (Future Integration)
The system is prepared to trigger notifications to the `professor_id` using the `approval_comment` when the status changes.
- **On Approval**: "Tu tema 'X' ha sido aprobado y ya está disponible para los alumnos."
- **On Rejection**: "Tu tema 'X' requiere correcciones. Comentario: Y."
