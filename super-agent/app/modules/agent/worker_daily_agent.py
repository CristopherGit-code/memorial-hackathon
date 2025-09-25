import json
from app.modules.model.oci_openai_client import LLM_Open_Client
from app.modules.model.model_with_output import Model_With_Output
import logging
import json
from langgraph.graph import MessagesState

logger = logging.getLogger(name=f"LAYOUT_BUILDER.{__name__}")

class WorkerAgent:
    def __init__(self):
        self.weather_llm = LLM_Open_Client().build_llm_client()
        self.get_schema()
        self.daily_llm = Model_With_Output().bind_output(self.output_schema)

    def get_schema(self):
        with open(r"C:\Users\Cristopher Hdz\Desktop\Test\hackathon\super-agent\app\util\docs\worker_schema.json",'r',encoding='utf-8') as f:
            self.output_schema = json.load(f)

    async def generate_daily_report(self,context:MessagesState)->MessagesState:
        query = context['messages'][-1].content

        logger.debug(query)

        prompt = f"Build a final daily report from a construction site to give the worker in charge of the task. Use the current site context: {query}. If you find any discrepancies accross the data provided, signal them in the space assigned."
        response = await self.daily_llm.ainvoke(prompt)

        logger.debug(response)
        return {"messages": [{"role": "assistant", "content": str(response)}]}