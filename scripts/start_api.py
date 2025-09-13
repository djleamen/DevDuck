#!/usr/bin/env python3
"""
Simple script to start the DevDuck API server.
"""

import sys
import os
import uvicorn

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

if __name__ == "__main__":
    print("🦆 Starting DevDuck API server...")
    print("API will be available at: http://localhost:8001")
    print("Press Ctrl+C to stop")

    uvicorn.run(
        "devduck.api.vapi_webhook:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
