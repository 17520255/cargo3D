from pydantic import BaseModel
from typing import List, Optional

class BoxRequest(BaseModel):
    id: str
    width: float
    height: float
    depth: float
    name: str
    label: str
    weight: float

class ContainerRequest(BaseModel):
    width: float
    height: float
    depth: float

class PackingRequest(BaseModel):
    goods: List[BoxRequest]
    container: ContainerRequest
    algorithm: str = "genetic"
    iterations: int = 5

class PackingResponse(BaseModel):
    placed_boxes: List[dict]
    utilization: float
    total_volume: float
    used_volume: float
    execution_time: float 