from pydantic import BaseModel, Field

class ServiceImport(BaseModel):
    """
    Dữ liệu của một service.
    """

    title: str
    realTitle: str
    category: str
    url: str
    buttonPosition: int = 1
    active: bool = True


class ServiceDocumentImport(BaseModel):
    """
    Dữ liệu của một service document.
    """

    serviceID: int
    realTitle: str
    sourceType: str = Field(..., regex="^(SCAN|FORM)$")
    required: bool = False
    formKey: str | None = None


class ScanRequirementImport(BaseModel):
    """
    Dữ liệu của một scan requirement.
    """

    serviceID: int
    code: str
    title: str
    description: str
    required: bool = False
    ocr_enabled: bool = False

class ServiceImportRequest(BaseModel):
    """
    Dữ liệu của một service import request.
    """

    services: ServiceImport
    serviceDocuments: list[ServiceDocumentImport]
    scanRequirements: list[ScanRequirementImport]