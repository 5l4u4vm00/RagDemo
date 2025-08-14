from pydantic import BaseModel
from DataModels.Enum.EMode import EMode


class Request(BaseModel):
    question: str
    model: str = "llama3"
    mode: EMode = 1
