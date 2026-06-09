# Arquitectura del Sistema — Risk Matrix Generator

## Visión General

Aplicación web para la **gestión de riesgos de activos de información** basada en la
fórmula estándar de la industria:

> **Riesgo = Probabilidad × Impacto**

## Stack Tecnológico

| Capa         | Tecnología          | Propósito                              |
|--------------|---------------------|----------------------------------------|
| Backend      | FastAPI (Python)    | API REST, lógica de negocio            |
| Base de datos| SQLite + SQLAlchemy | Persistencia ligera y portable         |
| Frontend     | HTML5 / CSS3 / Vanilla JS | Interfaz de usuario, Matriz de Calor |

## Fases de Desarrollo

### Fase 1 — Core Lógico
- Clasificación de activos de información
- Cálculo de riesgo intrínseco y residual
- Motor de sugerencia de controles automáticos

### Fase 2 — Base de Datos
- Entidades: `Asset`, `Risk`, `Control`
- Relaciones: un activo tiene múltiples riesgos; un riesgo tiene múltiples controles

### Fase 3 — Frontend
- Dashboard principal con Matriz de Calor interactiva (5×5)
- CRUD de activos, riesgos y controles
- Exportación de reportes

## Diagrama de Componentes (simplificado)

```
[Frontend HTML/JS]
      |
      | HTTP REST (JSON)
      ↓
[FastAPI Backend]
      |
      | SQLAlchemy ORM
      ↓
[SQLite Database]
```
