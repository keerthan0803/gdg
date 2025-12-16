# Start FastAPI server with Gmail integration
Write-Host "Starting AI Lead Qualification Agent server..." -ForegroundColor Green
Write-Host "Make sure you're in the backend directory and venv is activated" -ForegroundColor Yellow
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
