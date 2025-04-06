import uvicorn
import sys
import os

# Add the parent directory to the Python path so embedder_service can be found
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)

if __name__ == "__main__":
    uvicorn.run(
        "embedder_service.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
