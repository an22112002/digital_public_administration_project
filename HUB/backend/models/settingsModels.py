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

class SetLLMSettingRequest(BaseModel):
    model: str
    gpu_use: float
    context_length: int

class SetUIUserRequest(BaseModel):
    ui: Literal["desktop", "kiosk"]