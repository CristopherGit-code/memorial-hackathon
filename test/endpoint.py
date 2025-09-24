from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get-daily")
async def get_response(query:str = Query(...,description="User query to agent")):
    result = f"Example: {query}"
    return {"result": result}

if __name__ == "__main__":
    uvicorn.run(
        "portal:app",
        host="0.0.0.0",
        port=8001
    )