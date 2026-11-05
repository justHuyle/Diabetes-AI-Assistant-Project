# Entrypoint cho Hugging Face Spaces (SDK: Gradio / Python)
import os
import uvicorn
from backend.app.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"Starting Diabetes AI Assistant FastAPI on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
