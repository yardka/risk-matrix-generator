from dataclasses import dataclass, field
import json
from pathlib import Path
from collections import defaultdict
from .risk_engine import RiskLevel
from .asset_classifier import AssetType

_CONTROLS_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "controls_data.json"

@dataclass
class SecurityControl:
    id:          str
    framework:   str
    category:    str
    name:        str
    description: str
    priority:    str

@dataclass
class ControlRecommendation:
    risk_level:      RiskLevel
    asset_type:      AssetType
    total_controls:  int
    immediate:       list[SecurityControl] = field(default_factory=list)
    short_term:      list[SecurityControl] = field(default_factory=list)
    long_term:       list[SecurityControl] = field(default_factory=list)
    treatment_plan:  str = ""


def _load_controls_data() -> dict:
    with open(_CONTROLS_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _to_security_control(c: dict) -> SecurityControl:
    return SecurityControl(**c)


def get_control_recommendations(
    risk_level: RiskLevel,
    asset_type: AssetType,
) -> ControlRecommendation:
    data = _load_controls_data()

    base_controls_raw = data["controls_by_level"].get(risk_level.value, [])
    asset_controls_raw = data["controls_by_asset_type"].get(asset_type.value, [])

    all_controls_raw = base_controls_raw + asset_controls_raw
    all_controls = [_to_security_control(c) for c in all_controls_raw]

    buckets: dict[str, list[SecurityControl]] = {"Inmediata": [], "Corto plazo": [], "Largo plazo": []}
    for ctrl in all_controls:
        buckets.setdefault(ctrl.priority, []).append(ctrl)

    treatment_plan = data["treatment_strategies"].get(risk_level.value, "")

    return ControlRecommendation(
        risk_level=risk_level,
        asset_type=asset_type,
        total_controls=len(all_controls),
        immediate=buckets.get("Inmediata", []),
        short_term=buckets.get("Corto plazo", []),
        long_term=buckets.get("Largo plazo", []),
        treatment_plan=treatment_plan,
    )
