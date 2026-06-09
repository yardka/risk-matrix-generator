# Risk Matrix Generator

Herramienta profesional para la gestión de riesgos de activos de información basada en **ISO/IEC 27001:2022**, **NIST CSF 2.0** y **MAGERIT v3**.

## Arquitectura

```
risk-matrix-generator/
├── backend/          # API REST con FastAPI (Python)
├── frontend/         # SPA vanilla HTML/CSS/JS
├── database/         # SQLite (Fase 2)
└── docs/             # Frontend para GitHub Pages
```

### Backend
- **FastAPI** con motor de riesgo `Riesgo = Probabilidad × Impacto`
- Clasificación de activos por triada CIA (Confidencialidad, Integridad, Disponibilidad)
- Recomendación automática de controles ISO 27001 / NIST CSF
- Matriz de calor 5×5 interactiva

### Frontend
- Vanilla JS (sin frameworks) con diseño responsive
- Matriz de calor con tooltips interactivos
- Formularios de clasificación, cálculo de riesgo y controles
- Tema oscuro profesional con animaciones

## Despliegue

### Backend (Render)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend (GitHub Pages)
Configurado en `Settings → Pages → Branch: main, folder: /docs`

## Variables de entorno

| Variable | Por defecto | Descripción |
|---|---|---|
| `ALLOWED_ORIGINS` | `http://localhost:5500,...` | Orígenes CORS permitidos |
| `APP_PORT` | `8000` | Puerto del servidor |
| `DATABASE_URL` | `sqlite:///./database/risk_matrix.db` | Conexión a BD |
