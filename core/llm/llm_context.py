from typing import Any, Optional
from dataclasses import dataclass
from contextvars import ContextVar


@dataclass
class LLMContext:
    value: Any


__context: ContextVar[Optional[LLMContext]] = ContextVar("LLM Context", default=None)


def current_context() -> Optional[LLMContext]:
    return __context.get()


def set_context(context: LLMContext):
    __context.set(context)


def reset_context():
    __context.set(None)
