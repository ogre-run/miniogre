# Miniogre

**miniogre** is a command line application that helps generate a Dockerfile, requirements.txt file, and SBOM files for a Python project by analyzing the project codebase and README.

## How it works

The main entry point is miniogre/main.py. This contains the Typer CLI definition and main command functions.

The key steps are:

- Analyze project directory to determine main code language
- Find and read README file
- Use GPT-4 to generate requirements.txt content by prompting with README contents
- Generate requirements.txt
- Generate Dockerfile
- Generate SBOM.json
- Build Docker image
- Spin up ogre container

The `miniogre` module contains the main logic:

- `main.py`: This where the commands are defined.
- `actions.py`: Functions for listing files, extracting extensions, reading README, generating requirements with GPT-4, and building Docker image.
- `config.py`: Functions for configuring output directory, bashrc, and Dockerfile.
- `constants.py`: Template strings for Dockerfile and bashrc.

The .env file defines environment variables such as the GPT-4 model name and prompt content.

So in summary, miniogre inspects your project, prompts GPT-4 to generate requirements from the README, and builds a Dockerfile to containerize your application. This automates the process of dockerizing a Python application.

## Usage

After installation, go inside the project folder and run:

`miniogre run`

This will analyze the project, generate `ogre_dir/Dockerfile`, `ogre_dir/requirements.txt`, and `ogre_dir/sbom.json` and build a Docker image.

There are other commands:

- `readme`: Analyzes the source code to generate a new `README.md` file that is compatible with what actually happens in the source code.  

## Installation

- Using `pip`: `pip install miniogre`
- Using `pipx`: `pipx install miniogre`

## Contributing
Contributions are welcomed! Please reach out to the maintainers if you have any questions: [contact@ogre.run](contact@ogre.run).