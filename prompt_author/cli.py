import os
from io import TextIOWrapper

import click
import yaml
from langchain.chat_models import AzureChatOpenAI
from rich.markdown import Markdown
from rich.padding import Padding
from rich.panel import Panel
from rich.pretty import Pretty

from prompt_author.config import Config
from prompt_author.logging import console
from prompt_author.personas import personas
from prompt_author.template import Template, TemplateRegistry

registry = TemplateRegistry()


@click.group()
def main() -> None:
    """..."""


@main.command(name="run")
@click.option(
    "-c",
    "--config",
    type=click.File("r"),
    required=True,
)
@click.option("-v", "--verbose", is_flag=True)
def run(config: TextIOWrapper, verbose: bool = False) -> None:
    """..."""

    # Clear the console before running
    click.clear()

    # Load the config file
    with console.status("Loading configuration file...", spinner="earth"):
        config_text = config.read()
        config_content = yaml.load(config_text, Loader=yaml.FullLoader)
        config_content["persona"] = personas[config_content.get("persona", "default")]
        config_object = Config.model_validate(
            obj=config_content,
            strict=True,
        )
        if verbose:
            console.print(
                "Loaded configuration:",
                Padding(
                    Pretty(config_object, no_wrap=True),
                    pad=(0, 0, 1, 4),
                ),
            )

    # Use the config to load the template
    with console.status("Loading template...", spinner="earth"):
        llm = AzureChatOpenAI(
            deployment_name=os.environ["AZURE_CHAT_DEPLOYMENT_NAME"],
            temperature=config_object.model.temperature,
            openai_api_type="azure",
            request_timeout=600,
            max_retries=3,
        )
        template_type: type[Template] = registry.get(config_object.template)
        template_instance: Template = template_type(
            llm=llm,
            persona=config_object.persona,
            verbose=verbose,
            **config_object.model_dump(
                exclude={
                    "template",
                    "persona",
                    "model",
                    "model-config",
                }
            ),
        )
        if verbose:
            console.print(
                "Using LLM:",
                Padding(
                    Pretty(llm, no_wrap=True),
                    pad=(0, 0, 1, 4),
                ),
            )

    # Run the template
    result = template_instance.run()
    console.rule()
    console.line(2)
    console.print(Panel(Markdown(result)))
