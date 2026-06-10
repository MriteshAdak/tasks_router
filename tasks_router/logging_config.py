"""Application logging configuration."""

from __future__ import annotations

import logging
import os
import threading
from typing import Any

import structlog
from asgi_correlation_id import correlation_id
from fastapi import Request, Response
from starlette.middleware.base import RequestResponseEndpoint

from tasks_router.infrastructure.configurations import settings

CORRELATION_ID_HEADER = "X-Request-ID"

_configure_lock = threading.Lock()
_is_configured = False


def _get_log_level() -> int:
	level_name = os.getenv("LOG_LEVEL", "INFO").upper()
	return logging.getLevelNamesMapping().get(level_name, logging.INFO)


def _use_json_logging() -> bool:
	log_format = os.getenv("LOG_FORMAT", "").lower()
	env = settings.environment.lower()
	return log_format == "json" or env in {"prod", "production", "staging"}


def _build_structlog_processors(
	use_json: bool,
) -> tuple[list[Any], list[Any], Any]:
	timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

	exception_processor = structlog.processors.ExceptionRenderer()

	processors: list[Any] = [
		structlog.contextvars.merge_contextvars,
		structlog.stdlib.add_logger_name,
		structlog.stdlib.add_log_level,
		timestamper,
		structlog.processors.StackInfoRenderer(),
		exception_processor,
		structlog.processors.EventRenamer("message"),
		structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
	]

	foreign_pre_chain: list[Any] = [
		structlog.contextvars.merge_contextvars,
		structlog.stdlib.add_logger_name,
		structlog.stdlib.add_log_level,
		timestamper,
		structlog.processors.StackInfoRenderer(),
		exception_processor,
		structlog.processors.EventRenamer("message"),
	]

	renderer: Any = (
		structlog.processors.JSONRenderer()
		if use_json
		else structlog.dev.ConsoleRenderer()
	)

	return processors, foreign_pre_chain, renderer


def configure_logging() -> None:
	global _is_configured
	with _configure_lock:
		if _is_configured:
			return

		use_json = _use_json_logging()
		processors, foreign_pre_chain, renderer = _build_structlog_processors(use_json)

		structlog.configure(
			processors=processors,
			context_class=dict,
			logger_factory=structlog.stdlib.LoggerFactory(),
			wrapper_class=structlog.stdlib.BoundLogger,
			cache_logger_on_first_use=True,
		)

		handler = logging.StreamHandler()
		handler.setFormatter(
			structlog.stdlib.ProcessorFormatter(
				processor=renderer,
				foreign_pre_chain=foreign_pre_chain,
			)
		)

		root_logger = logging.getLogger()

		for existing_handler in root_logger.handlers:
			existing_handler.close()
		root_logger.handlers = [handler]
		root_logger.setLevel(_get_log_level())

		logging.captureWarnings(True)

		_is_configured = True


async def structlog_bind_middleware(
	request: Request,
	call_next: RequestResponseEndpoint,
) -> Response:
	structlog.contextvars.clear_contextvars()

	# Handle Standard Correlation ID
	cid = correlation_id.get()
	if cid:
		structlog.contextvars.bind_contextvars(correlation_id=cid)

	# Handle AWS Lambda Context if running via Mangum
	lambda_context = request.scope.get("aws.context")
	if lambda_context:
		structlog.contextvars.bind_contextvars(
			aws_request_id=getattr(lambda_context, "aws_request_id", None),
			lambda_function_name=getattr(lambda_context, "function_name", None),
			lambda_function_version=getattr(lambda_context, "function_version", None),
		)

	try:
		return await call_next(request)
	finally:
		structlog.contextvars.clear_contextvars()