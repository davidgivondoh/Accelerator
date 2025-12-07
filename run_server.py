"""
Growth Engine Server Runner
===========================

Simple script to run the API server on localhost:3000
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Givondo Growth Engine API...")
    print("📍 Server: http://localhost:3000")
    print("📚 Docs: http://localhost:3000/docs")
    print("📖 ReDoc: http://localhost:3000/redoc")
    print("-" * 50)
    
    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        log_level="info"
    )
