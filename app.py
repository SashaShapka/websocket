import os
import uvicorn
from core.broadcast_strategy import context
from core.shutdown import GracefulShutdown
from logger import setup_logging
from fastapi import FastAPI
from router.registry_rout import add_api_websocket_rout
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
add_api_websocket_rout(app)

workers = int(os.getenv("UVICORN_WORKERS", 1))

@app.on_event("startup")
async def on_startup():
    setup_logging()
    context.start()
    shutdown_handler = GracefulShutdown()

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, workers=workers)