from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from util.oci_openai_client import LLM_Open_Client
import logging
import asyncio
import json
from langgraph.graph import MessagesState
from pydantic import BaseModel
from langchain_core.tools import tool
from typing import List,Any

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=f"DAILY_BUILDER.{__name__}")

class DailyAgent:
    """ Agent in charge of helping the superintendent to build the daily report """

    _instance = None
    _initialized = False

    SYSTEM_INSTRUCTION = (
        """
        You are a report assistant, you will receive a text from the user, and you have to format that and convert in a formal languaje format for a business daily report
        """
    )

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DailyAgent,cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._oci_client = LLM_Open_Client()
            self._model = self._oci_client.build_llm_client()
            self._memory = MemorySaver()
            self._tools = []
            self._daily_builder_agent = create_react_agent(
                model=self._model,
                tools=self._tools,
                checkpointer=self._memory,
                prompt=self.SYSTEM_INSTRUCTION,
            )
            DailyAgent._initialized = True
    
    async def call_agent(self,prompt:str):
        query = f"Current user details to build the daily report:{prompt}"
        response = await self._daily_builder_agent.ainvoke({"messages": [{"role": "assistant", "content": query}]},{'configurable': {'thread_id': "1"}})
        ans = response['messages'][-1].content
        logger.debug(str(ans))

        return str(ans)