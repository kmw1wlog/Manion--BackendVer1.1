from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
from enum import Enum

class SchemaVersion(str, Enum):
    MVP = "1.0-mvp"
    FULL = "1.0"

class Problem(BaseModel):
    id: str
    statement: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProofStep(BaseModel):
    step: int
    rule: str
    expr_in: str
    expr_out: str
    comment: Optional[str] = None

class VisualAction(str, Enum):
    CREATE_AXES = "CreateAxes"
    PLOT_FUNCTION = "PlotFunction"
    HIGHLIGHT_POINT = "HighlightPoint"
    CREATE_TEX = "CreateTex"
    FADE_IN = "FadeIn"
    INDICATE = "Indicate"

class VisualStep(BaseModel):
    action: VisualAction
    params: Dict[str, Any] = Field(default_factory=dict)

class VisualSection(BaseModel):
    section_name: str
    steps: List[Dict[str, Any]]

class Visual(BaseModel):
    type: str = "ManimScene"
    sections: List[VisualSection]

class Verification(BaseModel):
    sympy: Union[str, Dict[str, Any]]
    wolfram_alpha: Optional[Dict[str, Any]] = None

class BuildOptions(BaseModel):
    fps: int = 30
    resolution: str = "1400x800"
    theme: str = "dark"

class Build(BaseModel):
    options: BuildOptions
    hash_key: Optional[str] = None
    created_at: Optional[str] = None

class MNIFile(BaseModel):
    schema_version: SchemaVersion
    problem: Problem
    proof_tape: List[Union[str, ProofStep]]
    visual: Visual
    verification: Verification
    build: Optional[Build] = None
    notes: Optional[str] = None
