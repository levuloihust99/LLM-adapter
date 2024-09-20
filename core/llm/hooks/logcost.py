import logging
from ..schemas import LLMResponse
from ..providers.price import PRICE_LOOKUP
from ..utils.logging import do_file_logging

logger = logging.getLogger(__name__)
do_file_logging(logger)


def logcost(
    response: LLMResponse,
    kwargs: dict = {},
):
    pricing = PRICE_LOOKUP[response.model]
    calculated_cost = (
        pricing["input"] * response.usage.prompt_tokens
        + pricing["output"] * response.usage.completion_tokens
    )
    log_message = "\n\t- LLM usage: {}\n\t- Model: {}\n\t- Pricing: {}\n\t- Calculated cost: {}".format(
        response.usage,
        response.model,
        pricing,
        calculated_cost,
    )
    for key, value in kwargs.items():
        log_message += "\n\t- {}: {}".format(key, value)
    logger.info(log_message, {"file": True})
