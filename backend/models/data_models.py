from pydantic import BaseModel
from typing import List, Optional

class EmbeddingPoint(BaseModel):
    annotation_id: int
    x: float
    y: float
    class_name: str

class SelectionRequest(BaseModel):
    x_min: float
    x_max: float
    y_min: float
    y_max: float

class SelectionResponse(BaseModel):
    annotation_ids: List[int]

class RemoveRequest(BaseModel):
    annotation_ids: List[int]

class RemoveResponse(BaseModel):
    success: bool
    removed_count: int
    output_file: str

class ClassesResponse(BaseModel):
    classes: List[str]

class HealthResponse(BaseModel):
    status: str
    embeddings_loaded: bool
    annotations_loaded: bool
    mapping_loaded: bool