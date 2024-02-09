# Miniogre

miniogre is a command line application that helps generate a Dockerfile and requirements.txt for a Python project by analyzing the project codebase and README.

## How it works

The main entry point is miniogre/main.py. This contains the Typer CLI definition and main command functions.

The key steps are:

- Analyze project directory to determine main code language
- Find and read README file
- Use GPT-3 to generate requirements.txt content by prompting with README contents
- Generate Dockerfile and populate with requirements
- Build Docker image

The `miniogre_cli` module contains the main logic:

- `actions.py`: Functions for listing files, extracting extensions, reading README, generating requirements with GPT-3, and building Docker image.
- `config.py`: Functions for configuring output directory, bashrc, and Dockerfile.
- `constants.py`: Template strings for Dockerfile and bashrc.

The .env file contains the GPT-3 model name and prompt content.

So in summary, miniogre inspects your project, prompts GPT-3 to generate requirements from the README, and builds a Dockerfile to containerize your application. This automates the process of dockerizing a Python application.

## Usage

After installation, run:

`miniogre run <project_dir>`

This will analyze the project, generate `ogre_dir/Dockerfile` and `ogre_dir/requirements.txt`, and build a Docker image.

The requirements command just generates the requirements file.

## Installation

`pip install miniogre`

## Contributing
Contributions welcome!
