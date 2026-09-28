import json
import os
import re
import datetime
import time

from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

HINDSIGHT_URL = os.getenv("HINDSIGHT_URL")
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")

if not HINDSIGHT_URL or not HINDSIGHT_API_KEY:
    raise RuntimeError(
        "HINDSIGHT_URL and HINDSIGHT_API_KEY must be set in .env"
    )

client = Hindsight(
    base_url=HINDSIGHT_URL,
    api_key=HINDSIGHT_API_KEY
)


def _bank(contact_name: str) -> str:
    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        contact_name.lower()
    ).strip("-")

    return f"meeting-prep-{slug}"


def retain(contact_name: str, extracted: dict) -> None:
    today = datetime.date.today().isoformat()

    if "outcome" in extracted:
        content = (
            f"Contact: {contact_name}\n"
            f"Logged on: {today}\n"
            f"Outcome after meeting: {extracted['outcome']}"
        )
    else:
        content = (
            f"Contact: {contact_name}\n"
            f"Logged on: {today}\n"
            f"Meeting information: {json.dumps(extracted)}"
        )

    client.retain(
        bank_id=_bank(contact_name),
        content=content
    )


def recall(contact_name: str) -> str:
    try:
        result = client.recall(
            bank_id=_bank(contact_name),
            query=(
                f"Previous meetings, commitments and sentiment "
                f"for {contact_name}"
            ),
        )

        if result.results:
            return "\n".join(
                memory.text for memory in result.results
            )

        # Give Hindsight a little time if processing is still underway.
        time.sleep(2)

        result = client.recall(
            bank_id=_bank(contact_name),
            query=(
                f"Previous meetings, commitments and sentiment "
                f"for {contact_name}"
            ),
        )

        return "\n".join(
            memory.text for memory in result.results
        )

    except Exception as error:
        status_code = getattr(error, "status_code", None)
        error_text = str(error).lower()

        if (
            status_code == 404
            or "404" in error_text
            or "not found" in error_text
        ):
            return ""

        raise
