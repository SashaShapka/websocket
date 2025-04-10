# WebSocket Broadcast Server

A FastAPI-based WebSocket on Windows server supporting both immediate and scheduled broadcasts. Designed to work efficiently in multi-worker setups with Redis for inter-process communication and graceful shutdown handling.

---

## 🚀 Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone <your-repo-url>
   cd websocket
   ```

2. **Install dependencies (preferably in a virtual environment):**

   ```bash
   pip install -r requirements.txt
   ```

3. **Start Redis (required):**

   ```bash
   cd \websocket
   docker-compose up -d
   ```

4. **Run the application:**

   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --workers 3
   ```

---

## 🔪 Testing the WebSocket Endpoint

Testing can be done interactively, or via WebSocket King Client (Chrome Extension)

1. **Run automated tests:**

   ```bash
   pytest unittests/
   ```

   Example test:
   ```bash
   pytest unittests/test_broadcast.py::test_multiple_clients_receive_both_messages
   ```
   **test_redis_brodecast_logs**
      log_redis_broudecast.txt
   **test_redis_shutdown**
      log.txt
   **test_websockets**
      log_test_websocket_1_worker
   **test_shutdown**
      log_shutdown_1_worker

2. **WebSocket King Client (Chrome Extension)**
   
3. Install the extension.
   Enter the URL: ws://localhost:8000/ws
   Click "Connect".
   Send send_now — send:
   "IM sent" - again
   "Scheduled broadcast" - every 10 seconds (if Redis and multiple workers are enabled)

---

## 🧘‍♂️ Graceful Shutdown Logic

This project handles graceful shutdown per **worker process**, ensuring that:

- If a worker receives a termination signal (SIGINT/SIGTERM), it waits up to `TIMEOUT` seconds (default: 60).
- During this time, it checks for active WebSocket connections.
- If there are active connections, the shutdown is delayed until they close or timeout expires.
- If there are no connections, the process exits immediately.

Key components:

- `ConnectionManager`: tracks active WebSocket clients.
- `GracefulShutdown`: hooks into OS signals to trigger shutdown logic per worker.
- `Redis heartbeat`: used to track which workers are still handling clients.

---

## 🔧 Environment Configuration

Set these environment variables in a `.env` file (or via shell):

```env
INTERVAL = 5
TIMEOUT = 1800
REDIS_HOST = 127.0.0.1
REDIS_PORT = 6379
UVICORN_WORKERS = 2
```

---

## 🧠 Notes

- Redis is required for coordinating broadcasts between multiple workers.
- Broadcasting logic ensures a worker doesn't re-send the same message to clients who already received it.
- The test suite includes scenarios to validate both immediate and scheduled broadcasts, as well as shutdown timing.

---
