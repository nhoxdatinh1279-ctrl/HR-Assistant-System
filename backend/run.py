#!/usr/bin/env python
import uvicorn
import sys

if __name__ == "__main__":
    print("Starting HR Assistant Backend...")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
