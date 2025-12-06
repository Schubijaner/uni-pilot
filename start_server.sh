#!/bin/bash
# Start server with auto-reload for development

uvicorn main:app --reload --host 0.0.0.0 --port 8000


