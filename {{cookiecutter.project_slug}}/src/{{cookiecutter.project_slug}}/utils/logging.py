"""Structured logging bootstrap using ``structlog``."""

from __future__ import annotations

import logging
import sys

import structlog


def setup_logging(level: int = logging.INFO) -> None:
    """Configure ``structlog`` and the stdlib ``logging`` root logger.

    Call this once at application startup::

        from {{ cookiecutter.project_slug }}.utils.logging import setup_logging
        setup_logging()
    """

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
