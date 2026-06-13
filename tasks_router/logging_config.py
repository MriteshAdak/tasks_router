"""Application logging configuration."""

from __future__ import annotations

import logging
import os
import threading
from typing import Any, Callable

import structlog
from asgi_correlation_id.context import correlation_id
from fastapi import Request, Response
from starlette.middleware.base import RequestResponseEndpoint

CORRELATION_ID_HEADER = "X-Request-ID"

_configure_lock = threading.Lock()


def _get_log_level() -> int:
	"""Get the configured log level from the environment.

	Returns:
		int: Numeric logging level corresponding to LOG_LEVEL, defaulting to INFO.
	"""
	level_name = os.getenv("LOG_LEVEL", "INFO").upper()
	return logging._nameToLevel.get(level_name, logging.INFO)


def _use_json_logging() -> bool:
	"""Determine whether structured JSON logging should be enabled.

	Returns:
		bool: True when LOG_FORMAT=json or the environment indicates production/staging.
	"""
	log_format = os.getenv("LOG_FORMAT", "").lower()
	env = os.getenv("ENV", "").lower()
	return log_format == "json" or env in {"prod", "production", "staging"}


def _build_structlog_processors(
	use_json: bool,
) -> tuple[list[Any], list[Any], Any]:
	"""Build structlog processor chains for the application logger.

	Args:
		use_json (bool): Whether JSON log rendering should be used.

	Returns:
		tuple[list[Any], list[Any], Any]: A tuple containing the processor chain, foreign pre-chain, and renderer.
	"""
	timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

	exception_processor = structlog.processors.ExceptionRenderer()

	def add_correlation_id(
		_: Any,
		__: str,
		event_dict: dict[str, Any],
	) -> dict[str, Any]:
		"""Add a correlation ID to structured log events when available."""
		if "correlation_id" not in event_dict:
			cid = correlation_id.get()
			if cid:
				event_dict["correlation_id"] = cid
		return event_dict

	processors: list[Any] = [
		structlog.contextvars.merge_contextvars,
		add_correlation_id,
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
		add_correlation_id,
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
	"""Configure structlog and standard logging for the application.

	This function is idempotent and can be called multiple times without reconfiguring logging.
	"""
	with _configure_lock:
		if getattr(configure_logging, "_configured", False):
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

		for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
			logger = logging.getLogger(logger_name)
			logger.handlers.clear()
			logger.propagate = True
			logger.setLevel(root_logger.level)

		logging.captureWarnings(True)

		configure_logging._configured = True


async def bind_contextvars_middleware(
	request: Request,
	call_next: RequestResponseEndpoint,
) -> Response:
	"""Bind request correlation ID to context variables for each HTTP request.

	Args:
		request (Request): Incoming HTTP request.
		call_next (RequestResponseEndpoint): Next ASGI request handler.

	Returns:
		Response: The HTTP response returned by the downstream handler.
	"""
	cid = correlation_id.get()
	structlog.contextvars.clear_contextvars()
	if cid:
		structlog.contextvars.bind_contextvars(correlation_id=cid)

	try:
		response = await call_next(request)
	except Exception:
		structlog.get_logger("app.error").exception("Unhandled exception")
		raise
	else:
		if cid:
			response.headers[CORRELATION_ID_HEADER] = cid
		return response
	finally:
		structlog.contextvars.clear_contextvars()