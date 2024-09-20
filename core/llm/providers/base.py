import time
import httpx
import inspect
import logging
import itertools
from typing import Callable, Optional

from ..schemas import LLMResponse
from ..llm_context import current_context
from ..exceptions import LLMHandlerException, LLMProviderException

logger = logging.getLogger(__name__)


class BaseCompletion:
    def __init__(self):
        self.__injected_hooks = {}

    def inject_completion_hook(self, hook, hook_id):
        self.__injected_hooks[hook_id] = hook

    def eject_completion_hook(self, hook_id):
        self.__injected_hooks.pop(hook_id, None)

    @property
    def injected_hooks(self):
        return self.__injected_hooks

    @property
    def request_endpoint(self):
        raise NotImplementedError

    @property
    def request_headers(self):
        raise NotImplementedError

    @property
    def default_request_json(self):
        raise NotImplementedError

    async def completion(
        self,
        post_hooks: list[Callable] = [],
        func_tracker: Optional[dict] = None,
        **kwargs
    ) -> LLMResponse:
        logger.info("Start calling LLM...")
        t0 = time.perf_counter()
        if self.default_request_json:
            kwargs = {**kwargs, **self.default_request_json}
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                self.request_endpoint,
                headers=self.request_headers,
                json=kwargs,
            )
            if isinstance(func_tracker, dict):
                func_tracker["raw"] = response.content
                func_tracker["headers"] = response.headers
            response.raise_for_status()

        try:
            data = response.json()
        except Exception as exc:
            try:
                response_text = response.text
            except Exception as exc:
                raise LLMHandlerException("Cannot parse JSON data from LLM response")
            raise LLMHandlerException(response_text)
        try:
            response = LLMResponse(
                model=data["model"],
                usage=data["usage"],
                completion=data["choices"][0]["message"]["content"],
                headers=response.headers,
                raw=response.content,
            )
        except Exception as exc:
            logger.error("Cannot parse data into LLMResponse: data={}".format(data))
            if "error" in data:
                error_code = data.get("error", {}).get("code")
                error_msg = data.get("error", {}).get("message")
                raise LLMProviderException(error_code=error_code, error_msg=error_msg)
            raise

        logger.info("LLM call succeeded in {}s".format(time.perf_counter() - t0))

        hooks = itertools.chain(post_hooks, self.injected_hooks.values())
        llm_context = current_context()
        if llm_context and llm_context.value:
            hooks = itertools.chain(hooks, [current_context().value["hook"]])
        for hook in hooks:
            if inspect.iscoroutinefunction(hook):
                await hook(response)
            else:
                hook(response)

        return response
