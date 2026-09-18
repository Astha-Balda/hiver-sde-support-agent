from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.support_agent import SIMILARITY_THRESHOLD, SupportAgent


app = FastAPI(
    title="Hiver SDE Support Agent",
    description="RAG-based AI customer support API",
    version="1.0.0"
)


# Allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SupportRequest(BaseModel):
    query: str


agent = SupportAgent()


@app.get("/")
def home():
    return {
        "message": "Hiver SDE Support Agent API is running"
    }


@app.post("/support")
def support(request: SupportRequest):

    # Retrieve relevant historical support cases
    results = agent.retriever.search(
        request.query,
        top_k=3
    )

    if not results:
        return {
            "query": request.query,
            "confidence": "LOW",
            "similarity": 0,
            "retrieved_cases": 0,
            "response": "Sorry, I could not find relevant support information."
        }

    best_score = results[0]["similarity"]

    # Generate response using the already retrieved results
    response = agent.generate_response(
        request.query,
        results=results
    )

    confidence = (
        "HIGH"
        if best_score >= SIMILARITY_THRESHOLD
        else "LOW"
    )

    return {
        "query": request.query,
        "confidence": confidence,
        "similarity": round(best_score, 4),
        "retrieved_cases": len(results),
        "response": response
    }
