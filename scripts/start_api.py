#!/usr/bin/env python3
"""
Simple script to start the DevDuck API server.
"""

import sys
import os
import uvicorn

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

if __name__ == "__main__":
    # Loopback by default; set DEVDUCK_API_HOST=0.0.0.0 only when the API
    # is intentionally exposed (e.g. behind ngrok for VAPI webhooks).
    host = os.getenv("DEVDUCK_API_HOST", "127.0.0.1")

    print("🦆 Starting DevDuck API server...")
    print("API will be available at: http://localhost:8001")
    print("Press Ctrl+C to stop")

    uvicorn.run(
        "devduck.api.vapi_webhook:app",
        host=host,
        port=8001,
        reload=True,
        log_level="info"
    )
