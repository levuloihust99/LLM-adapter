from .settings import settings
from .schemas import LLMProvider
from .providers.openai import OpenAICompletion, OpenAIParamsBuilder
from .providers.azure import AzureOpenAIParamsBuilder, AzureOpenAICompletion


class LLMFactory:
    @classmethod
    def instance(cls):
        if settings.config.type == LLMProvider.OPENAI:
            llm_provider = OpenAICompletion(config=settings.config)
            llm_params_builder = OpenAIParamsBuilder()
        elif settings.config.type == LLMProvider.AZURE:
            llm_provider = AzureOpenAICompletion(config=settings.config)
            llm_params_builder = AzureOpenAIParamsBuilder()
        else:
            raise Exception("LLM type '{}' is not supported".format(settings.config.type))
        return llm_provider, llm_params_builder

llm_provider, llm_params_builder = LLMFactory.instance()
