from typesafe_sdk import Choice, TypeSafeClient
from app.config import Settings
from app.schemas import DeploymentRequest, JevDecision, MemoryHit

class JevService:
    def __init__(self, settings: Settings): self.settings=settings

    def decide(self, deployment: DeploymentRequest, memories: list[MemoryHit]) -> JevDecision:
        if not self.settings.jev_enabled or not self.settings.typesafe_api_key:
            return JevDecision(risk='REVIEW', similar_failure=False, intervention='REVIEW', confidence=None, status='unavailable')
        state={'deployment':deployment.model_dump(),'historical_memories':[{'id':m.id,'text':m.text,'score':m.score} for m in memories]}
        client=TypeSafeClient()
        response=client.system_one(state=state, questions={
            'risk': Choice(instructions='Assess deployment risk using only the supplied deployment state and relevant historical memory. Choose HIGH when similar failures or strong risk signals are present, MEDIUM for meaningful but uncertain risk, LOW when no material risk signal is present, and REVIEW when evidence is insufficient.', criteria={'HIGH':'Strong evidence of a similar prior failure or a high-impact risky change.','MEDIUM':'Some relevant risk evidence exists, but it is not strong enough for HIGH.','LOW':'No material historical or change-specific risk signal is present.','REVIEW':'The evidence is insufficient or conflicting.'}),
            'similar_failure': Choice(instructions='Determine whether the historical memories contain a previous deployment failure that is materially similar to the current deployment.', criteria={'YES':'At least one prior failure is materially similar in technology, change, or failure mechanism.','NO':'No materially similar prior failure is supported by the memories.'}),
            'intervention': Choice(instructions='Choose the single most useful additional check before this deployment, based on the current changes and historical failures.', criteria={'DRIVER_CHECK':'Verify database driver and client compatibility.','MIGRATION_TEST':'Run database migration/upgrade tests.','STAGING_TEST':'Reproduce the deployment in staging before production.','ROLLBACK_READY':'Verify the rollback version and rollback path.','DEPENDENCY_CHECK':'Verify dependency compatibility and lockfile changes.','CONFIG_REVIEW':'Review configuration and environment changes.','NONE':'No additional targeted check is supported by the evidence.','REVIEW':'Evidence is insufficient; require human review.'})}
        )
        risk=response.answers['risk']; similar=response.answers['similar_failure']; intervention=response.answers['intervention']
        def choice(x): return getattr(x,'choice',str(x))
        def confidence(x):
            value=getattr(x,'confidence',None)
            return float(value) if value is not None else None
        cs=[confidence(x) for x in (risk,similar,intervention) if confidence(x) is not None]
        return JevDecision(risk=choice(risk), similar_failure=choice(similar)=='YES', intervention=choice(intervention), confidence=min(cs) if cs else None, status='available')
