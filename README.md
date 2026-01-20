# EduPractica API

Este proyecto es una API construida con FastAPI y configuración para SQLite.

## Requisitos

- Python 3.9+

## Instalación

1. Crear un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   ```

2. Activar el entorno virtual:
   - **Windows:** `.\venv\Scripts\activate`
   - **Unix/MacOS:** `source venv/bin/activate`

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución

Para iniciar el servidor de desarrollo:

```bash
uvicorn app.main:app --reload
```

La documentación interactiva estará disponible en `http://127.0.0.1:8000/docs`.
