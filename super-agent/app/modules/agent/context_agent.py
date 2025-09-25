from langgraph.checkpoint.memory import MemorySaver
from app.modules.model.oci_openai_client import LLM_Open_Client
import logging
from app.modules.tools.weather import get_alerts, get_forecast
from app.modules.tools.db_tool import get_daily_report_data
from langgraph.prebuilt import create_react_agent
import asyncio
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(name=f"Context_agent.{__name__}")

class ContextAgent:
    """ Agent in charge of give the plan order, recevie the responses and decide which agents to use """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ContextAgent,cls).__new__(cls)
        return cls._instance
    
    SYSTEM_INSTRUCTION = (
        """ 
        You are an agent in charge of helping a superintendent to manage the construction site and generate daily reports

        Your main task is to gather as much information as possible to pass that context to the next agent to build the daily report.

        Focus on generating structured details from the data gathered, pay attention to the details asked by the user and retrieve as much information as possible.

        For the final answer, generate a long detailed text with all the details found, discrepancies accross the different reports, weather, and other data available by sections.
        """
    )

    def __init__(self):
        if not self._initialized:
            self._oci_client = LLM_Open_Client()
            self._model = self._oci_client.build_llm_client()
            self._memory = MemorySaver()
            self._tools = [get_alerts,get_forecast,get_daily_report_data]
            self._context_agent = create_react_agent(
                model=self._model,
                tools=self._tools,
                checkpointer=self._memory,
                prompt=self.SYSTEM_INSTRUCTION
            )
            ContextAgent._initialized = True

    async def call_context_agent(self,state:MessagesState)->MessagesState:        
        user_message = state['messages'][0].content

        query = f"The current user request is: {user_message}, address using the tools and knowledge available, include as much details as possible."

        response = await self._context_agent.ainvoke({"messages": [{"role": "assistant", "content": query}]})
        ans = response['messages'][-1].content
        
        logger.debug(str(ans))
        
        return {"messages": [{"role": "assistant", "content": ans}]}
    
async def main_graph():
    planner = ContextAgent()
    main_graph_builder = StateGraph(MessagesState)

    main_graph_builder.add_node("planner_plan",planner.planner_agent)
    main_graph_builder.add_node("agents", planner.test)
    main_graph_builder.add_node("planner_execute",planner.planner_agent)

    main_graph_builder.add_edge(START,"planner_plan")
    main_graph_builder.add_edge("planner_plan","agents")
    main_graph_builder.add_edge("agents","planner_execute")

    graph = main_graph_builder.compile()

    try:
        user_input = input("USER: ")
        final_response = []
        for chunk in graph.stream( {"messages": [{"role": "user", "content": user_input}],'status':'plan'},
            {'configurable': {'thread_id': "1"}},
            stream_mode="values",
            subgraphs=True
        ):
            try:
                logger.debug("============ Chunk response ==========")
                logger.debug(chunk)
                final_response.append(chunk[-1]['messages'][-1].content)
            except Exception as p:
                final_response.append(f"Error in response: {p}")
        print("\nMODEL RESPONSE")
        print(final_response[-1])
    except Exception as e:
        logger.info(f'General error: {e}')

async def main():
    await main_graph()

if __name__ == "__main__":
    asyncio.run(main())