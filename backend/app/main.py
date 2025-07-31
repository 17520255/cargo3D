from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import packing

app = FastAPI(title="Cargo Packing API", version="1.0.0")

# CORS middleware để frontend có thể gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Cargo Packing API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include API router
app.include_router(packing.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 