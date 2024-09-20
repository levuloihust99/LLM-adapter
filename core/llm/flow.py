from functools import partial
from typing import Optional, Union

from .schemas import LLMResponse
from .hooks.logcost import logcost
from .instance import llm_params_builder, llm_provider

logcost_hook = partial(
    logcost, kwargs={"Provider": llm_provider.provider, "API Key": llm_provider.api_key}
)


def log_response(response: LLMResponse, file_name: str):
    with open(file_name, "w", encoding="utf-8") as writer:
        writer.write(response.completion)


async def llm_flow(
    prompt: str,
    screenshot: Union[bytes] = None,
    response_format: Optional[dict] = None,
    **context
) -> LLMResponse:
    params = llm_params_builder.build_params(
        prompt=prompt, screenshot=screenshot, response_format=response_format
    )
    params["post_hooks"] = [logcost_hook]
    if context.get("completion_file"):
        log_response_hook = partial(log_response, file_name=context["completion_file"])
        params["post_hooks"].append(log_response_hook)
    response = await llm_provider.completion(**params)
    return response
