from pathlib import Path
from typing import Optional

import jenkins
import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

CONFIG_FILE_PATH = Path.home() / ".config" / "jenkins.yaml"

app = typer.Typer()
console = Console()


def load_config() -> dict:
    if CONFIG_FILE_PATH.exists():
        with CONFIG_FILE_PATH.open("r") as file:
            return yaml.safe_load(file)
    return {"url": "", "username": "", "token": "", "template": {"job": ""}}


def save_config(config: dict):
    CONFIG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE_PATH.open("w") as file:
        yaml.safe_dump(config, file)


def validate_config(config: dict):
    if not config["url"] or not config["username"] or not config["token"]:
        console.print(Panel("Please configure Jenkins URL, username, and token using the `config` command.", style="bold red"))
        raise typer.Exit()


def get_jenkins_server(config: dict) -> jenkins.Jenkins:
    return jenkins.Jenkins(config["url"], username=config["username"], password=config["token"])


@app.command()
def config(
    username: Optional[str] = typer.Option(None, "--username", help="Jenkins username"),
    url: Optional[str] = typer.Option(None, "--url", help="Jenkins URL"),
    token: Optional[str] = typer.Option(None, "--token", help="Jenkins API token"),
    job: Optional[str] = typer.Option("", "--job", help="Default Jenkins job"),
):
    """
    Set Jenkins configuration parameters
    """
    config = load_config()

    if not (username or url or token):
        url = Prompt.ask("Please enter Jenkins URL", default=config["url"])
        username = Prompt.ask("Please enter Jenkins username", default=config["username"])
        token = Prompt.ask("Please enter Jenkins API token", default=config["token"])
        job = Prompt.ask("Please enter Jenkins default job", default=config["template"].get("job", ""))

    if username:
        config["username"] = username
        console.print(Panel(f"Set username to {username}", style="green", border_style="dim"))
    if url:
        config["url"] = url
        console.print(Panel(f"Set url to {url}", style="green", border_style="dim"))
    if token:
        config["token"] = token
        console.print(Panel(f"Set token to {token}", style="green", border_style="dim"))
    if job:
        config["template"]["job"] = job
        console.print(Panel(f"Set default job to {job}", style="green", border_style="dim"))

    save_config(config)
    console.print(Panel("Jenkins configuration saved successfully.", style="green", border_style="dim"))


if __name__ == "__main__":
    app()
