#!/usr/bin/env python3
"""
Simple script to start the DevDuck API server.
"""

import sys
import os
import uvicorn
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

if __name__ == "__main__":
    # Loopback by default; set DEVDUCK_API_HOST=0.0.0.0 only when the API
    # is intentionally exposed (e.g. behind ngrok for VAPI webhooks).
    host = os.getenv("DEVDUCK_API_HOST", "127.0.0.1")
    port = int(os.getenv("DEVDUCK_API_PORT", "8001"))
    display_host = "localhost" if host == "0.0.0.0" else host

    print("🦆 Starting DevDuck API server...")
    print(f"API will be available at: http://{display_host}:{port}")
    print("Press Ctrl+C to stop")

    uvicorn.run(
        "devduck.api.vapi_webhook:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
