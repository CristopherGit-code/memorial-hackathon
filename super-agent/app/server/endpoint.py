from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.server.agent_service import Superintendent_Agent
from fastapi.responses import JSONResponse

agent = Superintendent_Agent()

app = FastAPI()

origins = [
    "*"
    "http://localhost",         # Local dev
    "http://0.0.0.0",         # Local dev
    "http://127.0.0.1",         # Local dev
    "https://dania-nonoperating-differently.ngrok-free.dev", # Your actual ngrok URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get-daily")
async def get_response(query:str = Query(...,description="User query to agent")):
    response = await agent.generate_daily_report(query)
    result = {"result": response}
    return result

if __name__ == "__main__":
    uvicorn.run(
        "app.server.endpoint:app",
        host="0.0.0.0",
        port=8001
    )