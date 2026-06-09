"""
test_api.py — Script de prueba rápida de la API (Fase 1)
Ejecutar desde: backend/ con el venv activo y el servidor corriendo.
"""
import sys
import io
# pyrefly: ignore [missing-import]
import httpx
import json

# Forzar UTF-8 en la salida estándar (necesario en Windows con cp1252)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = "https://risk-matrix-generator.onrender.com"

def sep(label, status):
    print(f"\n{'='*60}")
    print(f"  {label}  [{status}]")
    print("="*60)

def pretty(label, r):
    sep(label, r.status_code)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))

# ─── 1. Health check ──────────────────────────────────────────
pretty("GET /", httpx.get(f"{BASE}/"))

# ─── 2. Matriz de calor ───────────────────────────────────────
r = httpx.get(f"{BASE}/api/v1/matrix")
data = r.json()
sep("GET /api/v1/matrix", r.status_code)
print("Matriz 5x5 (Probabilidad ↓ | Impacto →)\n")
print("     " + "  ".join(f"I={c['impact']}" for c in data["matrix"][0]))
for row in data["matrix"]:
    prob = row[0]["probability"]
    cells = "  ".join(f"{c['score']:2d}({c['level'][:3]})" for c in row)
    print(f"P={prob}  {cells}")

# ─── 3. Clasificar activo ─────────────────────────────────────
pretty("POST /api/v1/assets/classify", httpx.post(
    f"{BASE}/api/v1/assets/classify",
    json={
        "asset_name": "Servidor de Base de Datos",
        "asset_type": "data",
        "confidentiality": "high",
        "integrity": "high",
        "availability": "medium",
    }
))

# ─── 4. Calcular riesgo intrínseco/residual ───────────────────
pretty("POST /api/v1/risks/calculate", httpx.post(
    f"{BASE}/api/v1/risks/calculate",
    json={
        "threat_name": "Ransomware",
        "asset_name": "Servidor de BD",
        "intrinsic_probability": 4,
        "intrinsic_impact": 5,
        "residual_probability": 2,
        "residual_impact": 3,
    }
))

# ─── 5. Recomendación de controles ───────────────────────────
r = httpx.post(
    f"{BASE}/api/v1/controls/recommend",
    json={"risk_level": "critical", "asset_type": "data"},
)
data = r.json()
sep("POST /api/v1/controls/recommend", r.status_code)
print(f"Total controles: {data['total_controls']}")
print(f"\nInmediatos ({len(data['immediate'])}):")
for c in data["immediate"]:
    print(f"  [{c['id']}] {c['name']}")
print(f"\nCorto plazo ({len(data['short_term'])}):")
for c in data["short_term"]:
    print(f"  [{c['id']}] {c['name']}")
print(f"\nPlan de tratamiento:\n  {data['treatment_plan']}")

# ─── 6. Metadatos ─────────────────────────────────────────────
pretty("GET /api/v1/meta/scales", httpx.get(f"{BASE}/api/v1/meta/scales"))

print("\n\n✅  Todas las pruebas completadas exitosamente.\n")
