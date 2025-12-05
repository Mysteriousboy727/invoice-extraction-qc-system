#!/usr/bin/env python
"""
Simple script to run the FastAPI server.
"""

import sys
import uvicorn

if __name__ == "__main__":
    try:
        uvicorn.run("api.app:app", host="127.0.0.1", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

