import json
import datetime
import os
import re

from groq import Groq

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MAX_NOTES_CHARS = 12000
MAX_RECALL_CHARS = 12000
RETRIES = 3

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    half = limit // 2
    return text[:half] + "\n...[truncated]...\n" + text[-half:]


def _parse_json(raw: str) -> dict:
    raw = re.sub(r"<think>.*?</think>", "", raw or "", flags=re.DOTALL)
    raw = re.sub(r"```(?:json)?", "", raw).strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object found")
    return json.loads(raw[start:end + 1])


def _call_json(system: str, user: str) -> dict:
    last_err = None
    for _ in range(RETRIES):
        try:
            resp = _get_client().chat.completions.create(
                model=MODEL,
                temperature=0,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
            )
            return _parse_json(resp.choices[0].message.content)
        except Exception as e:  # invalid JSON, API hiccup, etc.
            last_err = e
    raise RuntimeError(f"LLM failed after {RETRIES} attempts: {last_err}")


def _str_list(value) -> list:
    if not isinstance(value, list):
        return []
    return [str(v).strip() for v in value if str(v).strip()]


# ---------- extract ----------

EXTRACT_SYSTEM = """You extract structured data from messy meeting notes.
Return ONLY a JSON object with exactly these keys:
{
  "key_points": [string],
 "commitments": [{"what": string, "due": string, "status": "pending" | "done" | "broken"}],
  "sentiment": integer 1-5 (1 = very negative, 5 = very positive),
  "landmines": [string],
  "competitors": [string]
}
Rules:
- Use ONLY information in the notes. Never invent facts.
- "due" is the deadline as written in the notes, or "" if none given.
- "status" is "pending" by default. Use "done" if the notes say it was completed. Use "broken" if the notes say it was missed, not delivered on time, or cancelled.
- landmines = sensitive topics/objections to handle carefully (e.g. security, pricing).
- competitors = competitor names mentioned.
- Use empty lists when nothing applies. No extra keys, no commentary."""


def _empty_extracted() -> dict:
    return {
        "key_points": [],
        "commitments": [],
        "sentiment": 3,
        "landmines": [],
        "competitors": [],
    }


def extract(notes: str) -> dict:
    if not isinstance(notes, str) or not notes.strip():
        return _empty_extracted()

    notes = _truncate(notes.strip(), MAX_NOTES_CHARS)
    data = _call_json(EXTRACT_SYSTEM, f"Meeting notes:\n{notes}")

    commitments = []
    for c in data.get("commitments", []) or []:
        if isinstance(c, dict) and str(c.get("what", "")).strip():
            status = str(c.get("status", "pending")).lower()
            commitments.append({
                "what": str(c["what"]).strip(),
                "due": str(c.get("due") or "").strip(),
                "status": status if status in ("pending", "done", "broken") else "pending",
            })

    try:
        sentiment = max(1, min(5, int(data.get("sentiment", 3))))
    except (TypeError, ValueError):
        sentiment = 3

    return {
        "key_points": _str_list(data.get("key_points")),
        "commitments": commitments,
        "sentiment": sentiment,
        "landmines": _str_list(data.get("landmines")),
        "competitors": _str_list(data.get("competitors")),
    }


# ---------- brief ----------

BRIEF_SYSTEM = """You prepare a pre-meeting briefing from recalled memory about a contact.
Return ONLY a JSON object with exactly these keys:
{
  "critical_alerts": [string],
  "open_commitments": [string],
  "sentiment_trend": string,
  "landmines": [string],
  "suggested_opener": string
}
Rules:
- Use ONLY the recalled memory provided. Never invent facts, names, dates or commitments.
- critical_alerts = promises not delivered, missed follow-ups, urgent risks.
- open_commitments = commitments still pending.
- If something is not in the memory, leave it empty rather than guessing.
- Use today's date to say how overdue a pending commitment is, but only when a due date is stated in the memory.
- If a commitment was promised more than once, say how many times.
- suggested_opener should address the most important critical alert or landmine first.
- suggested_opener = one short sentence grounded in the memory.
No extra keys, no commentary."""


def _no_history_brief() -> dict:
    return {
        "critical_alerts": [],
        "open_commitments": [],
        "sentiment_trend": "no history",
        "landmines": [],
        "suggested_opener": "No history with this contact yet. Start with open questions about their goals.",
    }


def brief(recalled: str, today=None) -> dict:
    if not isinstance(recalled, str) or not recalled.strip():
        return _no_history_brief()

    recalled = _truncate(recalled.strip(), MAX_RECALL_CHARS)
    today = today or datetime.date.today().isoformat()
    data = _call_json(BRIEF_SYSTEM, f"Today's date: {today}\nRecalled memory:\n{recalled}")

    return {
        "critical_alerts": _str_list(data.get("critical_alerts")),
        "open_commitments": _str_list(data.get("open_commitments")),
        "sentiment_trend": str(data.get("sentiment_trend") or "no history").strip(),
        "landmines": _str_list(data.get("landmines")),
        "suggested_opener": str(data.get("suggested_opener") or "").strip(),
    }


if __name__ == "__main__":
    n = ("Sarah is worried about security. We promised to send the proposal "
         "by Friday. She mentioned Competitor X.")
    print(json.dumps(extract(n), indent=2))
    print(json.dumps(brief("Sarah raised security concerns. Proposal promised, not delivered. Positive after API demo."), indent=2))
    print(json.dumps(brief(""), indent=2))
