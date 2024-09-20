import base64
import logging

from typing import Optional
from ..schemas import LLMProvider, OpenAIConfig
from .base import BaseCompletion

logger = logging.getLogger(__name__)

API_BASE = "https://api.openai.com/v1/chat/completions"


class OpenAIParamsBuilder:
    DEFAULT_PARAMS = {
        "max_tokens": 4096,
        "temperature": 0,
    }

    def build_params(
        self,
        prompt: str,
        screenshot: Optional[bytes] = None,
        response_format: Optional[dict] = None,
        **kwargs
    ):
        messages = []
        text_message = {"type": "text", "text": prompt}
        messages.append(text_message)
        if screenshot:
            b64_image = base64.b64encode(screenshot).decode("utf-8")
            image_message = {
                "type": "image_url",
                "image_url": {"url": "data:image/png;base64,{}".format(b64_image)},
            }
            messages.append(image_message)

        params = {"messages": [{"role": "user", "content": messages}]}
        if response_format:
            params["response_format"] = response_format
        params = {**self.DEFAULT_PARAMS, **params, **kwargs}
        return params


class OpenAICompletion(BaseCompletion):
    provider = LLMProvider.OPENAI

    def __init__(self, config: OpenAIConfig):
        super().__init__()
        self.model = config.model
        self.api_key = config.api_key

    @property
    def request_endpoint(self):
        return API_BASE

    @property
    def request_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.api_key),
        }

    @property
    def default_request_json(self):
        return {"model": self.model}
