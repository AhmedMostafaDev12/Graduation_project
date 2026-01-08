import sys
import os

# Add project root to Python path
sys.path.insert(0, 'C:/Users/USER/Desktop/Sentry_AI')

# Change to the notebook_library directory
os.chdir(os.path.dirname(__file__))

# Now import and run
import uvicorn

if __name__ == "__main__":
    uvicorn.run("FastAPI_app:app", host="0.0.0.0", port=8001, reload=False)
