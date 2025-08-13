from pydantic import BaseModel


class Option(BaseModel):
    Value: str
    Label: str
