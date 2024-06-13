import typer

from jenkins_terminal.build import build
from jenkins_terminal.config import config
from jenkins_terminal.status import status

app = typer.Typer()

app.command()(config)
app.command()(build)
app.command()(status)

if __name__ == "__main__":
    app()
