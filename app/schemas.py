from typing import Literal
from pydantic import BaseModel, Field

Risk = Literal['LOW','MEDIUM','HIGH','REVIEW']
DeploymentStatus = Literal['success','failed','partial']

class DeploymentChanges(BaseModel):
    database: str | None = None
    driver: str | None = None
    dependencies: str | None = None
    infrastructure: str | None = None
    configuration: str | None = None
    api: str | None = None

class DeploymentRequest(BaseModel):
    application: str
    version: str
    environment: str
    description: str = ''
    changes: DeploymentChanges = Field(default_factory=DeploymentChanges)
    rollback: str | None = None

class MemoryHit(BaseModel):
    id: str | None = None
    text: str
    score: float | None = None

class JevDecision(BaseModel):
    risk: Risk
    similar_failure: bool
    intervention: Literal['DRIVER_CHECK','MIGRATION_TEST','STAGING_TEST','ROLLBACK_READY','DEPENDENCY_CHECK','CONFIG_REVIEW','NONE','REVIEW']
    confidence: float | None = None
    status: Literal['available','unavailable']

class AnalyzeResponse(BaseModel):
    risk: Risk
    similar_failure: bool
    intervention: str
    confidence: float | None
    reasoning: str
    recommendations: list[str]
    memories: list[MemoryHit]
    decision: JevDecision
    memory_status: Literal['connected','unavailable']
    explanation_status: Literal['generated','unavailable']

class LearnRequest(BaseModel):
    deployment: DeploymentRequest
    status: DeploymentStatus
    root_cause: str = ''
    resolution: str = ''
    impact: str = ''
    downstream_effects: str = ''
    lessons: str = ''
    notes: str = ''

class LearnResponse(BaseModel):
    saved: bool
    memory_status: Literal['connected','unavailable']
    message: str
