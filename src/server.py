"""
    Main server process

    File:       server.py
    Author:     Zoltan Fabian <zoltan.dzooli.fabian@gmail.com>
"""

from __future__ import annotations

import socket
import time
from multiprocessing import Queue

import attrs
from sanic import Sanic, Request, SanicException, Websocket
from sanic.log import logger
from sanic.worker.manager import WorkerManager
from sanic_ext import validate, Config, openapi as doc, CountedRequest
from sanic_ext.exceptions import ValidationError
from sanic_ext.extensions.openapi.definitions import RequestBody

import src.actions.carbon as actions_carbon
import src.actions.websocket as actions_ws
from src.app import helpers
from src.app.context import TvTraderContext
from src.config import AppConfig
from src.doc import (
    alert_post_documentation,
    check_get_documentation,
    carbon_post_documentation,
)
from src.schemas.alerts import TradingViewAlert, TradingViewAlertSchema
from src.schemas.responses import (
    SuccessResponseSchema,
    ErrorResponseSchema,
    SuccessResponse,
    CommonResponse,
    ResponseStatus,
)


def create_app() -> Sanic:
    """Create the application instance."""

    ws_clients: set = set()
    carbon_connection = None
    WorkerManager.THRESHOLD = 300

    app_context = TvTraderContext()
    app_context.carbon_sock = carbon_connection
    app = Sanic(
        "TvTrader",
        config=AppConfig(),
        configure_logging=True,
        ctx=app_context,
        request_class=CountedRequest,
    )
    app.extend(config=Config(oas=True, health=True, health_endpoint=True, logging=True))

    try:
        carbon_connection = socket.create_connection(
            (AppConfig.CARBON_HOST, AppConfig.CARBON_PORT)
        )
    except ConnectionRefusedError:
        logger.error("Carbon connection is not available.")

    app.enable_websocket(True)

    @doc.no_autodoc
    @doc.exclude()
    @app.websocket("/wsalerts")
    async def feed(request: Request, ws: Websocket):
        """Websocket endpoint."""
        logger.debug("ws request: %s", str(request))
        ws_clients.add(ws)
        while True:
            data = await ws.recv()
            if data is not None:
                logger.debug("ws data received: %s", str(data))
                await ws.send(data)

    @app.main_process_start
    async def main_process_start(application):
        application.shared_ctx.logger_queue = Queue()

    @app.after_server_stop
    def teardown(application):
        """Application shutdown."""
        logger.debug("Closing the Carbon socket...")
        sock = Sanic.get_app().ctx.carbon_sock
        try:
            del sock
        except (AttributeError, SanicException):
            logger.error("Carbon connection close failed!")

    @app.exception(ValidationError, ValueError)
    def handle_validation_errors(request: Request, exception):
        """Handle validation errors with a proper JSON response."""
        return CommonResponse(
            status=400,
            message=ResponseStatus.VALIDATION_ERROR.name,
            description=str(exception),
        ).json()

    @app.route("/", methods=["GET"])
    @check_get_documentation
    async def check(request: CountedRequest) -> SuccessResponse:
        """Healthcheck endpoint.

        Returns a valid message when the application is working.
        """
        return SuccessResponse(
            description=f"HEALTHY {app.config.APPNAME}",
        ).json()

    @app.route("/alert", methods=["POST"])
    @alert_post_documentation
    @validate(json=TradingViewAlert)
    async def alert_post(
        request: CountedRequest, body: TradingViewAlert
    ) -> SuccessResponse:
        """Alert POST endpoint to receive alerts and forward alerts.

        Receives the alerts for further processing. Every alert will be sent to the connected websocket clients.
        """
        json_data = attrs.asdict(body)
        helpers.add_timezone_info(json_data, Sanic.get_app())
        helpers.format_json_input(json_data)
        await actions_ws.send_metric(json_data, ws_clients)
        return SuccessResponse().json()

    @app.route("/carbon-alert", methods=["POST"])
    @carbon_post_documentation
    # @doc.definition(
    #     tag="Backend",
    # )
    # @doc.body(RequestBody({"application/json": TradingViewAlertSchema}, required=True))
    # @doc.response(200, SuccessResponseSchema, description="Success")
    # @doc.response(
    #     400,
    #     ErrorResponseSchema,
    #     description="Error. See 'description' property in the response",
    # )
    @validate(json=TradingViewAlert)
    async def carbon_alert_post(request: CountedRequest, body: TradingViewAlert):
        """Alert POST endpoint to forward the alerts to a Carbon server."""
        json_data = attrs.asdict(body)
        helpers.add_timezone_info(json_data, Sanic.get_app())
        helpers.format_json_input(json_data)
        # Message meaning conversion to numbers
        config = Sanic.get_app().config
        value = (
            config.CARBON_SELL_VALUE
            if json_data["direction"] == "SELL"
            else config.CARBON_BUY_VALUE
        )
        time_diff = int(time.time()) - (json_data["timestamp"] + json_data["utcoffset"])
        if time_diff > (config.GR_TIMEOUT * 60):
            value = int((config.CARBON_SELL_VALUE + config.CARBON_BUY_VALUE) / 2)
        # Message prepare
        msg = f'strat.{json_data["name"]}.{json_data["interval"]}.{json_data["symbol"]} \
            {value} {json_data["timestamp"]}\n'
        await actions_carbon.send_metric(msg)
        return SuccessResponse().json()

    return app
