# Server API

FastAPI backend for resume analysis using Hugging Face models.

## Setup

1. Navigate to server directory:
```bash
cd server
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

4. Run the server:
```bash
python3 -m uvicorn main:app --reload --port 8000
```

**Note:** If you get "command not found" errors:
- Make sure virtual environment is activated (you should see `(venv)` in your prompt)
- Use `python3 -m pip` instead of just `pip`
- Use `python3 -m uvicorn` instead of just `uvicorn`

Or use the start script:
```bash
./start.sh
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `POST /upload-resume` - Extract text from PDF/DOCX resume
- `POST /extract-skills` - Extract skills using NER model
- `POST /analyze-skills` - Analyze skills using sentence transformers

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

