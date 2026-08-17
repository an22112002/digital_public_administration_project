from pydantic import BaseModel

class StartProcessRequest(BaseModel):
    service_id: str

class StartProcessResponse(BaseModel):
    service: dict | None
    documents: list | None
    code: str = "0"
    error: str = ""