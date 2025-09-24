from typing import Any
import httpx
from langchain_core.tools import tool
from app.modules.db.db import DataBase
from app.util.config.config import Settings

settings = Settings(r'C:\Users\Cristopher Hdz\Desktop\Test\hackathon\test\util\config\config.yaml')
db = DataBase(settings)

@tool
def get_daily_report_data():
    """ Function to retrieve the current daily information from DB"""
    query = """ SELECT * FROM WORKER_DATA """
    responses = db._sort_files(query)
    return responses