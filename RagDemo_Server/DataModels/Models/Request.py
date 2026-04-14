from pydantic import BaseModel, field_validator
from DataModels.Enums.EMode import EMode
from openai.types.chat.completion_create_params import ChatCompletionMessageParam


class Request(BaseModel):
    questions: list[ChatCompletionMessageParam]
    systemMessage: str
    model: str = "gemma4:e4b"
    mode: EMode = EMode.vector
    dataList: list[str | None]
    finalPrompt: str

    @field_validator("dataList")
    @classmethod
    def filter_null_data(cls, v: list[str | None]) -> list[str]:
        return [item for item in v if item is not None]
