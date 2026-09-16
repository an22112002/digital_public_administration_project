from pydantic import BaseModel
from typing import Literal

class SetNAPS2PathRequest(BaseModel):
    path: str

class SetTitleRequest(BaseModel):
    title: str

class SetPositionRequest(BaseModel):
    provinceID: str
    communeID: str

class ModeSaveRequest(BaseModel):
    mode: Literal["basic", "server", "client"]
    server_ip: str | None = None