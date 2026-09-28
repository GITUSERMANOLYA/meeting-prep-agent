# Meeting-prep-agent

## An AI-powered meeting assistant that helps you prepare for client conversations by turning meeting notes into structured information and using persistent memory to create pre-meeting briefings.

## Overview

Important details from a client conversation are easy to forget: what they promised, what you promised, what is still pending, and which topics need careful handling.

Meeting Prep Agent is designed to help with that. You can:

- Save meeting notes for a contact.
- Extract key points, commitments, sentiment, and topics to avoid.
- Store meeting information in Hindsight memory.
- Generate a briefing before your next meeting.
- Record meeting outcomes to help build a longer-term history.

The app includes a Hindsight Memory ON/OFF option for the preparation flow.

## Features

- **Log a meeting:** Enter a contact name and meeting notes.
- **Structured extraction:** Uses an LLM to identify key points, commitments, sentiment, and sensitive topics.
- **Persistent memory:** Uses Hindsight to retain and recall information associated with a contact.
- **Pre-meeting briefing:** Generates a briefing with:
  - Critical Alerts
  - Broken Commitments
  - Sentiment Trend
  - Topics to Avoid
  - Suggested Opener
- **Memory toggle:** Choose whether the preparation request uses previous meeting history.
- **Record meeting outcome:** Save follow-up notes after a meeting.

> **Note:** This is an actively developed prototype. Memory recall, outcome reflection, and commitment-status behavior are still being tested.
> ## Tech Stack

- **Backend:** Python, FastAPI
- **Frontend:** HTML, CSS, JavaScript
- **LLM:** Groq
- **Memory:** Hindsight
- **Local development server:** Uvicorn

## Project Structure

```text
meeting-prep-agent/
│
├── backend/
│   ├── main.py       # FastAPI application and API endpoints
│   ├── llm.py        # LLM extraction and briefing generation
│   └── memory.py     # Hindsight memory operations
│
├── frontend/
│   └── index.html    # Web application interface
│
├── .env              # API credentials (keep private)
├── requirements.txt  # Python dependencies
└── README.md
```

## Prerequisites

Before running the project, make sure you have:

- **Python** installed
- **Git** installed (if cloning the repository)
- **Groq API credentials**
- **Hindsight API credentials**
- **VS Code** or another code editor

## Installation and Setup

### 1. Clone or Download the Repository

To clone the repository:

```bash
git clone <repository-url>
cd meeting-prep-agent
```

Alternatively, download the project as a ZIP file, extract it, and open the project folder in VS Code.

### 2. Create a Virtual Environment

From the project root directory, run:

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

Install the Python packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root directory.

Add the environment variables required by the backend, using the variable names expected in `backend/llm.py` and `backend/memory.py`.

Keep your API credentials private. Do not commit the `.env` file to GitHub or share it publicly.

## Running the Application

### 1. Start the Backend Server

From the project root directory, run:

```bash
uvicorn backend.main:app --reload
```

The FastAPI backend will be available at:

```text
http://127.0.0.1:8000
```

### 2. Open the Frontend

Open the following file in your browser:

```text
frontend/index.html
```

Keep the backend server running while using the frontend.

### 3. Check the Backend

To check whether the backend is running, visit:

```text
http://127.0.0.1:8000/health
```

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Checks whether the backend is running |
| `POST` | `/log-meeting` | Extracts and stores information from meeting notes |
| `POST` | `/prep-meeting` | Generates a pre-meeting briefing using available memory |
| `POST` | `/log-outcome` | Records the outcome of a meeting |

## Unique Selling Point (USP)

Meeting Prep Agent focuses on **continuity between meetings**, rather than only summarizing individual conversations.

It connects meeting notes, commitments, outcomes, and contact-based memory to help users carry important context from one conversation into the next.

## Future Improvements

- Improve commitment-status tracking across meetings.
- Ensure recorded outcomes are reflected in future briefings.
- Improve grounding so generated details are supported by saved meeting information.
- Add more tests for memory recall and separation between contacts.
- Strengthen error handling and data privacy controls.

## Security Note

This project is an actively developed prototype that uses external AI and memory services.

Avoid entering confidential or sensitive meeting information unless appropriate consent and data-handling arrangements are in place.

Never commit API keys, passwords, or `.env` files to version control.
