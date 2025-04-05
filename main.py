import os
import requests
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify exact origins for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PERSPECTIVE_API_KEY = os.getenv("PERSPECTIVE_API_KEY")
if not PERSPECTIVE_API_KEY:
    raise RuntimeError("Missing Perspective API key.")

PERSPECTIVE_API_URL = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"

MODERATION_ATTRIBUTES = {
    "TOXICITY": {}, "INSULT": {}, "IDENTITY_ATTACK": {},
    "PROFANITY": {}, "THREAT": {}, "SEVERE_TOXICITY": {}
}

tokenizer = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-sarcasm-twitter")
model = AutoModelForSequenceClassification.from_pretrained("mrm8488/t5-base-finetuned-sarcasm-twitter")

class CommentRequest(BaseModel):
    text: str
    threshold: float = 0.75

@app.get("/")
def check_status():
    return {"message": "Service running."}

@app.post("/analyze")
def analyze_comment(comment: CommentRequest):
    text = comment.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty text.")

    payload = {
        "comment": {"text": text},
        "languages": ["en"],
        "requestedAttributes": MODERATION_ATTRIBUTES
    }

    try:
        response = requests.post(
            PERSPECTIVE_API_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            params={"key": PERSPECTIVE_API_KEY}
        )

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Perspective API error.")

        data = response.json()
        scores = {
            attr: data.get("attributeScores", {}).get(attr.upper(), {}).get("summaryScore", {}).get("value", 0)
            for attr in MODERATION_ATTRIBUTES.keys()
        }
        flagged = {attr: score for attr, score in scores.items() if score >= comment.threshold}

        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            logits = model(**inputs).logits
            probs = F.softmax(logits, dim=1)
            sarcasm_score = probs[0][1].item()
            is_sarcastic = sarcasm_score > 0.5

        return {
            "text": text,
            "scores": scores,
            "flagged": flagged,
            "is_toxic": "TOXICITY" in flagged,
            "is_sarcastic": is_sarcastic,
            "sarcasm_score": round(sarcasm_score, 4)
        }

    except requests.exceptions.RequestException as e:
        logging.error("Perspective API request failed.")
        raise HTTPException(status_code=500, detail="Connection error.")