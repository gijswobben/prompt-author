from pydantic import BaseModel, ConfigDict, Field

from prompt_author.personas.default import DefaultPersona
from prompt_author.personas.persona import Persona


class ModelConfig(BaseModel):
    temperature: float = 0.7


class Config(BaseModel):
    template: str = Field(
        ...,
        title="Template name",
        description="The name of the template to use",
    )
    persona: Persona = Field(
        default=DefaultPersona,
        title="Persona",
        description="The persona to use",
    )
    model: ModelConfig = Field(
        ...,
        default_factory=ModelConfig,
        alias="model-config",
    )

    # Pydantic configuration
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
