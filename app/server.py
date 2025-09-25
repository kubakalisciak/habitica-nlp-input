from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from script import create_task_from_text as add_task  # import your existing function

app = FastAPI(title="Habitica FastAdd API")

# ----------------------------
# POST with JSON body
# ----------------------------
class TaskRequest(BaseModel):
    user_id: str
    api_token: str
    task: str

app.mount("/static", StaticFiles(directory="site/static"), name="static")

# Serve the main HTML page
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("site/index.html") as f:
        return HTMLResponse(f.read())
    

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
