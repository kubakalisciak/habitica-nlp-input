from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from script import add_task  # import your existing function

app = FastAPI(title="Habitica Task API")

# ----------------------------
# POST with JSON body
# ----------------------------
class TaskRequest(BaseModel):
    user_id: str
    api_token: str
    task: str

@app.post("/add_task")
def create_task(req: TaskRequest):
    """
    Create a Habitica task (POST with JSON body).
    """
    try:
        result = add_task(req.user_id, req.api_token, req.task)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# GET with query params
# ----------------------------
@app.get("/add_task")
def create_task_get(user_id: str, api_token: str, task: str):
    """
    Create a Habitica task (GET with query params).

    Example:
    http://127.0.0.1:8000/add_task?user_id=...&api_token=...&task=...
    """
    try:
        result = add_task(user_id, api_token, task)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))