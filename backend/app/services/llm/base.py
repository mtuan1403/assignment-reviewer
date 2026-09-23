from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMException(Exception):
    pass


class BaseLLMProvider(ABC):
    @property
    def provider_name(self) -> str:
        return self.__class__.__name__

    @property
    def model_name(self) -> str:
        return getattr(self, "model", "default")

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        """Generates a structured response adhering strictly to the given Pydantic model."""
        pass

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generates plain text response."""
        pass
