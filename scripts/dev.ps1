# Dev server for team-prompt-library
$env:LLM_MODE = "mock"
uvicorn backend.main:app --reload --port 8000
