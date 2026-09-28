import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

import llm      # noqa: E402  (#3)
import memory   # noqa: E402  (#2)

log = logging.getLogger("meeting-prep")
app = FastAPI(title="Meeting Prep Agent")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MAX_NOTES_CHARS = 20000

NO_HISTORY = {
    "critical_alerts": [],
    "open_commitments": [],
    "sentiment_trend": "no history",
    "landmines": [],
    "suggested_opener": "No history with this contact yet. Start with an open introduction.",
}


class LogMeeting(BaseModel):
    contact_name: str
    notes: str


class PrepMeeting(BaseModel):
    contact_name: str
    memory_on: bool = True


class LogOutcome(BaseModel):
    contact_name: str
    outcome: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/log-meeting")
def log_meeting(req: LogMeeting):
    contact, notes = req.contact_name.strip(), req.notes.strip()
    if not contact:
        raise HTTPException(400, "contact_name is required")
    if not notes:
        raise HTTPException(400, "notes are empty")
    notes = notes[:MAX_NOTES_CHARS]
    try:
        extracted = llm.extract(notes)
    except Exception as e:
        log.exception("extract failed")
        raise HTTPException(502, f"Extraction failed: {e}")
    try:
        memory.retain(contact, extracted)
    except Exception as e:
        log.exception("retain failed")
        raise HTTPException(502, f"Saving to memory failed: {e}")
