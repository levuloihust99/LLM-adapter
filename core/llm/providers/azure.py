import base64
import logging

logger = logging.getLogger(__name__)

from typing import Optional, Union
from ..schemas import LLMProvider, AzureConfig
from .base import BaseCompletion


API_BASE_TEMPLATE = "{api_base}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"


class AzureOpenAIParamsBuilder:
    DEFAULT_PARAMS = {
        "max_tokens": 4096,
        "temperature": 0,
    }

    def build_params(
        self,
        prompt: str,
        screenshot: Union[bytes] = None,
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


class AzureOpenAICompletion(BaseCompletion):
    provider = LLMProvider.AZURE

    def __init__(self, config: AzureConfig):
        super().__init__()
        self.deployment = config.deployment
        self.api_key = config.api_key
        self.api_base = config.api_base
        self.api_version = config.api_version

    @property
    def request_endpoint(self):
        return API_BASE_TEMPLATE.format(
            api_base=self.api_base,
            deployment=self.deployment,
            api_version=self.api_version,
        )

    @property
    def request_headers(self):
        return {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }

    @property
    def default_request_json(self):
        return {}
