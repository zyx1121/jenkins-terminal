# Jenkins Terminal Tool

A powerful command-line tool for interacting with Jenkins, enabling easy configuration, build triggering, and status monitoring.

[![PyPI version](https://badge.fury.io/py/jenkins-terminal.svg)](https://badge.fury.io/py/jenkins-terminal)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🔧 Interactive and command-line Jenkins configuration
- 🚀 Trigger Jenkins jobs with customizable parameters
- 📊 Retrieve and display Jenkins job statuses
- 📝 Fetch and show Jenkins job console outputs
- 📋 List builds of specified Jenkins jobs
- 💾 Template job feature for quick access to frequently used jobs

## Installation

### Using pip

```bash
pip install jenkins-terminal
```

## Quick Start

1. Set up your Jenkins configuration:
   ```bash
   jenkins config
   ```

2. Trigger a Jenkins job:
   ```bash
   jenkins build <job> --param key1=value1 --param key2=value2
   ```

3. Check job status:
   ```bash
   jenkins status <job>
   ```

## Detailed Usage

### Configuration

Set Jenkins configuration parameters interactively:
```bash
jenkins config
```

Or use command-line options:
```bash
jenkins config --username <username> --url <url> --token <token>
```

### Build Triggering

Trigger a job with inline parameters:
```bash
jenkins build <job> -p key1=value1 -p key2=value2
```

Use parameters from a YAML file:
```bash
jenkins build <job> -f <file>
```

Load parameters from a specific build:
```bash
jenkins build <job> -l <build-number>
```

Combine options:
```bash
jenkins build <job> -l <build-number> -f <file> -p key1=value1
```

### Job Status and Output

Get job status:
```bash
jenkins status <job> -b <build-number>
```

Fetch console output:
```bash
jenkins output <job> -b <build-number> -l <max-lines>
```

List job builds:
```bash
jenkins builds <job>
```

### Template Job Feature

The tool automatically saves the last executed job as a template. Run without specifying job name:
```bash
jenkins build
```

## Configuration File

The tool uses `~/.config/jenkins.yaml` for storing configurations and templates.

Example:
```yaml
template:
  builds:
    job1:
      build_number: 10
      parameters:
        SITE: tpe001
  job: job1
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

- [Typer](https://typer.tiangolo.com/) - CLI library for Python
- [Rich](https://rich.readthedocs.io/) - Rich text formatting in the terminal
- [Jenkins](https://www.jenkins.io/) - The leading open source automation server

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

If you encounter any problems or have any questions, please [open an issue](https://github.com/yourusername/jenkins-terminal/issues) on GitHub.