import json
from langgraph.checkpoint.memory import MemorySaver
from app.modules.model.oci_openai_client import LLM_Open_Client
import logging
import json
from app.modules.tools.weather import get_alerts
from app.modules.tools.db_tool import get_daily_report_data
from langgraph.prebuilt import create_react_agent

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=f"LAYOUT_BUILDER.{__name__}")

class HelperOpenAI:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HelperOpenAI,cls).__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        if self._initialized:
            return
        self.openai_module = LLM_Open_Client()
        self._initialized = True

    def bind_output(self,schema):
        model = self.openai_module.build_llm_client()
        output_model = model.with_structured_output(schema)
        return output_model
    
class Superintendent_Agent:
    def __init__(self):
        self.weather_llm = LLM_Open_Client().build_llm_client()
        self.agent = create_react_agent(
            model=self.weather_llm,
            tools=[get_alerts,get_daily_report_data]
        )
        self.get_schema()
        self.main_llm = HelperOpenAI().bind_output(self.output_schema)

    def get_weather_response(self):
        weather_response = self.agent.invoke({"messages": [{"role": "assistant", "content": "Get the current weather alerts in SF"}]})
        logger.debug(weather_response)
        return weather_response
    
    def get_daily_db_reports(self):
        daily_response = self.agent.invoke({"messages": [{"role": "assistant", "content": "Get the current daily reports from the DB"}]})
        logger.debug(daily_response)
        return daily_response

    def get_schema(self):
        with open(r"C:\Users\Cristopher Hdz\Desktop\Test\hackathon\test\util\docs\schema.json",'r',encoding='utf-8') as f:
            self.output_schema = json.load(f)

    async def generate_daily_report(self,query:str):
        daily_response = self.get_daily_db_reports()
        weather_response = self.get_weather_response()
        prompt = f"Build a final daily report from a construction site to give the superintendent in charge of the duty. Use the worker information: {daily_response}, suppose you found some discrepancies across reports. Take into consideration weather conditions {weather_response}"
        response = await self.main_llm.ainvoke(prompt)
        return response