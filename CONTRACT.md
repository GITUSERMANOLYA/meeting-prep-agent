# API Contract (do not change without telling the team)

## POST /log-meeting
Request: { "contact_name": str, "notes": str }
Response: { "status": "saved", "extracted": Extracted }

## POST /prep-meeting
Request: { "contact_name": str, "memory_on": bool }
Response: {
  "critical_alerts": [str],
  "open_commitments": [str],
  "sentiment_trend": str,
  "landmines": [str],
  "suggested_opener": str
}

## POST /log-outcome
Request: { "contact_name": str, "outcome": str }
Response: { "status": "saved" }

## Extracted shape
{
  "key_points": [str],
  "commitments": [{ "what": str, "due": str, "status": "pending|done|broken" }],
  "sentiment": int (1-5),
  "landmines": [str],
  "competitors": [str]
}

## Function signatures
memory.retain(contact_name: str, extracted: dict) -> None
memory.recall(contact_name: str) -> str   # "" if no history
llm.extract(notes: str) -> dict           # returns Extracted
llm.brief(recalled: str) -> dict          # returns prep-meeting response
