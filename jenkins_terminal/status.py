import datetime
from typing import Optional

import jenkins
import typer
from rich.console import Console
from rich.panel import Panel

from jenkins_terminal.config import (
    get_jenkins_server,
    load_config,
    save_config,
    validate_config,
)

app = typer.Typer()
console = Console()


@app.command()
def status(
    job: Optional[str] = typer.Argument(None, help="Jenkins job name"),
    build_number: Optional[int] = typer.Option(None, "--build-number", "-b", help="Build number (optional)"),
):
    """
    Display Jenkins job status
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

    save_config(config)

    server = get_jenkins_server(config)

    try:
        if build_number:
            build_info = server.get_build_info(job, build_number)
        else:
            job_info = server.get_job_info(job)
            build_info = server.get_build_info(job, job_info["lastBuild"]["number"])
    except jenkins.JenkinsException as e:
        console.print(Panel(f"Failed to get status: {e}", style="bold red"))
        raise typer.Exit(code=1)

    timestamp = datetime.datetime.fromtimestamp(build_info["timestamp"] / 1000)
    duration_seconds = build_info["duration"] / 1000
    duration = str(datetime.timedelta(seconds=int(duration_seconds)))
    status = "building" if build_info.get("building") else build_info["result"]

    # Extract user who triggered the job
    user = "Unknown user"
    for action in build_info["actions"]:
        if action and "causes" in action:
            causes = action["causes"]
            if causes and "userName" in causes[0]:
                user = causes[0]["userName"]
                break

    # Extract parameters
    parameters = {}
    for action in build_info["actions"]:
        if action and action["_class"] == "hudson.model.ParametersAction":
            for param in action["parameters"]:
                parameters[param["name"]] = param["value"]

    # Format parameters
    params_text = "\n".join([f"  {name}: {value}" for name, value in parameters.items()])

    info_text = ""
    info_text += f"[bold][cyan]Job:[/cyan] {job}[/bold]\n"
    info_text += f"[cyan]Status:[/cyan] {status}\n"
    info_text += f"[cyan]Build Number:[/cyan] {build_info['number']}\n"
    info_text += f"[cyan]Build Time:[/cyan] {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
    info_text += f"[cyan]Duration:[/cyan] {duration}\n"
    info_text += f"[cyan]Triggered By:[/cyan] {user}\n"
    info_text += f"[cyan]Parameters:[/cyan]\n{params_text}"

    console.print(Panel(info_text, title="Job Status", title_align="left", border_style="dim"))
