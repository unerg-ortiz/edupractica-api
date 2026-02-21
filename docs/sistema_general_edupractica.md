# Documento general del sistema EduPractica

## 1) ¿De qué trata el sistema?

EduPractica es una plataforma educativa orientada a la **gestión y consumo de contenidos por etapas**, con foco en aprendizaje progresivo y seguimiento académico. El sistema integra:

- **Estudiantes**: avanzan por rutas de aprendizaje (stages) con desbloqueo secuencial.
- **Profesores**: crean y transfieren contenido, y gestionan recursos académicos.
- **Administradores**: supervisan usuarios, categorías, aprobación de contenido y analítica.

En conjunto, los dos repositorios (`edupractica-api` y `edupractica-app`) implementan un sistema web de tipo **cliente-servidor**, donde el frontend consume APIs REST del backend para autenticación, administración académica y trazabilidad del progreso.

---

## 2) Funcionalidades principales del sistema

### 2.1 Gestión de identidad y acceso
- Inicio de sesión por credenciales (`/login/access-token`).
- Autenticación social OAuth (Google/Microsoft).
- Control por roles (admin/superuser, profesor, estudiante) y restricciones por endpoint.
- Health-check de servicio (`/health`).

### 2.2 Gestión académica por categorías y etapas
- CRUD de categorías (incluyendo listado administrativo avanzado con búsqueda, ordenamiento y detección de duplicados).
- CRUD de etapas (stages) asociadas a categorías.
- Flujo de progreso por estudiante con etapas **desbloqueadas/completadas**.
- Marcado de etapa completada con desbloqueo automático de la siguiente.

### 2.3 Revisión y aprobación de contenidos
- Cola de revisión de etapas pendientes para administración.
- Aprobación/rechazo con comentarios de revisión.
- Regla de visibilidad: estudiantes solo ven contenido aprobado.

### 2.4 Feedback pedagógico y apoyo al estudiante
- Gestión de pistas/correcciones/mensajes (feedback) por etapa.
- Carga de recursos multimedia para feedback (imagen/audio).
- Registro de intentos y consumo de pistas por intento.

### 2.5 Analítica académica y reportes
- Métricas de dashboard para administración y profesor.
- Identificación de etapas difíciles y tasa de éxito.
- Exportación de datos a **Excel** y **PDF** para seguimiento institucional.

### 2.6 Transferencia de contenido entre profesores
- Búsqueda de colegas.
- Solicitud de transferencia de contenido.
- Aceptación/rechazo de solicitud y notificaciones.
- En frontend existe flujo dedicado de transferencia (`initiate/request/success`) con enfoque UX para continuidad académica.

### 2.7 Frontend funcional por áreas
- Vistas localizadas por idioma (`[lang]`).
- Áreas de administración: analítica, categorías, revisión de contenido, gestión de usuarios y retos.
- Área de profesor: panel, transferencia de contenido.
- Área de estudiante/perfil: learning path, perfil, control de acceso bloqueado.

---

## 3) División del sistema entre Backend y Frontend

## Backend (`edupractica-api`)
Responsable de la lógica de negocio, seguridad y persistencia de datos:

- Exposición de API REST (FastAPI).
- Validación y serialización de datos (schemas Pydantic).
- Modelado de entidades con SQLAlchemy (usuario, categoría, etapa, feedback, transferencia, auditoría).
- Autorización por rol en endpoints.
- Procesamiento de analítica y generación de reportes.
- Integración con almacenamiento/local uploads y cliente Supabase.

## Frontend (`edupractica-app`)
Responsable de la experiencia de usuario y orquestación de flujos:

- Aplicación web con Next.js (App Router).
- Internacionalización por ruta dinámica (`[lang]`) y archivos de mensajes.
- UI administrativa, profesor y estudiante.
- Patrón MVVM en capa de frontend (Views + hooks como ViewModel + services como acceso API).
- Estado global con Zustand y validación de formularios con Zod.

---

## 4) Stack tecnológico por proyecto

## Stack Backend
- **Python 3.9+**
- **FastAPI** (API REST)
- **Uvicorn** (servidor ASGI)
- **SQLAlchemy 2.x** (ORM)
- **SQLite** (entorno de desarrollo)
- **Pydantic Settings** (configuración)
- **python-jose, passlib/argon2** (autenticación/seguridad)
- **fastapi-sso + httpx** (OAuth)
- **Pandas + Openpyxl + ReportLab** (exportación y reportes)
- **Pillow** (procesamiento de imágenes)
- **Supabase SDK** (integración de almacenamiento/servicios)

