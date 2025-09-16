from langchain_core.tools import tool

@tool
def get_weather(city:str):
    """ Returns the current weather of the city """