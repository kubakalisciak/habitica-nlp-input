# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from script import add_task  # import your corrected code

app = FastAPI(title="Habitica Task API")


# Define the structure of the POST request
class TaskRequest(BaseModel):
    user_id: str
    api_token: str
    task: str


@app.post("/add_task")
def create_task(req: TaskRequest):
    """
    Endpoint to create a task in Habitica.
    Expects JSON: { "user_id": "...", "api_token": "...", "task": "..." }
    """
    try:
        result = add_task(req.user_id, req.api_token, req.task)
        return result
    except Exception as e:
        # Return HTTP 500 if something goes wrong
        raise HTTPException(status_code=500, detail=str(e))
