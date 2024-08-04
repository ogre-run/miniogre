# miniogre

**miniogre** automates the management of software dependencies with AI, to ensure your Python code runs on any computer. It is a command-line application that analyzes a Python codebase to automatically generate a Dockerfile, requirements.txt file, and SBOM files, expediting the process of packaging any Python application. Additionally, it is able to update the README (documentation) file to comply with what really happens in the source code.

![miniogre_gif_33](https://github.com/ogre-run/miniogre/assets/6482944/0850dbb5-6634-4f08-80a9-6fd8e3ca8e03)

## Why miniogre

Developers waste hours per week managing software dependencies. This is particularly true in AI development where many Python packages lack proper documentation and have outdated configuration files. **Miniogre empowers developers** to automatically identify, update, and install the necessary software dependencies to get code to work. Unlike other tools that need manual setup, **miniogre uses AI to quickly handle Python dependencies setup**, cutting down "dependency hunting" from hours a week to just minutes.

## How it Works

Upon running the application, it carries out the following steps:

- The project directory is scrutinized to identify the primary code language.
- The README file is located and read.
- The source code is crawled to obtain a preliminary list of requirements.
- A large language model (LLM) provider (choices are `openai`, `mistral`, `groq`, `octoai`) is used to refine the list of requirements and generate the final content for the `requirements.txt` file.
- The `requirements.txt`, `Dockerfile`, and `sbom.json` files are created.
- A Docker image of the application is built.
- An ogre container is spun up.

Two main commands can be run, with the `miniogre/main.py` file serving as the entry point.

- **run**: Executes a series of actions, including configuring directories and files (bashrc, Dockerfile), generating requirements, building a Docker image, and spinning up a container.
- **readme**: Constructs a new `README.md` file that mirrors the operations observed within the source code.

For more in-depth execution details, refer to `miniogre/main.py`,`miniogre/actions.py`, and `miniogre/config.py`.

## Requirements

To use miniogre effectively, ensure the following are installed:

- Python 3: Miniogre is developed in Python. If it's not already installed, [get Python here](https://www.python.org/downloads/).
- Docker: Docker is a platform used to eliminate "works on my machine" problems when collaborating on code with co-workers. If it's not already installed, [get Docker here](https://docs.docker.com/get-docker/).
- pip or pipx: These are python package installers used to install miniogre. If they are not already installed, [get pipx here](https://pipxproject.github.io/pipx/installation/) or [pip here](https://pip.pypa.io/en/stable/installing/).
- An API token of at least one of the following LLM inference providers:
    - `openai`: type `export OPENAI_API_KEY=<YOUR_TOKEN>` on the terminal;
    - `mistral`: type `export MISTRAL_API_KEY=<YOUR_TOKEN>` on the terminal;
    - `groq`: type `export GROQ_SECRET_ACCESS_KEY=<YOUR_TOKEN>` on the terminal;
    - `octoai`: type `export OCTOAI_TOKEN=<YOUR_TOKEN>` on the terminal.

OpenAI token in the environment:

## Installation
Miniogre can be installed either by using `pip` or `pipx`:
- `pip install miniogre`
- `pipx install miniogre`

You can also build the wheel from the source and then install it on your system. We provide a handy script `install.sh` to accomplish that.

## Usage

After installation, go inside the project folder and run:

`miniogre run`

This will analyze the project, generate `ogre_dir/Dockerfile`, `ogre_dir/requirements.txt`, and `ogre_dir/sbom.json` and build a Docker image.

### Commands
- `run`: Executes a series of actions, including configuring directories and files (bashrc, Dockerfile), generating requirements, building a Docker image, and spinning up a container.
- `readme`: Analyzes the source code to generate a new README.md file that reflects the actual operations in the source code.
- `eval`: Determines the reproducibility score of the repository by evaluating the README quality.
- `spinup`: Spins up a container if an image was previously built with the run command.
- `version`: Displays the current version of miniogre.

### Build Ogre base image

Useful to create a Docker image that can be deployed on Google Cloud Run:

`miniogre build-ogre-image --host-platform linux/amd64 --baseimage ogrerun/base:ubuntu22.04-amd64 --verbose --no-cache`

## Contributing
Contributions to improve this resource are more than welcome. For inquiries, contact the maintainers at [contact@ogre.run](contact@ogre.run).
