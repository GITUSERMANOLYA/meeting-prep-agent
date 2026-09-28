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

GENERIC = {
    "critical_alerts": [],
    "open_commitments": [],
    "sentiment_trend": "unknown (memory off)",
    "landmines": [],
    "suggested_opener": "Thanks for making time today. What are your top priorities for this call?",
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
    return {"status": "saved", "extracted": extracted}


@app.post("/prep-meeting")
def prep_meeting(req: PrepMeeting):
    contact = req.contact_name.strip()
    if not contact:
        raise HTTPException(400, "contact_name is required")
    try:
        if not req.memory_on:
            return GENERIC  # memory OFF: generic briefing, no recall or LLM call
        recalled = memory.recall(contact)
        if not recalled or not recalled.strip():
            return NO_HISTORY  # F8: never let the LLM guess
        return llm.brief(recalled)
    except Exception as e:
        log.exception("prep failed")
        raise HTTPException(502, f"Briefing failed: {e}")


@app.post("/log-outcome")
def log_outcome(req: LogOutcome):
    contact, outcome = req.contact_name.strip(), req.outcome.strip()
    if not contact or not outcome:
        raise HTTPException(400, "contact_name and outcome are required")
    try:
        memory.retain(contact, {"outcome": outcome})
    except Exception as e:
        log.exception("log-outcome failed")
        raise HTTPException(502, f"Saving outcome failed: {e}")
    return {"status": "saved"}
