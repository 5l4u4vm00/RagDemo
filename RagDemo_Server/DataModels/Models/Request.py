from pydantic import BaseModel
from DataModels.Enums.EMode import EMode
from openai.types.chat.completion_create_params import ChatCompletionMessageParam


class Request(BaseModel):
    questions: list[ChatCompletionMessageParam]
    systemMessage: str
    model: str = "gemma3n:e4b"
    mode: EMode = EMode.vector
    dataList: list[str]
    finalPrompt: str
