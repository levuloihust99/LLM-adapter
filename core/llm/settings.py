import os
from dotenv import load_dotenv
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field

from .schemas import LLMProviderConfig, AzureConfig, OpenAIConfig

load_dotenv()


class LoggingFileHandler(BaseModel):
    type: Literal["file"] = "file"
    path: str


class LoggingRotatingFileHandler(BaseModel):
    type: Literal["rotating_file"] = "rotating_file"
    path: str
    max_bytes: Optional[int] = None
    backup_count: Optional[int] = None


LoggingHandler = Annotated[
    Union[LoggingFileHandler, LoggingRotatingFileHandler], Field(discriminator="type")
]


class LoggingSettings(BaseModel):
    handlers: list[LoggingHandler]


class LLMSettings(BaseModel):
    config: LLMProviderConfig
    logging: LoggingSettings

    @classmethod
    def load(cls) -> "LLMSettings":
        handler = LoggingRotatingFileHandler(
            path=os.environ["LOGCOST_FILE"],
            max_bytes=int(os.environ["LOGCOST_FILE_MAX_BYTES"]),
            backup_count=int(os.environ["LOGCOST_FILE_BACKUP_COUNT"]),
        )
        is_azure_enable = os.environ["ENABLE_AZURE_OPENAI"] == "true"
        is_openai_enable = os.environ["ENABLE_OPENAI"] == "true"
        if is_azure_enable:
            config = AzureConfig(
                deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
                api_key=os.environ["AZURE_OPENAI_API_KEY"],
                api_base=os.environ["AZURE_OPENAI_API_BASE"],
                api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            )
        elif is_openai_enable:
            config = OpenAIConfig(
                api_key=os.environ["OPENAI_API_KEY"], model=os.environ["OPENAI_MODEL"]
            )
        else:
            raise Exception(
                "You must enable Azure OpenAI or OpenAI, i.e. set `ENABLE_AZURE_OPENAI=true` or `ENABLE_OPENAI=true`"
            )
        return cls(config=config, logging=LoggingSettings(handlers=[handler]))


settings = LLMSettings.load()
