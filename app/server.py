from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware  # FIXED IMPORT
from script import create_task_from_text as add_task  # your existing function

app = FastAPI(title="Habitica FastAdd API")

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="super-secret-key")

# Mount static files
app.mount("/static", StaticFiles(directory="../site/static"), name="static")

# Serve index.html
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("../site/index.html") as f:
        return HTMLResponse(f.read())

# Login endpoint
class LoginRequest(BaseModel):
    user_id: str
    api_token: str

@app.post("/login")
async def login(req: LoginRequest, request: Request):
    request.session['user_id'] = req.user_id
    request.session['api_token'] = req.api_token
    return JSONResponse({"message": "Logged in"})

# Add task endpoint
@app.post("/add_task")
async def create_task(request: Request, task: str):
    user_id = request.session.get("user_id")
    api_token = request.session.get("api_token")
    if not user_id or not api_token:
        raise HTTPException(status_code=401, detail="Not logged in")

    try:
        result = add_task(user_id, api_token, task)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
