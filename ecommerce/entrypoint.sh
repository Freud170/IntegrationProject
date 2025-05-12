#!/bin/sh
# initialize the database
python -c 'from app.db import init_db; import asyncio; asyncio.run(init_db())'
# start the server, replace shell with uvicorn so it runs as PID 1
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
