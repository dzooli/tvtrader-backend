"""Response models and schemas."""

from enum import Enum

from attrs import define, field, validators, asdict
from sanic import json
from sanic_ext import openapi as doc


class ResponseStatus(Enum):
    OK = 0
    SUCCESS = 1
    ERROR = 2
    VALIDATION_ERROR = 3


@define(kw_only=True)
class CommonResponse:
    status: int = field(default=200, validator=[validators.ge(100)])
    message: str = ResponseStatus.OK.name
    description: str = ""

    def json(self):
        return json(asdict(self))


@define
class SuccessResponse(CommonResponse):
    pass


class SuccessResponseSchema:
    description = doc.String(description="Optional response description", nullable=True)
    status = doc.Integer(description="Status code", required=True)
    message = doc.String(description="Response message of the call", nullable=True)

    @classmethod
    def openapi(cls):
        return {
            "status": 200,
            "content": {"application/json": SuccessResponseSchema},
            "description": "Success",
        }


class ErrorResponseSchema:
    description = doc.String(description="Error description", nullable=True)
    status = doc.Integer(description="Status code", required=True)
    message = doc.String(description="Details of the error message", nullable=True)

    @classmethod
    def openapi(cls):
        return {
            "status": 400,
            "content": {"application/json": ErrorResponseSchema},
            "description": "Error. See 'description' property in the response",
        }
