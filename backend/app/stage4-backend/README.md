# Stage4 API

This repository contains the Stage4 Teaching Assistant backend service.

## Structure

- `app/main.py`: FastAPI application entrypoint.
- `app/routers/stage4.py`: Defines the `/stage4/process` endpoint.
- `app/services`: Contains analysis, retrieval, and report generation logic.
- `app/models/schema.py`: Pydantic models for request/response validation.
- `app/utils/faiss_helper.py`: FAISS helper for loading the vector index.
- `app/config.py`: Configuration for environment variables and LLM setup.

## Setup

1. Rename `.env.example` to `.env` and add your `OPENAI_API_KEY`.
2. Build and run with Docker:
   ```bash
   docker-compose up --build
   ```
3. Access the API at `http://localhost:8000/stage4/process`.

## Usage

Send a POST request to `/stage4/process` with JSON body:
```json
{
  "Topic": "Your topic",
  "Summary": "Lesson summary",
  "ConversationHistory": [
    {"Speaker": "Teacher", "Text": "..."},
    {"Speaker": "User", "Text": "..."}
  ]
}
```
