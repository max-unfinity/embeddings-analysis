from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from api import embeddings, images, annotations

app = FastAPI(title="Object Detection Analysis Tool", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(embeddings.router, prefix="/api")
app.include_router(images.router, prefix="/api")
app.include_router(annotations.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Object Detection Analysis Tool API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")