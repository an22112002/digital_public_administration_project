from fastapi import WebSocket
from pydantic import BaseModel
from typing import Literal
from plugin.WebView.main import DataProcess

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

class ImportFileRequest(BaseModel):
    filename: str
    file: str

class CropImageRequest(BaseModel):
    image: str
    position: list[int] | None  # [x1, y1, x2, y2]

class WebSocketRequest(BaseModel):
    type: Literal["start_scan", "start_webview", "import_file", "crop_image", "close"]
    request: StartScanRequest | StartWebViewRequest | ImportFileRequest | CropImageRequest | None

class UserTask:
    def __init__(self, mode: str, server_ip: str, timestamp: int, websocket: WebSocket, service: dict, required_documents: list[dict]):
        self.mode = mode
        self.server_ip = server_ip
        self.timestamp = timestamp
        self.websocket = websocket
        self.service = service
        self.required_documents = required_documents
        self.need_process = True
        self.data_from_client = None
        self.data_ready_for_web_view = None
        self.url = self.service.get("url", "")

    def set_data_from_client(self, data: StartWebViewRequest) -> None:
        if self.data_from_client != data:
            self.data_from_client = data
            self.need_process = True

    def is_ready_for_web_view(self) -> bool:
        if not self.need_process and self.data_from_client is not None and self.data_ready_for_web_view is not None and self.url is not None:
            return True
        return False

    