from pydantic import BaseModel, Field


class ServiceImport(BaseModel):
    """
    Dữ liệu của một service được đọc từ file Excel.
    """

    title: str
    realTitle: str
    url: str
    buttonPosition: int = 1
    processes: list[str] = Field(default_factory=list)
    active: bool = True


class DefaultDocumentImport(BaseModel):
    """
    Dữ liệu của một default document được đọc từ file Excel.
    """

    serviceID: int
    name: str
    description: str | None = None
    required: bool = False
    OCRtab: str | None = None


class ExtentionDocumentImport(BaseModel):
    """
    Dữ liệu của một extention document được đọc từ file Excel.
    """

    name: str
    description: str | None = None
    OCRtab: str | None = None