from pydantic import BaseModel
from DataModels.Enums.EMode import EMode


class Request(BaseModel):
    question: str
    model: str = "llama3"
    mode: EMode = "vector"
