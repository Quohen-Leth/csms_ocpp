from pydantic import BaseModel


class MinModel(BaseModel):
    cp_id: str
