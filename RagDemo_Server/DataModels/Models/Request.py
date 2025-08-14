from pydantic import BaseModel
from DataModels.Enums.EMode import EMode


class Request(BaseModel):
    question: str
    systemMessage: str
    model: str = "gemma3n:e4b"
    mode: EMode = EMode.vector
    dataList: list[str]
    finalPrompt: str
