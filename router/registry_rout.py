from fastapi import FastAPI
from socket_service.endpoints import websocket_endpoint

def add_api_websocket_rout(app: FastAPI):
    app.add_api_websocket_route("/ws", websocket_endpoint)