from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.schemas import AnalyzeResponse, DeploymentRequest, JevDecision, LearnRequest, LearnResponse
from app.services.explanation_service import ExplanationService
from app.services.hindsight_service import HindsightService
from app.services.jev_service import JevService

settings=get_settings()
app=FastAPI(title='DeployMind API',version='0.1.0')
app.add_middleware(CORSMiddleware,allow_origins=[settings.frontend_origin],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
hindsight=HindsightService(settings)
jev=JevService(settings)
explanation=ExplanationService(settings)

@app.get('/health')
def health():
    return {'ok':True,'hindsight_configured':bool(settings.hindsight_api_key),'jev_configured':bool(settings.typesafe_api_key and settings.jev_enabled),'groq_configured':bool(settings.groq_api_key)}

@app.post('/deployments/analyze',response_model=AnalyzeResponse)
def analyze(deployment: DeploymentRequest):
    try:
        memories=hindsight.recall_deployment_history(deployment); memory_status='connected'
    except Exception:
        memories=[]; memory_status='unavailable'
    try:
        decision=jev.decide(deployment,memories)
    except Exception:
        decision=JevDecision(risk='REVIEW',similar_failure=False,intervention='REVIEW',confidence=None,status='unavailable')
    try:
        reasoning,recommendations=explanation.explain(deployment,decision,memories); explanation_status='generated'
    except Exception:
        reasoning=f'Jev decision: {decision.risk}. Similar historical failure: {decision.similar_failure}. Suggested intervention: {decision.intervention}.'
        recommendations=[decision.intervention.replace('_',' ').title()]; explanation_status='unavailable'
    if decision.risk in {'HIGH','MEDIUM','REVIEW'}: recommendations.append('Keep rollback version ready.')
    recommendations=list(dict.fromkeys(recommendations))[:5]
    return AnalyzeResponse(risk=decision.risk,similar_failure=decision.similar_failure,intervention=decision.intervention,confidence=decision.confidence,reasoning=reasoning,recommendations=recommendations,memories=memories,decision=decision,memory_status=memory_status,explanation_status=explanation_status)

@app.post('/deployments/learn',response_model=LearnResponse)
def learn(request: LearnRequest):
    payload=f'''DEPLOYMENT EXPERIENCE\nApplication: {request.deployment.application}\nVersion: {request.deployment.version}\nEnvironment: {request.deployment.environment}\nDescription: {request.deployment.description}\nChanges: {request.deployment.changes.model_dump()}\nOutcome: {request.status}\nRoot cause: {request.root_cause or 'Not provided'}\nResolution: {request.resolution or 'Not provided'}\nImpact: {request.impact or 'Not provided'}\nDownstream effects: {request.downstream_effects or 'Not provided'}\nLessons learned: {request.lessons or 'Not provided'}\nNotes: {request.notes or 'Not provided'}'''
    try:
        hindsight.retain_outcome(payload,document_id=f'{request.deployment.application}:{request.deployment.version}')
    except Exception as exc:
        return LearnResponse(saved=False,memory_status='unavailable',message=f'Could not save the experience to Hindsight: {exc}')
    return LearnResponse(saved=True,memory_status='connected',message='Deployment experience retained in Hindsight.')
