from enum import Enum
from dataclasses import dataclass


class AssetType(str, Enum):
    HARDWARE      = "hardware"
    SOFTWARE      = "software"
    DATA          = "data"
    NETWORK       = "network"
    PEOPLE        = "people"
    PHYSICAL      = "physical"
    SERVICE       = "service"


class CIALevel(str, Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"


class AssetCriticality(str, Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"


_CIA_WEIGHT: dict[CIALevel, int] = {
    CIALevel.LOW:      1,
    CIALevel.MEDIUM:   2,
    CIALevel.HIGH:     3,
    CIALevel.CRITICAL: 4,
}

_CRITICALITY_FROM_SCORE: list[tuple[int, AssetCriticality]] = [
    (4,  AssetCriticality.LOW),
    (7,  AssetCriticality.MEDIUM),
    (10, AssetCriticality.HIGH),
    (12, AssetCriticality.CRITICAL),
]


@dataclass
class AssetClassification:
    asset_type:       AssetType
    confidentiality:  CIALevel
    integrity:        CIALevel
    availability:     CIALevel
    criticality:      AssetCriticality
    cia_score:        int
    rationale:        str


def classify_asset(
    asset_type: AssetType,
    confidentiality: CIALevel,
    integrity: CIALevel,
    availability: CIALevel,
) -> AssetClassification:
    score = (
        _CIA_WEIGHT[confidentiality]
        + _CIA_WEIGHT[integrity]
        + _CIA_WEIGHT[availability]
    )

    criticality = AssetCriticality.CRITICAL
    for threshold, level in _CRITICALITY_FROM_SCORE:
        if score <= threshold:
            criticality = level
            break

    rationale = (
        f"Activo de tipo '{asset_type.value}' con perfil CIA "
        f"[C={confidentiality.value} | I={integrity.value} | A={availability.value}]. "
        f"Puntuación CIA agregada: {score}/12. "
        f"Criticidad resultante: {criticality.value.upper()}."
    )

    return AssetClassification(
        asset_type=asset_type,
        confidentiality=confidentiality,
        integrity=integrity,
        availability=availability,
        criticality=criticality,
        cia_score=score,
        rationale=rationale,
    )
