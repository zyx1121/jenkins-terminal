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
def output(
    job: Optional[str] = typer.Argument(None, help="Jenkins job name, e.g., sv/protocol_tests"),
    build_number: Optional[int] = typer.Option(None, "--build-number", "-b", help="Specific build number to fetch the console output"),
    max_lines: Optional[int] = typer.Option(None, "--max-lines", "-l", help="Maximum number of lines to display from the console output"),
):
    """
    Fetch the console output of the latest or specific Jenkins job build
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
            output = server.get_build_console_output(job, build_number)
        else:
            last_build_number = server.get_job_info(job)["lastCompletedBuild"]["number"]
            output = server.get_build_console_output(job, last_build_number)

        if max_lines:
            output = "\n".join(output.splitlines()[-max_lines:])

        console.print(Panel(output, title=f"Console Output for {job}", border_style="dim", title_align="left"))
    except jenkins.JenkinsException as e:
        console.print(Panel(f"Failed to fetch console output: {e}", style="bold red"))
        raise typer.Exit(code=1)
