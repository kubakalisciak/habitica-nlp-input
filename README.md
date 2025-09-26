Here’s the full README in clean Markdown, ready to use:

# habitica-fastadd
A lightweight FastAPI service to quickly convert natural language tasks into Habitica tasks. Perfect for fast task capture using mobile automations or scripts, leveraging Habitica’s gamified task management.

---
## Features
- Parse natural language tasks (e.g., “Water plants every morning at 8am”)
- Automatically detect recurring schedules and due dates
- Send tasks directly to Habitica via its API
- Minimal, RESTful API suitable for mobile automations

---
## API Endpoints

### **GET /status**
Check if Habitica API is reachable.

**Response:**
```json
{
  "isUp": true
}
````

**Errors:**

- `503 Service Unavailable` if Habitica API is unreachable.

---
### **POST /add-task**

Create a Habitica task from natural language.

**Request JSON:**

```json
{
  "user_id": "your-habitica-user-id",
  "api_token": "your-habitica-api-token",
  "text": "Drink water every morning at 8am"
}
```

**Response JSON (success):**

```json
{
  "success": true,
  "task": {
    "id": "abc123",
    "type": "habit",
    "text": "Drink water",
    "repeat": {...},
    "dueDate": "2025-09-27T08:00:00.000Z"
  }
}
```

**Errors:**

- `400 Bad Request` if Habitica rejects the task
    
- `500 Internal Server Error` for unexpected errors
    

---

## Deployment

### 1. Clone the repository

```bash
git clone git@github.com:kubakalisciak/habitica-fastadd.git
cd habitica-fastadd
```

### 2. Set up the virtual environment

```bash
python -m venv venv
```

Activate the virtual environment:

- **macOS/Linux:** `source venv/bin/activate`
    
- **Windows (Command Prompt):** `venv\Scripts\activate`
    
- **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
    

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the API

```bash
uvicorn app:app --reload
```

The API will be available at `http://127.0.0.1:8000`.  
Swagger docs are available at `http://127.0.0.1:8000/docs`.

---

## Usage Example

Using `curl`:

```bash
curl -X POST http://127.0.0.1:8000/add-task \
     -H "Content-Type: application/json" \
     -d '{"user_id": "your-id", "api_token": "your-token", "text": "Drink water every morning"}'
```

---

## User Interfaces


- No official frontend is provided.
- Mobile automation tools like **MacroDroid** can easily POST tasks to this API (see my tutorial on [how to set it up](macrodroid.md))
    

---

## Contributing

1. Fork the repository
    
2. Create a feature branch (`git checkout -b feature/your-feature`)
    
3. Commit your changes (`git commit -m 'Add some feature'`)
    
4. Push to the branch (`git push origin feature/your-feature`)
    
5. Open a pull request
    

---

## License

This project is licensed under the [MIT License](LICENSE)