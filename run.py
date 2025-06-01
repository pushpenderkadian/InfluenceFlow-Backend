#!/usr/bin/env python3
"""
InfluenceFlow API Server
Run script for the FastAPI application and microservices
"""

import os
import sys
import uvicorn
import subprocess
import threading
import time
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def run_microservice(service_name, port, module_path):
    """Run a microservice on a specific port"""
    print(f"🔧 Starting {service_name} on port {port}...")
    try:
        uvicorn.run(
            module_path,
            host="0.0.0.0",
            port=port,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error starting {service_name}: {e}")

def run_consumer(service_name, module_path):
    """Run a consumer script using module path"""
    print(f"🔄 Starting {service_name} consumer...")
    try:
        subprocess.run([sys.executable, "-m", module_path], check=True)
    except Exception as e:
        print(f"❌ Error starting {service_name} consumer: {e}")

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print("🚀 Starting InfluenceFlow Complete System...")
    print(f"📍 Main API: http://{host}:{port}")
    print(f"📍 WhatsApp Business Service: http://{host}:8001")
    print(f"📍 WhatsApp Service Consumer: Background Process")
    print(f"📍 Email Service Consumer: Background Process")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print("=" * 60)
    
    # Start microservices in separate threads
    services = [
        # WhatsApp Business API Service
        threading.Thread(
            target=run_microservice,
            args=("WhatsApp Business", 8001, "micro_services.whatsapp_business.main:app"),
            daemon=True
        ),
        # Email Service Consumer
        threading.Thread(
            target=run_consumer,
            args=("Email Service", "micro_services.emailing_service.consumer"),
            daemon=True
        ),
        # WhatsApp Service Consumer
        threading.Thread(
            target=run_consumer,
            args=("WhatsApp Service", "micro_services.whatsapp_service.consumer"),
            daemon=True
        ),
    ]
    
    # Start all microservices
    for service in services:
        service.start()
        time.sleep(1)  # Small delay between service starts
    
    print("✅ All microservices started successfully!")
    print("🔧 Starting main API server...")
    
    # Run the main FastAPI application
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info" if not debug else "debug"
        )
    except KeyboardInterrupt:
        print("\n🛑 Shutting down all services...")
        sys.exit(0)