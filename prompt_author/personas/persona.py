from pydantic import BaseModel


class Persona(BaseModel):
    name: str
    description: str

    def to_string(self) -> str:
        return (
            "Please act as the persona described below in the <persona></persona> tags. "
            "It is very important that you respond like this persona would.\n\n"
            f"<persona>You are {self.name}. {self.description}</persona>"
        )
