from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from modules.daily_agent import DailyAgent
import uvicorn
import json

app = FastAPI()

# Missing out of test security rules
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = DailyAgent()

async def call_main_graph(query:str)->str:
    """ Calls the complete graph """
    response = await agent.call_agent(query)
    return response

@app.get("/get-response")
async def get_response(query:str = Query(...,description="User query to agent")):
    result = await call_main_graph(query)
    return {"result": result}

if __name__ == "__main__":
    uvicorn.run(
        "modules.server:app",
        host="0.0.0.0",
        port=8001
    )