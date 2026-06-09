from enum import Enum
from dataclasses import dataclass


class Probability(int, Enum):
    VERY_RARE   = 1
    RARE        = 2
    POSSIBLE    = 3
    PROBABLE    = 4
    ALMOST_SURE = 5


PROBABILITY_LABELS: dict[int, str] = {
    1: "Muy Rara",
    2: "Rara",
    3: "Posible",
    4: "Probable",
    5: "Casi Cierta",
}


class Impact(int, Enum):
    INSIGNIFICANT = 1
    MINOR         = 2
    MODERATE      = 3
    MAJOR         = 4
    CATASTROPHIC  = 5


IMPACT_LABELS: dict[int, str] = {
    1: "Insignificante",
    2: "Menor",
    3: "Moderado",
    4: "Mayor",
    5: "Catastrófico",
}


class RiskLevel(str, Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"


RISK_LEVEL_COLORS: dict[RiskLevel, str] = {
    RiskLevel.LOW:      "#22c55e",
    RiskLevel.MEDIUM:   "#eab308",
    RiskLevel.HIGH:     "#f97316",
    RiskLevel.CRITICAL: "#ef4444",
}

_LEVEL_LABELS: dict[RiskLevel, str] = {
    RiskLevel.LOW:      "Bajo",
    RiskLevel.MEDIUM:   "Medio",
    RiskLevel.HIGH:     "Alto",
    RiskLevel.CRITICAL: "Crítico",
}

_RISK_THRESHOLDS: list[tuple[int, RiskLevel]] = [
    (4,  RiskLevel.LOW),
    (9,  RiskLevel.MEDIUM),
    (16, RiskLevel.HIGH),
    (25, RiskLevel.CRITICAL),
]


@dataclass
class RiskScore:
    probability:       int
    impact:            int
    score:             int
    level:             RiskLevel
    color:             str
    probability_label: str
    impact_label:      str
    level_label:       str


@dataclass
class RiskAssessment:
    threat_name:    str
    asset_name:     str
    intrinsic:      RiskScore
    residual:       RiskScore

    @property
    def risk_reduction(self) -> int:
        return max(0, self.intrinsic.score - self.residual.score)

    @property
    def reduction_pct(self) -> float:
        if self.intrinsic.score <= 0:
            return 0.0
        return round((self.risk_reduction / self.intrinsic.score) * 100, 1)


def _score_to_level(score: int) -> RiskLevel:
    for threshold, level in _RISK_THRESHOLDS:
        if score <= threshold:
            return level
    return RiskLevel.CRITICAL


def calculate_risk(probability: int, impact: int) -> RiskScore:
    if not (1 <= probability <= 5):
        raise ValueError(f"Probabilidad debe estar entre 1 y 5. Recibido: {probability}")
    if not (1 <= impact <= 5):
        raise ValueError(f"Impacto debe estar entre 1 y 5. Recibido: {impact}")

    score = probability * impact
    level = _score_to_level(score)

    return RiskScore(
        probability=probability,
        impact=impact,
        score=score,
        level=level,
        color=RISK_LEVEL_COLORS[level],
        probability_label=PROBABILITY_LABELS[probability],
        impact_label=IMPACT_LABELS[impact],
        level_label=_LEVEL_LABELS[level],
    )


def assess_risk(
    threat_name: str,
    asset_name: str,
    intrinsic_probability: int,
    intrinsic_impact: int,
    residual_probability: int,
    residual_impact: int,
) -> RiskAssessment:
    intrinsic = calculate_risk(intrinsic_probability, intrinsic_impact)
    residual  = calculate_risk(residual_probability, residual_impact)

    return RiskAssessment(
        threat_name=threat_name,
        asset_name=asset_name,
        intrinsic=intrinsic,
        residual=residual,
    )


def generate_heat_matrix() -> list[list[dict]]:
    matrix: list[list[dict]] = []
    for prob in range(5, 0, -1):
        row: list[dict] = []
        for imp in range(1, 6):
            rs = calculate_risk(prob, imp)
            row.append({
                "probability":       rs.probability,
                "impact":            rs.impact,
                "score":             rs.score,
                "level":             rs.level.value,
                "color":             rs.color,
                "probability_label": rs.probability_label,
                "impact_label":      rs.impact_label,
            })
        matrix.append(row)
    return matrix
