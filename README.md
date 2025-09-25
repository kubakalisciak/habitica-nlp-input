# habitica-nlp-input
---
A lightweight system to quickly capture natural language (typed or spoken) tasks on a webapp, parse them into structured formats, and automatically add them to Habitica via its API.  
For anyone who wants fast task capture combined with Habitica’s gamified task management.
## Features
- Capture tasks in plain language (e.g., “Finish report tomorrow 5pm, high priority”)  
- Parse input into structured fields (title, due date, difficulty, type)  
- Automatically send tasks to Habitica via API  
- Mobile-friendly quick input 
## Setup
### 1. Clone the repository
```bash
git clone <your-repo-url>
cd habitica-nlp-input
```
### 2. Create a virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate     # Linux/macOS
venv\Scripts\activate        # Windows
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Run the API locally
```bash
uvicorn api:app --reload
```

- Server URL: http://127.0.0.1:8000
- Interactive API docs: http://127.0.0.1:8000/docs
## Roadmap
- [x] Connect to Habitica API
- [x] Add tasks (without NLP)
- [x] Process due dates
- [x] Distinguish between task types
- [x] Process rewards' values
- [x] Process dailies' frequencies
- [x] Process task difficulties
- [x] Refactor request making
- [x] Make a custom API
- [ ] Code the frontend
- [ ] Hook up the backend to the frontend
- [ ] Check for compliance with API usage guidelines
- [ ] Write the documentation
- [ ] Host on my personal server
- [ ] Popularize the project
## License
This project is licensed under the **MIT License**.
