import logging
from dataclasses import asdict

from fastapi import APIRouter, HTTPException
from app.core.asset_classifier import classify_asset, AssetType, CIALevel
from app.core.risk_engine import (
    assess_risk, generate_heat_matrix,
    PROBABILITY_LABELS, IMPACT_LABELS, RiskLevel,
)
from app.core.controls_advisor import get_control_recommendations
from app.core.schemas import (
    ClassifyAssetRequest, AssetClassificationOut,
    CalculateRiskRequest, RiskAssessmentOut, RiskScoreOut,
    GetControlsRequest, ControlRecommendationOut, SecurityControlOut,
    HeatMatrixOut, HeatMatrixCellOut,
)

logger = logging.getLogger("risk_matrix.api")
router = APIRouter()


@router.get(
    "/matrix",
    response_model=HeatMatrixOut,
    summary="Obtener la Matriz de Calor 5×5",
    description="Devuelve todas las celdas de la matriz de riesgo con su puntuación, nivel y color.",
)
def get_heat_matrix():
    raw_matrix = generate_heat_matrix()

    matrix_out = [
        [HeatMatrixCellOut(**cell) for cell in row]
        for row in raw_matrix
    ]

    probability_axis = [
        {"value": v, "label": lbl}
        for v, lbl in sorted(PROBABILITY_LABELS.items(), reverse=True)
    ]
    impact_axis = [
        {"value": v, "label": lbl}
        for v, lbl in sorted(IMPACT_LABELS.items())
    ]

    return HeatMatrixOut(
        matrix=matrix_out,
        probability_axis=probability_axis,
        impact_axis=impact_axis,
    )


@router.post(
    "/assets/classify",
    response_model=AssetClassificationOut,
    summary="Clasificar un activo de información",
    description="Calcula la criticidad del activo a partir de la triada CIA.",
)
def classify_asset_endpoint(body: ClassifyAssetRequest):
    try:
        result = classify_asset(
            asset_type=AssetType(body.asset_type),
            confidentiality=CIALevel(body.confidentiality),
            integrity=CIALevel(body.integrity),
            availability=CIALevel(body.availability),
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return AssetClassificationOut(
        asset_name=body.asset_name,
        asset_type=result.asset_type.value,
        confidentiality=result.confidentiality.value,
        integrity=result.integrity.value,
        availability=result.availability.value,
        criticality=result.criticality.value,
        cia_score=result.cia_score,
        rationale=result.rationale,
    )


@router.post(
    "/risks/calculate",
    response_model=RiskAssessmentOut,
    summary="Calcular riesgo intrínseco y residual",
    description="Aplica la fórmula Riesgo = Probabilidad × Impacto para calcular ambos niveles.",
)
def calculate_risk_endpoint(body: CalculateRiskRequest):
    try:
        assessment = assess_risk(
            threat_name=body.threat_name,
            asset_name=body.asset_name,
            intrinsic_probability=body.intrinsic_probability,
            intrinsic_impact=body.intrinsic_impact,
            residual_probability=body.residual_probability,
            residual_impact=body.residual_impact,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return RiskAssessmentOut(
        threat_name=assessment.threat_name,
        asset_name=assessment.asset_name,
        intrinsic=RiskScoreOut(**asdict(assessment.intrinsic)),
        residual=RiskScoreOut(**asdict(assessment.residual)),
        risk_reduction=assessment.risk_reduction,
        reduction_pct=assessment.reduction_pct,
    )


@router.post(
    "/controls/recommend",
    response_model=ControlRecommendationOut,
    summary="Obtener controles de seguridad recomendados",
    description="Sugiere controles ISO 27001 / NIST CSF basados en el nivel de riesgo y tipo de activo.",
)
def recommend_controls_endpoint(body: GetControlsRequest):
    try:
        recommendation = get_control_recommendations(
            risk_level=RiskLevel(body.risk_level),
            asset_type=AssetType(body.asset_type),
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return ControlRecommendationOut(
        risk_level=recommendation.risk_level.value,
        asset_type=recommendation.asset_type.value,
        total_controls=recommendation.total_controls,
        immediate=[SecurityControlOut(**asdict(c)) for c in recommendation.immediate],
        short_term=[SecurityControlOut(**asdict(c)) for c in recommendation.short_term],
        long_term=[SecurityControlOut(**asdict(c)) for c in recommendation.long_term],
        treatment_plan=recommendation.treatment_plan,
    )


@router.get(
    "/meta/asset-types",
    summary="Tipos de activos disponibles",
)
def get_asset_types():
    return [{"value": t.value, "label": t.value.capitalize()} for t in AssetType]


@router.get(
    "/meta/scales",
    summary="Escalas de probabilidad e impacto",
)
def get_scales():
    return {
        "probability": [
            {"value": v, "label": lbl}
            for v, lbl in sorted(PROBABILITY_LABELS.items())
        ],
        "impact": [
            {"value": v, "label": lbl}
            for v, lbl in sorted(IMPACT_LABELS.items())
        ],
        "cia_levels": [{"value": l.value} for l in CIALevel],
    }
