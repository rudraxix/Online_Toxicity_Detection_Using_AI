import os
import requests
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

PERSPECTIVE_API_KEY = os.getenv("PERSPECTIVE_API_KEY")
if not PERSPECTIVE_API_KEY:
    print("WARNING: No API key found! Check your .env file")
    raise RuntimeError("Missing Perspective API key!")

PERSPECTIVE_API_URL = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"

# Removed 'severe_toxicity' from the list of valid attributes
MODERATION_ATTRIBUTES = {
    "TOXICITY": {}, "INSULT": {}, "IDENTITY_ATTACK": {}, "PROFANITY": {}, "THREAT": {}, "SEVERE_TOXICITY" : {}
}

class CommentRequest(BaseModel):
    text: str
    threshold: float = 0.75

@app.get("/")
def check_status():
    print("Goodjob checking the status")
    return {"message": "Service is running. Don't worry!"}

@app.post("/analyze")
def analyze_comment(comment: CommentRequest):
    if comment.text.strip() == "":
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    payload = {
        "comment": {"text": comment.text}, "languages": ["en"], "requestedAttributes": MODERATION_ATTRIBUTES
    }

    try:
        response = requests.post(
            PERSPECTIVE_API_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            params={"key": PERSPECTIVE_API_KEY}
        )

        if response.status_code != 200:
            print(f"API ERROR: {response.text}")
            raise HTTPException(status_code=500, detail="Perspective API error.")

        data = response.json()

        scores = {}
        for attr in MODERATION_ATTRIBUTES.keys():
            scores[attr] = data.get("attributeScores", {}).get(attr.upper(), {}).get("summaryScore", {}).get("value", 0)

        flagged = {}
        for attr, score in scores.items():
            if score >= comment.threshold:
                flagged[attr] = score

        return {
            "text": comment.text, "scores": scores, "flagged": flagged, "is_toxic": "toxicity" in flagged
        }

    except requests.exceptions.RequestException as e:
        logging.error("API connection error.")
        raise HTTPException(status_code=500, detail="Failed to analyze comment.")
