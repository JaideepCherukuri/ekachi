from collections.abc import Mapping
from typing import Any, Optional

from app.application.errors.exceptions import BadRequestError
from langchain_anthropic import ChatAnthropic
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI


SUPPORTED_MODEL_PROVIDERS = {"anthropic", "deepseek", "ollama", "openai"}


def build_chat_model(
    *,
    model_name: str,
    model_provider: str,
    temperature: float,
    max_tokens: int,
    api_base: Optional[str] = None,
    api_key: Optional[str] = None,
    default_headers: Optional[Mapping[str, str]] = None,
):
    provider = model_provider.strip().lower()
    if provider not in SUPPORTED_MODEL_PROVIDERS:
        raise BadRequestError(f"Unsupported model provider: {model_provider}")

    common_kwargs: dict[str, Any] = {
        "temperature": temperature,
    }
    if default_headers:
        common_kwargs["default_headers"] = default_headers

    if provider == "openai":
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=api_base,
            max_completion_tokens=max_tokens,
            **common_kwargs,
        )

    if provider == "deepseek":
        return ChatDeepSeek(
            model=model_name,
            api_key=api_key,
            base_url=api_base,
            max_tokens=max_tokens,
            **common_kwargs,
        )

    if provider == "anthropic":
        return ChatAnthropic(
            model_name=model_name,
            api_key=api_key,
            base_url=api_base,
            max_tokens_to_sample=max_tokens,
            **common_kwargs,
        )

    return ChatOllama(
        model=model_name,
        base_url=api_base,
        num_predict=max_tokens,
        temperature=temperature,
    )
