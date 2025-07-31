import uvicorn
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backend.log')
    ]
)

if __name__ == "__main__":
    print("🚀 Starting Cargo Packing API Server...")
    print("📝 Logs will be saved to 'backend.log'")
    print("🌐 Server will run on http://localhost:8000")
    print("📊 API docs available at http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 