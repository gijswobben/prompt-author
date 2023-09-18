from prompt_author.personas.persona import Persona


class _DefaultPersona(Persona):
    def to_string(self) -> str:
        return ""


DefaultPersona = _DefaultPersona(
    name="",
    description="",
)
