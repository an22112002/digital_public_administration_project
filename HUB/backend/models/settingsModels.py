from pydantic import BaseModel

class SetNAPS2PathRequest(BaseModel):
    path: str

class SetTitleRequest(BaseModel):
    title: str

class SetPositionRequest(BaseModel):
    provinceID: str
    communeID: str