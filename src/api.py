import os
from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.support_agent import SIMILARITY_THRESHOLD, SupportAgent


app = FastAPI(
    title="Hiver SDE Support Agent",
    description="RAG-based AI customer support API",
    version="1.0.0"
)


def get_allowed_origins():
    default_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    configured_origins = os.getenv("ALLOWED_ORIGINS", "")
    production_origins = [
        origin.strip()
        for origin in configured_origins.split(",")
        if origin.strip()
    ]

    return default_origins + production_origins


# Allow requests from the React frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SupportRequest(BaseModel):
    query: str


@lru_cache(maxsize=1)
def get_agent():
    return SupportAgent()


@app.get("/")
@app.get("/api")
def home():
    return {
        "message": "Hiver SDE Support Agent API is running"
    }


@app.post("/support")
@app.post("/api/support")
def support(request: SupportRequest):
    try:
        agent = get_agent()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Support agent is not ready: {exc}",
        ) from exc

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
