from pathlib import Path
from typing import List, Optional

import jenkins
import typer
import yaml
import time
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


def parse_params(params: List[str]) -> dict:
    parameters = {}
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


def confirm_parameters(job: str, parameters: dict) -> bool:
    params_text = "\n".join([f"[cyan]{key}[/cyan] = [yellow]{value}[/yellow]" for key, value in parameters.items()])
    console.print(Panel(params_text, title=f"Parameters for job: {job}", title_align="left", border_style="dim"))
    return Confirm.ask("Do you want to proceed with these parameters?")


def stream_build_console_output(server, job_name, build_number):
    console.print(Panel(f"Streaming console output for job {job_name} build #{build_number}", style="blue", border_style="dim"))
    last_offset = 0
    while True:
        try:
            output = server.get_build_console_output(job_name, build_number)
            new_output = output[last_offset:]
            console.print(new_output, end="")
            last_offset = len(output)
            # Check if build is still running
            build_info = server.get_build_info(job_name, build_number)
            if build_info["building"]:
                time.sleep(2)
            else:
                break
        except jenkins.JenkinsException as e:
            console.print(Panel(f"Error streaming console output: {e}", style="bold red"))
            break
    console.print(Panel(f"Build #{build_number} completed.", style="green", border_style="dim"))


@app.command()
def build(
    job: Optional[str] = typer.Argument(None, help="Jenkins job path, e.g., sv/protocol_tests"),
    params: Optional[List[str]] = typer.Option(None, "--param", "-p", help="Job parameter in key=value format"),
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

    if params:
        new_parameters = parse_params(params)
        parameters.update(new_parameters)

    if not confirm_parameters(job, parameters):
        console.print(Panel("Build cancelled.", style="red"))
        raise typer.Exit()

    server = get_jenkins_server(config)

    try:
        # Trigger the build
        queue_id = server.build_job(job, parameters)
        console.print(Panel("Build triggered successfully", style="green", border_style="dim"))

        # Get the build number of the triggered build
        build_number = None
        while not build_number:
            queue_item = server.get_queue_item(queue_id)
            if "executable" in queue_item:
                build_number = queue_item["executable"]["number"]
            else:
                time.sleep(1)

        # Stream the console output
        stream_build_console_output(server, job, build_number)

        # Save build information
        if "builds" not in config["template"]:
            config["template"]["builds"] = {}
        config["template"]["builds"][job] = {"build_number": build_number, "parameters": parameters}
        save_config(config)
    except jenkins.JenkinsException as e:
        console.print(Panel(f"Build trigger failed: {e}", style="bold red"))
        raise typer.Exit(code=1)
