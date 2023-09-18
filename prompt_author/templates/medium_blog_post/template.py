from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field
from rich.markdown import Markdown
from rich.panel import Panel

from prompt_author.logging import console
from prompt_author.template import Template

# Current directory contains all the templates
templates_directory = Path(__file__).parent


class Abstract(BaseModel):
    content: str = Field(
        ...,
        title="Abstract",
        description="Abstract of the blog",
    )


class TitleSuggestions(BaseModel):
    titles: list[str] = Field(
        ...,
        title="Titles",
        description="Suggested titles for a blog",
    )

    def to_string(self) -> str:
        return "\n".join(
            [f"{index+1}. {title}" for index, title in enumerate(self.titles)]
        )


class BlogSection(BaseModel):
    title: str = Field(
        ...,
        title="Section Title",
        description="Title of the section",
    )
    content: str = Field(
        ...,
        title="Section Content",
        description="Content of the section",
    )


class BlogOutline(BaseModel):
    sections: list[BlogSection] = Field(
        ...,
        title="Sections",
        description="Sections of the blog",
    )

    def to_string(self) -> str:
        return "\n\n".join(
            [
                f"## {section.title}" + "\n" + section.content
                for section in self.sections
            ]
        )


class Example(BaseModel):
    title: str
    content: str


class Examples(BaseModel):
    examples: list[Example]

    def to_string(self) -> str:
        return "\n\n".join(
            [
                f"## {example.title}" + "\n" + example.content
                for example in self.examples
            ]
        )


class Article(BaseModel):
    title: str = Field(
        ...,
        title="Title",
        description="Title of the blog",
    )
    abstract: str = Field(
        ...,
        title="Abstract",
        description="Abstract of the blog",
    )
    sections: list[BlogSection] = Field(
        ...,
        title="Sections",
        description="Sections of the blog",
    )

    def to_string(self) -> str:
        return "\n\n".join(
            [
                f"# {self.title}",
                f"> {self.abstract}",
                *[
                    f"## {section.title}" + "\n\n" + section.content
                    for section in self.sections
                ],
            ]
        )


class MediumBlogPostTemplate(Template):
    name: str = "medium_blog_post"

    def run(self) -> str:
        console.log(
            f"Writing a blog post about: \"[italic green]{self.memory['topic']}[/]\""
        )

        with console.status("Generating titles...", spinner="earth"):
            # Start by making suggestions for the title
            title_suggestions = self.step(
                model=TitleSuggestions,
                prompt_file=templates_directory / "title.md",
            )
            self.memory["title_suggestions"] = title_suggestions.titles
            console.log(
                Panel(
                    Markdown(title_suggestions.to_string()), title="Title Suggestions"
                )
            )

        with console.status("Selecting the best title...", spinner="earth"):
            # Select the best title for the blog
            title = self.step(
                prompt_file=templates_directory / "select_title.md",
            )
            self.memory["title"] = title
            console.log(Panel(title, title="Selected Title"))

        with console.status("Writing the blog outline...", spinner="earth"):
            # Write an outline for the blog post
            post_outline = self.step(
                model=BlogOutline,
                prompt_file=templates_directory / "outline.md",
            )
            self.memory["outline"] = post_outline.to_string()
            console.log(Panel(Markdown(post_outline.to_string()), title="Blog Outline"))

        with console.status("Writing the abstract...", spinner="earth"):
            # Write an abstract
            abstract = self.step(
                model=Abstract,
                prompt_file=templates_directory / "abstract.md",
            )
            self.memory["abstract"] = abstract.content
            console.log(Panel(abstract.content, title="Abstract"))

        with console.status("Generating relevant examples...", spinner="earth"):
            # Create some concrete examples to illustrate the blog
            examples = self.step(
                model=Examples,
                prompt_file=templates_directory / "concrete_examples.md",
            )
            self.memory["examples"] = examples.to_string()
            console.log(Panel(Markdown(examples.to_string()), title="Examples"))

        with console.status("Writing the blog content...", spinner="earth"):
            # Use the outline to write the blog
            article = self.step(
                model=Article,
                prompt_file=templates_directory / "blog.md",
            )

        return article.to_string()
