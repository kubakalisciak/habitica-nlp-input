from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import datetime
import re
from dateparser.search import search_dates
from recurrent import RecurringEvent
from dateutil.rrule import DAILY, WEEKLY, MONTHLY
from script import _build_task_from_text, _send_task_to_habitica, _check_habitica_connection
# -----------------------------------------------------------------------------
# FASTAPI APP
# -----------------------------------------------------------------------------

app = FastAPI(title="Habitica NLP Task API",
              description="Convert natural language into Habitica tasks",
              version="1.0.0")

class TaskRequest(BaseModel):
    user_id: str
    api_token: str
    text: str

@app.get("/status")
def status():
    """Check if Habitica API is up."""
    if _check_habitica_connection():
        return {"isUp": True}
    else:
        raise HTTPException(status_code=503, detail="Habitica API unavailable")

@app.post("/add_task")
def create_task(req: TaskRequest):
    """Create a Habitica task from natural language."""
    if not _check_habitica_connection():
        raise HTTPException(status_code=503, detail="Habitica API unavailable")

    try:
        task_data = _build_task_from_text(req.text)
        result = _send_task_to_habitica(req.user_id, req.api_token, task_data)

        if result["success"]:
            return {"success": True, "task": result["data"]["data"]}
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
