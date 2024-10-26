# app/models/request_model.py

from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str