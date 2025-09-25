import asyncio
import logging
from langgraph.graph import StateGraph, START, MessagesState, END
from app.modules.agent.context_agent import ContextAgent
from app.modules.agent.worker_daily_agent import WorkerAgent
from app.modules.agent.super_daily_agent import SuperintendentAgent

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=f"LAYOUT_GRAPH.{__name__}")

class ChainManager:
    """ 
    Class to hold the graph management and calls
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChainManager,cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.context_agent = ContextAgent()
            self.worker_agent = WorkerAgent()
            self.super_agent = SuperintendentAgent()
            self._build_super_chain()
            self._build_worker_chain()
            ChainManager._initialized = True

    def _build_super_chain(self):
        main_graph_builder = StateGraph(MessagesState)

        main_graph_builder.add_node("context",self.context_agent.call_context_agent)
        main_graph_builder.add_node("daily",self.super_agent.generate_daily_report)

        main_graph_builder.add_edge(START,"context")
        main_graph_builder.add_edge("context","daily")
        main_graph_builder.add_edge("daily",END)

        self._super_graph = main_graph_builder.compile()

    def _build_worker_chain(self):
        main_graph_builder = StateGraph(MessagesState)

        main_graph_builder.add_node("context",self.context_agent.call_context_agent)
        main_graph_builder.add_node("daily",self.worker_agent.generate_daily_report)

        main_graph_builder.add_edge(START,"context")
        main_graph_builder.add_edge("context","daily")
        main_graph_builder.add_edge("daily",END)

        self._worker_graph = main_graph_builder.compile()

    async def call_super_main_graph(self, user_input:str):
        try:
            final_response = []
            async for chunk in self._super_graph.astream( {"messages": [{"role": "user", "content": user_input}],'status':'plan'},
                {'configurable': {'thread_id': "1"}},
                stream_mode="values",
                subgraphs=True
            ):
                try:
                    final_response.append(chunk[-1]['messages'][-1].content)
                except Exception as p:
                    final_response.append(f"Error in response: {p}")
            return final_response[-1]
        except Exception as e:
            return f'General error: {e}'
        
    async def call_worker_main_graph(self, user_input:str):
        try:
            final_response = []
            async for chunk in self._worker_graph.astream( {"messages": [{"role": "user", "content": user_input}],'status':'plan'},
                {'configurable': {'thread_id': "1"}},
                stream_mode="values",
                subgraphs=True
            ):
                try:
                    final_response.append(chunk[-1]['messages'][-1].content)
                except Exception as p:
                    final_response.append(f"Error in response: {p}")
            return final_response[-1]
        except Exception as e:
            return f'General error: {e}'

async def main():
    chain = ChainManager()
    response = await chain.call_main_graph("Get the daily for today")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())