from pathlib import Path
from typing import List, Optional

import jenkins
import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from jenkins_terminal.config import get_jenkins_server, load_config, validate_config

app = typer.Typer()
console = Console()


def parse_params(params: Optional[List[str]]) -> dict:
    parameters = {}
    if params:
        for param in params:
            try:
                key, value = param.split("=")
                parameters[key] = value
            except ValueError:
                console.print(
                    Panel(
                        f"Invalid parameter format: {param}. Should be key=value",
                        style="bold red",
                    )
                )
                raise typer.Exit(code=1)
    return parameters


def load_params_from_file(config_file: Path) -> dict:
    with config_file.open("r") as file:
        file_parameters = yaml.safe_load(file)
        if not isinstance(file_parameters, dict):
            console.print(
                Panel(
                    "Invalid format in the config file. It should be a dictionary.",
                    style="bold red",
                )
            )
            raise typer.Exit(code=1)
        return file_parameters


def confirm_parameters(parameters: dict) -> bool:
    params_text = "\n".join([f"[cyan]{key}[/cyan] = [yellow]{value}[/yellow]" for key, value in parameters.items()])
    console.print(Panel(params_text, title="Parameters", title_align="left", border_style="dim"))
    return Confirm.ask("Do you want to proceed with these parameters?")


@app.command()
def build(
    job: str = typer.Argument(..., help="Jenkins job path, e.g., sv/protocol_tests"),
    params: Optional[List[str]] = typer.Argument(None, help="Job parameters in key=value format or path to YAML config file"),
):
    """
    Trigger a Jenkins job
    """

    config = load_config()
    validate_config(config)

    parameters = {}

    if params:
        for param in params:
            param_path = Path(param)
            if param_path.is_file():
                parameters.update(load_params_from_file(param_path))
            else:
                parameters.update(parse_params([param]))

    if not confirm_parameters(parameters):
        console.print(Panel("Build cancelled.", style="red"))
        raise typer.Exit()

    server = get_jenkins_server(config)

    try:
        server.build_job(job, parameters)
        console.print(Panel("Build triggered successfully", style="green", border_style="dim"))
    except jenkins.JenkinsException as e:
        console.print(Panel(f"Build trigger failed: {e}", style="bold red"))
        raise typer.Exit(code=1)
