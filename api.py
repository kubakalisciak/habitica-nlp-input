from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from script import add_task  # import your corrected code

app = FastAPI(title="Habitica NLP Input API")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from script import add_task  # import your corrected code

app = FastAPI(title="Habitica Task API")

@app.post("/add_task")
def create_task(user_id: str, api_token: str, task: str):
    """
    Endpoint to create a task in Habitica.
    Expects query parameters: user_id, api_token, task
    """
    try:
        result = add_task(user_id, api_token, task)
        return result
    except Exception as e:
        # Return HTTP 500 if something goes wrong
        raise HTTPException(status_code=500, detail=str(e))
