from pydantic import BaseModel


class MessageModel(BaseModel):
    name: str
    age: int
