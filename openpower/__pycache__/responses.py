from typing import Any, Optional


class Response(object):
	code: int = None
	message: str = None
	expiryMessage: Optional[str] = None
	data: Any = None

	def __init__(self, response):
		self.code = response["code"]
		self.message = response["msg"]
		self.expiryMessage = response["expMsg"]
		self.data = response["data"]


class ListResponse(Response):
	pass

