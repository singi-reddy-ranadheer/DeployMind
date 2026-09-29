from groq import Groq
from app.config import Settings
from app.schemas import DeploymentRequest, JevDecision, MemoryHit

class ExplanationService:
    def __init__(self, settings: Settings):
        self.settings=settings
        self.client=Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None

    def explain(self, deployment: DeploymentRequest, decision: JevDecision, memories: list[MemoryHit]) -> tuple[str,list[str]]:
        if not self.client: return '', []
        memory_text='\n'.join(f'- {m.id or "memory"}: {m.text}' for m in memories) or '- No relevant historical memory was retrieved.'
        prompt=f'''You are the explanation layer of DeployMind, a DevOps deployment risk assistant.

Current deployment:
{deployment.model_dump_json(indent=2)}

Structured Jev decision:
{decision.model_dump_json(indent=2)}

Relevant Hindsight memories:
{memory_text}

Write a concise explanation for a developer. Explain ONLY what is supported by the deployment data, Jev decision, and memories. Do not invent incidents. Return one short risk explanation paragraph followed by exactly 3-5 actionable recommendations as bullet lines.'''
        response=self.client.chat.completions.create(model=self.settings.groq_model,messages=[{'role':'system','content':'Be precise, evidence-grounded, and concise. Never invent historical incidents.'},{'role':'user','content':prompt}],temperature=0.2,max_tokens=500)
        text=response.choices[0].message.content or ''
        recommendations=[]
        for line in text.splitlines():
            stripped=line.strip()
            if stripped.startswith(('-', '*')): recommendations.append(stripped[1:].strip())
        if not recommendations: recommendations=[decision.intervention.replace('_',' ').title()]
        return text,recommendations[:5]
