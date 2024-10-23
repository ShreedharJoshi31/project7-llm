# app/main.py

from fastapi import FastAPI
from app.routers import websocket

app = FastAPI()

# Include the WebSocket router
app.include_router(websocket.router)

@app.get("/")
async def root():
    return {"message": "Hello bitches"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
