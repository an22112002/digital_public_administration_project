from pydantic import BaseModel


class SetServiceActiveRequest(BaseModel):
	active: bool

class SetServiceAllowMutilPushRequest(BaseModel):
	active: bool