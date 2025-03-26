import os
from dotenv import load_dotenv
from fastapi import FastAPI
import requests
from pydantic import BaseModel

app = FastAPI()
load_dotenv(dotenv_path=".env")


PERSPECTIVE_API_KEY = os.getenv("PERSPECTIVE_API_KEY")
print(f"Loaded the API key : {PERSPECTIVE_API_KEY}")

PERSPECTIVE_API_URL = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"

class CommentRequest(BaseModel):
    text : str

@app.get("/")
def read_root():
    return{"message" : "Moderator running status verified"}

@app.post("/analyze")
def analyze_comment(comment: CommentRequest):
    headers = {"Content-Type": "application/json"}
    payload = {
        "comment" : {"text" : comment.text}, "languages" : ["en"], "requestedAttributes" : {"TOXICITY": {}}
    }

    response = requests.post(PERSPECTIVE_API_URL, headers=headers, json= payload, params={"key" : PERSPECTIVE_API_KEY})

    if response.status_code == 200:
        return response.json()
    else :
        return {"error" : "Failed to analyze the comment", "details" : response.text}