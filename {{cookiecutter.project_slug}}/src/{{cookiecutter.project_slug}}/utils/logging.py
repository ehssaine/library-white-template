"""Structured logging bootstrap using ``structlog``."""

from __future__ import annotations

import logging
import sys

import structlog

from {{ cookiecutter.project_slug }}.config.settings import Settings


def setup_logging(settings: Settings | None = None) -> None:
    """Configure ``structlog`` and the stdlib ``logging`` root logger.

    Call this once at application startup::

        from {{ cookiecutter.project_slug }}.utils.logging import setup_logging
        setup_logging()
    """
    _settings = settings or Settings()
    level = getattr(logging, _settings.log_level.upper(), logging.INFO)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )
