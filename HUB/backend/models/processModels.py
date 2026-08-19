from pydantic import BaseModel
from typing import Literal

class StartProcessResponse(BaseModel):
    service: dict | None
    documents: list[dict] | None
    code: str
    error: str | None

class StartScanRequest(BaseModel):
    scanner: str
    driver: str

class DocumentFile(BaseModel):
    srID: str           # ID của yêu cầu quét, nếu là "ADD:<tên tài liệu>" thì nó là tài liệu bổ sung
    files: list[str]    # path to files

class StartWebViewRequest(BaseModel):
    files: list[DocumentFile]

class WebSocketRequest(BaseModel):
    type: Literal["start_scan", "start_webview", "close"]
    request: StartScanRequest | StartWebViewRequest | None