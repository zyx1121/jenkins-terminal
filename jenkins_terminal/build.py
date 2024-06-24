from pathlib import Path
from typing import List, Optional

import jenkins
import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from jenkins_terminal.config import (
    get_jenkins_server,
    load_config,
    save_config,
    validate_config,
)

app = typer.Typer()
console = Console()


def parse_param(param: Optional[str]) -> dict:
    parameters = {}
    if param:
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


def confirm_parameters(job: str, parameters: dict) -> bool:
    params_text = "\n".join([f"[cyan]{key}[/cyan] = [yellow]{value}[/yellow]" for key, value in parameters.items()])
    console.print(Panel(params_text, title=f"Parameters for job: {job}", title_align="left", border_style="dim"))
    return Confirm.ask("Do you want to proceed with these parameters?")


@app.command()
def build(
    job: Optional[str] = typer.Argument(None, help="Jenkins job path, e.g., sv/protocol_tests"),
    param: Optional[str] = typer.Option(None, "--param", "-p", help="Job parameter in key=value format"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Path to YAML file containing job parameters"),
    load: Optional[int] = typer.Option(None, "--load", "-l", help="Load parameters from a specific build number"),
):
    """
    Trigger a Jenkins job
    """

    config = load_config()
    validate_config(config)

    # Use the last job if not provided
    if job:
        config["template"]["job"] = job
    else:
        job = config["template"].get("job")

    if not job:
        console.print(Panel("No job specified and no previous job found in template.", style="bold red"))
        raise typer.Exit()

    parameters = {}

    # Use the last parameters if not provided
    last_build_info = config["template"]["builds"].get(job)
    if last_build_info:
        parameters.update(last_build_info.get("parameters", {}))

    if load is not None:
        try:
            server = get_jenkins_server(config)
            if load == 0:
                build_info = server.get_job_info(job)["lastCompletedBuild"]
                build_number = build_info["number"]
            else:
                build_number = load
            build_info = server.get_build_info(job, build_number)
            loaded_parameters = build_info.get("actions", [{}])[0].get("parameters", {})
            parameters.update({param["name"]: param["value"] for param in loaded_parameters})
        except jenkins.JenkinsException as e:
            console.print(Panel(f"Failed to load parameters from build number {load}: {e}", style="bold red"))
            raise typer.Exit(code=1)

    if file:
        file_parameters = load_params_from_file(file)
        parameters.update(file_parameters)

    if param:
        new_parameters = parse_param(param)
        parameters.update(new_parameters)

    if not confirm_parameters(job, parameters):
        console.print(Panel("Build cancelled.", style="red"))
        raise typer.Exit()

    server = get_jenkins_server(config)

    try:
        last_completed_build = server.get_job_info(job).get("lastCompletedBuild")
        if last_completed_build:
            last_build_number = last_completed_build["number"]
        else:
            last_build_number = 0  # Default to 0 if no completed build exists

        server.build_job(job, parameters)
        console.print(Panel("Build triggered successfully", style="green", border_style="dim"))

        # Save build information
        if "builds" not in config["template"]:
            config["template"]["builds"] = {}
        config["template"]["builds"][job] = {"build_number": last_build_number + 1, "parameters": parameters}
        save_config(config)
    except jenkins.JenkinsException as e:
        console.print(Panel(f"Build trigger failed: {e}", style="bold red"))
        raise typer.Exit(code=1)
