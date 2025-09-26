from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Header, HTTPException
import uvicorn, ast
from app.server.agent_service import Superintendent_Agent
from app.modules.agent.main_graph import ChainManager
import os

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
API_KEY = os.environ.get("ENDPOINT_API_KEY")

async def call_super_graph(query:str)->str:
    """ Calls the full agent """
    response = await chain.call_super_main_graph(query)

    return response

async def call_worker_graph(query:str)->str:
    """ Calls the full agent """
    response = await chain.call_worker_main_graph(query)

    return response

@app.get("/get-super-daily")
async def get_response(query: str, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    response = await call_super_graph(query)
    python_obj = ast.literal_eval(response)
    return {"result": python_obj}

@app.get("/get-worker-daily")
async def get_response(query: str, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    response = await call_worker_graph(query)
    python_obj = ast.literal_eval(response)
    return {"result": python_obj}

if __name__ == "__main__":
    uvicorn.run(
        "app.server.endpoint:app",
        host="0.0.0.0",
        port=8001
    )