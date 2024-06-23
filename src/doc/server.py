from sanic_ext.extensions.openapi import openapi

from src.schemas import (
    TradingViewAlertSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
)


def _tag_backend(func):
    return openapi.tag("Backend")(func)


def _tag_frontend(func):
    return openapi.tag("Frontend")(func)


def _resp_success(func):
    return openapi.response(**SuccessResponseSchema.openapi())(func)


def _resp_error(func):
    return openapi.response(**ErrorResponseSchema.openapi())(func)


def _body_alert(func):
    return openapi.body(**TradingViewAlertSchema.openapi_in_request())(func)


def alert_post_documentation(func):
    return _tag_frontend(_resp_success(_body_alert(func)))


def check_get_documentation(func):
    return _tag_backend(_resp_success(func))


def carbon_post_documentation(func):
    return check_get_documentation(_body_alert(_resp_error(func)))
