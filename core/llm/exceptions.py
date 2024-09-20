from typing import Union


class LLMProviderException(Exception):
    """Raise when there is an error caused by the LLM provider."""

    def __init__(self, error_code: Union[str, int], error_msg: str):
        self.error_code = error_code
        self.error_msg = error_msg
        super().__init__(error_msg)


class LLMHandlerException(Exception):
    """Raise when there is an error caused by the LLM flow."""