## Stack Frontend
- **Next.js 16 + React 19 + TypeScript**
- **App Router**
- **Tailwind CSS v4 + Material Tailwind**
- **next-intl** (i18n)
- **Zustand** (estado)
- **Zod + react-hook-form** (validación y formularios)
- **ESLint** (calidad de código)

---

## 5) Relación con prácticas de ingeniería de software solicitadas

A continuación se describe cómo el sistema evidencia o permite aplicar las prácticas indicadas.

## 5.1 Metodología Scrum
Aplicación práctica observada/propuesta en este sistema:

- **Product Backlog**: funcionalidades separables por módulos (auth, categorías, etapas, aprobación, analítica, transferencias).
- **Sprints**: cada módulo puede planificarse como incremento vertical (UI + API + pruebas).
- **Definition of Done**: endpoint implementado + documentación en `docs/` + vista integrada en frontend + validación de permisos.
- **Revisión incremental**: evidencia de evolución por features específicas (ej. content transfer, stage approval, analytics export).

## 5.2 Procesos, tareas y modelo MM
Tomando MM como un enfoque de **medición/mejora de madurez del proceso**, la solución refleja:

- **Procesos definidos**: autenticación, gestión académica, revisión de contenido, seguimiento analítico.
- **Tareas trazables**: CRUD por entidad, aprobación/rechazo, registro de intentos, exportación de reportes.
- **Métricas de control**: completion rate, success rate, difficult stages, intentos fallidos/exitosos.
- **Mejora continua**: la analítica habilita decisiones de iteración sobre contenido y experiencia pedagógica.

## 5.3 UML
El sistema se presta claramente a modelado UML en varios niveles:

- **Casos de uso**: estudiante completa etapas; profesor transfiere contenido; admin aprueba/rechaza etapas.
- **Diagrama de clases**: entidades centrales (`User`, `Category`, `Stage`, `Feedback`, `TransferRequest`, `Audit`).
- **Diagramas de secuencia**: login OAuth, aprobación de etapa, flujo de transferencia entre profesores.
- **Diagramas de componentes**: frontend Next.js ↔ API FastAPI ↔ DB/servicios externos.

## 5.4 ADOO (Análisis y Diseño Orientado a Objetos)
Se observa aplicación de ADOO mediante:

- **Modelado de dominio por objetos** (modelos ORM por entidad del negocio).
- **Responsabilidades separadas** (endpoints, CRUD, schemas, services).
- **Encapsulamiento de reglas** (autorización por rol y lógica de negocio en capas).
- **Extensibilidad** (nuevos tipos de desafíos interactivos y nuevas métricas sin romper arquitectura base).

## 5.5 Análisis de los modelos de descripción
La documentación técnica y estructura de capas permiten analizar coherencia entre:

- Modelo funcional (qué hace el sistema: auth, gestión de contenidos, revisión, analítica).
- Modelo de datos (entidades y relaciones académicas).
- Modelo de interacción (rutas frontend por rol y endpoints backend).
- Modelo de despliegue lógico (cliente web + API + base de datos + servicios auxiliares).

## 5.6 Análisis situacional y documental
Se evidencia en:

- **Situacional**: necesidad educativa real de continuidad académica, control de calidad del contenido y monitoreo del progreso.
- **Documental**: endpoints documentados en `edupractica-api/docs/` con descripción, entradas, salidas y ejemplos.
- **Trazabilidad**: la documentación de módulos (auth, users, categories, stages, feedback, approval, challenges) respalda decisiones funcionales.

## 5.7 Definición de requerimientos
Puede estructurarse (y en gran parte ya se refleja) en:

- **Requerimientos funcionales**: autenticación, CRUD, aprobaciones, progreso, analítica, transferencias.
- **No funcionales**: seguridad por roles, mantenibilidad por capas, internacionalización en UI, exportabilidad de datos.
- **Reglas de negocio**: visibilidad por estado de aprobación, desbloqueo secuencial de etapas, control de acceso por perfil.

---

## 6) Conclusión general

EduPractica, como sistema compuesto por backend y frontend desacoplados, implementa una arquitectura sólida para una plataforma educativa con enfoque en trazabilidad del aprendizaje, gobernanza del contenido y operación multirol. Además, su organización técnica permite mapear de forma clara prácticas formales de ingeniería de software (Scrum, modelado UML, ADOO, análisis y definición de requerimientos), facilitando su uso tanto en producción académica como en contextos de documentación y evaluación de procesos.
