#!/usr/bin/env python3
"""
InfluenceFlow API Server
Run script for the FastAPI application
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print("🚀 Starting InfluenceFlow API Server...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔍 Alternative Docs: http://{host}:{port}/redoc")
    print("=" * 50)
    
    # Run the FastAPI application
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )