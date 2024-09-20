from enum import Enum
from typing import Annotated, Literal, Optional, Union
from pydantic import BaseModel, Field, model_validator


class LLMProvider(str, Enum):
    OPENAI = "openai"
    AZURE = "azure"


class OpenAIConfig(BaseModel):
    type: Literal[LLMProvider.OPENAI] = LLMProvider.OPENAI

    api_key: Optional[str]
    model: Optional[str]


class AzureConfig(BaseModel):
    type: Literal[LLMProvider.AZURE] = LLMProvider.AZURE

    deployment: Optional[str]
    api_key: Optional[str]
    api_base: Optional[str]
    api_version: Optional[str]


LLMProviderConfig = Annotated[
    Union[OpenAIConfig, AzureConfig], Field(discriminator="type")
]


class LLMUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    @model_validator(mode="after")
    def ensure_consistent_state(self) -> "LLMUsage":
        if self.prompt_tokens + self.completion_tokens != self.total_tokens:
            raise ValueError("Inconsistent state: {}".format(self))
        return self


class LLMResponse(BaseModel):
    usage: LLMUsage
    model: str
    completion: str
    headers: dict
    raw: bytes
