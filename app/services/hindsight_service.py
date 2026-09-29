from hindsight_client import Hindsight
from app.config import Settings
from app.schemas import DeploymentRequest, MemoryHit

def _get(obj, name: str, default=None):
    if isinstance(obj, dict): return obj.get(name, default)
    return getattr(obj, name, default)

class HindsightService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = None
        if settings.hindsight_api_key:
            self.client = Hindsight(base_url=settings.hindsight_base_url, api_key=settings.hindsight_api_key)

    def recall_deployment_history(self, deployment: DeploymentRequest, limit: int = 8) -> list[MemoryHit]:
        if not self.client: raise RuntimeError('Hindsight is not configured')
        result = self.client.recall(bank_id=self.settings.hindsight_bank_id, query=self._query(deployment), types=['experience','observation'], budget='mid')
        hits=[]
        for item in (_get(result,'results',[]) or [])[:limit]:
            hits.append(MemoryHit(id=_get(item,'id'), text=_get(item,'text','') or _get(item,'content',''), score=_get(item,'score',None)))
        return hits

    def retain_outcome(self, payload: str, document_id: str | None = None) -> None:
        if not self.client: raise RuntimeError('Hindsight is not configured')
        kwargs={'bank_id':self.settings.hindsight_bank_id,'content':payload}
        if document_id: kwargs['document_id']=document_id
        self.client.retain(**kwargs)

    @staticmethod
    def _query(deployment: DeploymentRequest) -> str:
        c=deployment.changes
        return f'''Deployment to analyze:
Application: {deployment.application}
Version: {deployment.version}
Environment: {deployment.environment}
Description: {deployment.description}
Database: {c.database}
Driver: {c.driver}
Dependencies: {c.dependencies}
Infrastructure: {c.infrastructure}
Configuration: {c.configuration}
API: {c.api}

Find previous deployment experiences, failures, root causes, mitigations, and lessons relevant to these changes. Prioritize similar database, dependency, infrastructure, configuration, or API changes.'''.strip()
