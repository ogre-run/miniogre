# Miniogre

**Miniogre** is a command-line application that analyzes a Python project codebase and README file to automatically generate a Dockerfile, requirements.txt file, and SBOM files. This tool expedites the process of dockerizing any Python application.

![miniogre_gif_33](https://github.com/ogre-run/miniogre/assets/6482944/0850dbb5-6634-4f08-80a9-6fd8e3ca8e03)

## How it Works

Upon running the application, it carries out the following steps:

- The project directory is scrutinized to identify the primary code language.
- The README file is located and read.
- GPT-4 language model is used to predict the application dependencies and generate content for the `requirements.txt` file based on the README contents.
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
- An OpenAI token in the environment: `export OPENAI_API_KEY=<YOUR_TOKEN>`

## Usage 

After installation, go inside the project folder and run:

`miniogre run`

This will analyze the project, generate `ogre_dir/Dockerfile`, `ogre_dir/requirements.txt`, and `ogre_dir/sbom.json` and build a Docker image.

There are other commands:

- `readme`: Analyzes the source code to generate a new `README.md` file that is compatible with what actually happens in the source code.  

## Installation
Miniogre can be installed either by using `pip` or `pipx`:
- `pip install miniogre`
- `pipx install miniogre`

## Contributing
Contributions to improve this resource are more than welcome. For inquiries, contact the maintainers at [contact@ogre.run](contact@ogre.run).
