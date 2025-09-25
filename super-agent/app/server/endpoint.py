from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.server.agent_service import Superintendent_Agent
from app.modules.agent.main_graph import ChainManager

agent = Superintendent_Agent()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chain = ChainManager()

async def call_super_graph(query:str)->str:
    """ Calls the full agent """
    response = await chain.call_super_main_graph(query)

    return response

async def call_worker_graph(query:str)->str:
    """ Calls the full agent """
    response = await chain.call_worker_main_graph(query)

    return response

@app.get("/get-super-daily")
async def get_response(query:str = Query(...,description="User query to agent")):
    response = await call_super_graph(query)
    result = {"result": response}
    return result

@app.get("/get-worker-daily")
async def get_response(query:str = Query(...,description="User query to agent")):
    response = await call_worker_graph(query)
    result = {"result": response}
    return result

if __name__ == "__main__":
    uvicorn.run(
        "app.server.endpoint:app",
        host="0.0.0.0",
        port=8001
    )