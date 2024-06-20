import datetime

import jenkins
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from jenkins_terminal.config import get_jenkins_server, load_config, validate_config

app = typer.Typer()
console = Console()


@app.command()
def builds(
    job: str = typer.Argument(..., help="Jenkins job name, e.g., sv/protocol_tests"),
):
    """
    List the latest ten builds of a specified Jenkins job
    """
    config = load_config()
    validate_config(config)

    server = get_jenkins_server(config)

    try:
        job_info = server.get_job_info(job)
        builds = job_info["builds"][:10]  # Get the latest 10 builds

        table = Table(title=f"Latest 10 Builds for {job}")
        table.add_column("#", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Triggered by", style="green")
        table.add_column("Start time", style="yellow")

        for build in builds:
            build_info = server.get_build_info(job, build["number"])
            build_number = build["number"]
            status = build_info["result"]

            user = "Unknown user"
            for action in build_info["actions"]:
                if action and "causes" in action:
                    causes = action["causes"]
                    if causes and "userName" in causes[0]:
                        user = causes[0]["userName"]
                        break

            timestamp = datetime.datetime.fromtimestamp(build_info["timestamp"] / 1000)
            start_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")

            table.add_row(str(build_number), status, user, start_time)

        console.print(table)
    except jenkins.JenkinsException as e:
        console.print(Panel(f"Failed to fetch builds: {e}", style="bold red"))
        raise typer.Exit(code=1)
