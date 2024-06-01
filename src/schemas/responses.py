"""Response classes and schemas."""

from sanic_ext import openapi as doc
from sanic.response import JSONResponse


class CommonJSONResponse(JSONResponse):
    def __init__(self, message: str | None = None, status: int | None = None):
        super().__init__()
        self.set_body(message or "")
        self.status = status or 200


class ErrorResponse(CommonJSONResponse):
    def __init__(self, message: str | None = None, status: int | None = None):
        super().__init__(message or "Bad Request", status or 400)


class SuccessResponse(CommonJSONResponse):
    def __init__(self, message: str | None = None, status: int | None = None):
        super().__init__(message or "OK", status or 200)


class ErrorResponseSchema:
    description = doc.String(description="Error description", nullable=True)
    status = doc.Integer(description="Status code", required=True)
    message = doc.String(description="Details of the error message", nullable=True)


class SuccessResponseSchema:
    status = doc.Integer(description="Response code", required=True)
    message = doc.String(description="Response message of the call", nullable=True)
