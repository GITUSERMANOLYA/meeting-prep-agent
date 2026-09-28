import json
from pathlib import Path

import requests


API_URL = "http://localhost:8000/log-meeting"


def load_seed_data():
    data_file = Path(__file__).parent / "seed_data.json"

    with open(data_file, "r", encoding="utf-8") as file:
        return json.load(file)


def seed():
    meetings = load_seed_data()

    print(f"Loading {len(meetings)} meetings...")

    successful = 0

    for i, meeting in enumerate(meetings, start=1):
        try:
            response = requests.post(
                API_URL,
                json=meeting,
                timeout=30,
            )

            response.raise_for_status()

            print(
                f"[{i}/{len(meetings)}] "
                f"Saved meeting for {meeting['contact_name']}"
            )

            successful += 1

        except requests.RequestException as error:
            print(
                f"[{i}/{len(meetings)}] "
                f"FAILED for {meeting['contact_name']}: {error}"
            )

    print()
    print(f"Seed complete: {successful}/{len(meetings)} meetings loaded.")


if __name__ == "__main__":
    seed()
