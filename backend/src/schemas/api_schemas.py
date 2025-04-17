from typing import Optional

from pydantic import BaseModel

class AgroRequest(BaseModel):
    id: str
    message: str


class AgroResponse(BaseModel):
    status: str