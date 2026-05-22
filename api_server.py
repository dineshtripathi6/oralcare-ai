from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ✅ INIT
app = FastAPI(title="OralCare AI API")

# ✅ ADD CORS (CRITICAL FIX)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (for dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    text: str

# -------------------------------
# KNOWLEDGE BASE
# -------------------------------
knowledge = [
    "White patch in mouth may indicate leukoplakia.",
    "Persistent ulcers can indicate oral cancer.",
    "Smoking increases oral cancer risk.",
    "Difficulty swallowing may indicate serious condition."
]

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
knowledge_vectors = embed_model.encode(knowledge)

def rag(query):
    q_vec = embed_model.encode([query])
    sim = cosine_similarity(q_vec, knowledge_vectors)[0]
    idx = sim.argsort()[-1]
    return knowledge[idx]

def tools(query):
    q = query.lower()

    if "white patch" in q:
        return "Possible leukoplakia", "moderate"

    if "ulcer" in q:
        return "Possible oral lesion", "high"

    if "pain" in q:
        return "Possible condition", "moderate"

    return "General oral condition", "low"

# -------------------------------
# API
# -------------------------------
@app.post("/predict")
def predict(q: Query):

    insight = rag(q.text)
    condition, severity = tools(q.text)

    return {
        "condition": condition,
        "severity": severity,
        "insight": insight,
        "recommendation": "Consult a healthcare professional"
    }
