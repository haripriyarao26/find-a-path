# Server API

FastAPI backend for resume analysis using Hugging Face Inference API (no local models needed - much faster!).

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
- `POST /extract-skills` - Extract skills using Hugging Face NER API
- `POST /analyze-skills` - Analyze skills using Hugging Face embedding API

## Hugging Face API Token

The API works without a token, but **using a token gives you better rate limits and faster responses**.

### Setting the Token (Recommended - Using .env file):

1. Get a free token from: https://huggingface.co/settings/tokens

2. Create a `.env` file in the `server/` directory:
```bash
cd server
touch .env
```

3. Add your token to the `.env` file:
```
HUGGINGFACE_API_TOKEN=your_token_here
```

4. **Verify it's loaded:** When you start the server, you should see:
   - ✅ `Hugging Face API token loaded successfully` (if token is set)
   - ⚠️  `No Hugging Face API token found` (if not set)

### Alternative: Environment Variable

You can also set it as an environment variable:

**macOS/Linux:**
```bash
export HUGGINGFACE_API_TOKEN=your_token_here
```

**Windows:**
```bash
set HUGGINGFACE_API_TOKEN=your_token_here
```

**Note:** The `.env` file method is recommended as it's easier to manage and doesn't require setting it each time you open a new terminal.

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

