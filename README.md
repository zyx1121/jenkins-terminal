# Jenkins Terminal Tool

A command-line tool for interacting with Jenkins, allowing you to configure Jenkins credentials, trigger builds, and get job statuses.

## Features

- Set Jenkins configuration parameters interactively or via command-line options
- Trigger Jenkins jobs with parameters
- Get the status of Jenkins jobs
- Fetch and display Jenkins job console outputs
- List the builds of a specified Jenkins job
- Template job feature to automatically save and read last executed job

## Installation

### Using pip

1. Install the tool:

    ```bash
    pip install jenkins-terminal
    ```

2. Run the CLI tool:

    ```bash
    jenkins <command>
    ```

## Usage

### Configuration

You can set Jenkins configuration parameters either interactively or via command-line options.

#### Interactively

Run the following command and follow the prompts to enter your Jenkins URL, username, and API token:

```bash
jenkins config
```

#### Command-line options

You can also set the configuration parameters using command-line options:

```bash
jenkins config --username <username> --url <url> --token <token>
```

### Trigger a Jenkins Job

Trigger a Jenkins job with parameters:

```bash
jenkins build <job> --param/-p <key1>=<value1> --param/-p <key2>=<value2>
```

Trigger a Jenkins job with parameters from a YAML file:

```bash
jenkins build <job> --file/-f <file>
```

Trigger a Jenkins job with parameters from specific build:

```bash
jenkins build <job> --load/-l <build-number>
```

Also, you can combine the above options:

```bash
jenkins build <job> -l <build-number> -f <file> -p <key1>=<value1> -p <key2>=<value2>
```

The YAML file should contain the job parameters in the following format:

```yaml
key1: value1
key2: value2
```

### Get Jenkins Job Status

Get the status of a Jenkins job:

```bash
jenkins status <job> --build-number/-b <number>
```

### Fetch Jenkins Job Console Output

Fetch and display the console output of the latest or a specific Jenkins job build:

```bash
jenkins output <job> --build-number/-b <number> --max-lines/-l <number>
```

### List the builds of Jenkins Job

List the builds of a specified Jenkins job:

```bash
jenkins builds <job>
```

### Template Job

Save the last executed job as a template in the `~/.config/jenkins.yaml`:

```yaml
template:
  builds:
    job1:
      build_number: 10
      parameters:
        SITE: tpe001
    job2:
      build_number: 20
      parameters:
        SITE: tpe001
    job3:
      build_number: 30
      parameters:
        ENV: test1
        SITE: tpe002
  job: job3
```

You can run commands without specifying the job name and parameters:

```bash
jenkins build
```

Output:

```bash
╭─ Parameters for job: job3 ──────────────────────────────────────────────╮
│ ENV = test1                                                             │
│ SITE = tpe002                                                           │
╰─────────────────────────────────────────────────────────────────────────╯
Do you want to proceed with these parameters? [y/n]:
```

## Acknowledgements

- [Typer](https://typer.tiangolo.com/) - CLI library for Python
- [Rich](https://rich.readthedocs.io/) - Rich text and beautiful formatting in the terminal
- [Jenkins](https://www.jenkins.io/) - The leading open source automation server

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
