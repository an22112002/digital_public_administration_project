from pydantic import BaseModel


class SetServiceActiveRequest(BaseModel):
	active: bool