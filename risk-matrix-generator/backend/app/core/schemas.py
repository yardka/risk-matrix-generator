from pydantic import BaseModel, Field, field_validator
from app.core.asset_classifier import AssetType, CIALevel
from app.core.risk_engine import RiskLevel


class ClassifyAssetRequest(BaseModel):
    asset_name:      str       = Field(..., min_length=2, max_length=120, example="Servidor de Base de Datos")
    asset_type:      AssetType = Field(..., example="data")
    confidentiality: CIALevel  = Field(..., example="high")
    integrity:       CIALevel  = Field(..., example="high")
    availability:    CIALevel  = Field(..., example="medium")

    model_config = {"use_enum_values": True}


class CalculateRiskRequest(BaseModel):
    threat_name:            str = Field(..., min_length=2, max_length=200, example="Ransomware")
    asset_name:             str = Field(..., min_length=2, max_length=120, example="Servidor de BD")
    intrinsic_probability:  int = Field(..., ge=1, le=5, example=4)
    intrinsic_impact:       int = Field(..., ge=1, le=5, example=5)
    residual_probability:   int = Field(..., ge=1, le=5, example=2)
    residual_impact:        int = Field(..., ge=1, le=5, example=4)

    @field_validator("residual_probability")
    @classmethod
    def residual_prob_lte_intrinsic(cls, v, info):
        intrinsic = info.data.get("intrinsic_probability")
        if intrinsic is not None and v > intrinsic:
            raise ValueError("La probabilidad residual no puede ser mayor que la intrínseca.")
        return v

    @field_validator("residual_impact")
    @classmethod
    def residual_impact_lte_intrinsic(cls, v, info):
        intrinsic = info.data.get("intrinsic_impact")
        if intrinsic is not None and v > intrinsic:
            raise ValueError("El impacto residual no puede ser mayor que el intrínseco.")
        return v


class GetControlsRequest(BaseModel):
    risk_level: RiskLevel = Field(..., example="high")
    asset_type: AssetType = Field(..., example="data")

    model_config = {"use_enum_values": True}


class RiskScoreOut(BaseModel):
    probability:       int
    impact:            int
    score:             int
    level:             str
    color:             str
    probability_label: str
    impact_label:      str
    level_label:       str


class AssetClassificationOut(BaseModel):
    asset_name:      str
    asset_type:      str
    confidentiality: str
    integrity:       str
    availability:    str
    criticality:     str
    cia_score:       int
    rationale:       str


class RiskAssessmentOut(BaseModel):
    threat_name:    str
    asset_name:     str
    intrinsic:      RiskScoreOut
    residual:       RiskScoreOut
    risk_reduction: int
    reduction_pct:  float


class SecurityControlOut(BaseModel):
    id:          str
    framework:   str
    category:    str
    name:        str
    description: str
    priority:    str


class ControlRecommendationOut(BaseModel):
    risk_level:     str
    asset_type:     str
    total_controls: int
    immediate:      list[SecurityControlOut]
    short_term:     list[SecurityControlOut]
    long_term:      list[SecurityControlOut]
    treatment_plan: str


class HeatMatrixCellOut(BaseModel):
    probability:       int
    impact:            int
    score:             int
    level:             str
    color:             str
    probability_label: str
    impact_label:      str


class HeatMatrixOut(BaseModel):
    matrix:           list[list[HeatMatrixCellOut]]
    probability_axis: list[dict]
    impact_axis:      list[dict]
