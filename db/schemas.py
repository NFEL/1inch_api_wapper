from pydantic import BaseModel
from pydantic.types import Json


class LogSchema(BaseModel):
    data : Json
    
    class Config:
        orm_mode = True
