from fastapi import FastAPI
from pydantic import BaseModel

from src.support_agent import SupportAgent


app = FastAPI(
    title="Hiver SDE Support Agent",
    description="RAG-based AI customer support API",
    version="1.0.0"
)


# Request format
class SupportRequest(BaseModel):
    query: str


# Create support agent once when the API starts
agent = SupportAgent()


@app.get("/")
def home():
    return {
        "message": "Hiver SDE Support Agent API is running"
    }


@app.post("/support")
def support(request: SupportRequest):

    results = agent.retriever.search(
        request.query,
        top_k=3
    )

    if not results:
        return {
            "query": request.query,
            "confidence": "LOW",
            "similarity": 0,
            "response": "Sorry, I could not find relevant support information."
        }

    best_score = results[0]["similarity"]

    response = agent.generate_response(
        request.query,
        results=results
    )

    confidence = (
        "HIGH"
        if best_score >= 0.75
        else "LOW"
    )

    return {
        "query": request.query,
        "confidence": confidence,
        "similarity": round(best_score, 4),
        "retrieved_cases": len(results),
        "response": response
    }