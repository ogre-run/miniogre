# miniogre

**miniogre** is a command-line tool that helps developers automate the process of setting up reproducible Python environments. It leverages AI to analyze a Python codebase and automatically generate necessary files such as `Dockerfile`, `requirements.txt`, and SBOM (Software Bill of Materials) files.  This simplifies packaging Python applications and significantly reduces the time spent on dependency management.  It can even update your README file to accurately reflect the current state of your project.

![miniogre_gif_33](https://github.com/ogre-run/miniogre/assets/6482944/0850dbb5-6634-4f08-80a9-6fd8e3ca8e03)

## Why miniogre?

Managing software dependencies is a tedious and time-consuming task for developers. This is especially problematic in AI/ML development, where rapidly evolving Python packages often have poor documentation or outdated configuration files.  miniogre addresses this issue by using AI to automate the dependency setup process. This reduces the time spent "dependency hunting" from hours to minutes, allowing developers to focus on writing code instead of wrestling with environments.

## How it Works

miniogre performs the following actions:

1. **Identifies the primary code language:**  miniogre analyzes the project directory. Currently optimized for Python projects.
2. **Reads the README file:** If a README exists, miniogre reads it to gather information about the project.
3. **Crawls the source code:**  The code is analyzed to identify import statements and extract a preliminary list of dependencies.
4. **Refines the requirements:**  miniogre leverages a Large Language Model (LLM) of your choice (OpenAI, Mistral, Groq, or OctoAI) to refine the dependency list and create a `requirements.txt` file.  The LLM helps to resolve complex dependencies and ensure compatibility. 
    * Note: current implementation uses `uv pip compile` to lock requirements, removing the need for an LLM cleaning step for dependency generation.
5. **Generates supporting files:** It generates a `Dockerfile` enabling containerization of your project and an SBOM (`sbom.json`) documenting all project dependencies.
6. **Builds a Docker image (optional):**  miniogre can build a Docker image of the application, facilitating easy deployment and sharing.
7. **Spins up a container (optional):**  miniogre can run the application in a Docker container.

## Requirements

- **Python 3.10 or higher:**  miniogre is written in Python and requires this version. [Download Python](https://www.python.org/downloads/).
- **Docker:**  Containerization platform for consistent environments. [Download Docker](https://docs.docker.com/get-docker/).
- **pipx (recommended) or pip:** Python package installers.  pipx is recommended for isolated installations.  [Download pipx](https://pipxproject.github.io/pipx/installation/).  [Download pip](https://pip.pypa.io/en/stable/installing/).
- **LLM API Key:** You need an API key for at least one of the following LLM providers:
    - **OpenAI:**  Set your API key using `export OPENAI_API_KEY=<YOUR_TOKEN>`.
    - **Mistral AI:** Set your API key using `export MISTRAL_API_KEY=<YOUR_TOKEN>`.
    - **Groq:** Set your API key using `export GROQ_SECRET_ACCESS_KEY=<YOUR_TOKEN>`.
    - **Ogre:** Set your token using `export OGRE_TOKEN=<YOUR_TOKEN>`.

## Installation

Miniogre can be installed using pipx or pip:

- With pipx (recommended): `pipx install miniogre`
- With pip: `pip install miniogre`

You can also build from source using Poetry: `poetry build && pipx install dist/*.whl` (or `pip install dist/*.whl`).  A helper script, `install.sh`, is provided in the repository to simplify this process.


## Usage

1. **Navigate to Project Directory:** Open your terminal and go to the root directory of your Python project.

2. **Run miniogre:** Use the following command to analyze your project and generate the reproducibility artifacts:

   ```bash
   miniogre run
   ```
By default, it will generate the `Dockerfile`, `requirements.txt`, and `sbom.json` in an `ogre_dir` directory, build a Docker image named `miniogre/<your_project_name>:latest`, and then start a container. You can customize the LLM provider, baseimage, port mapping and more using command-line options. If you don't want to build a container, simply add the `--no-container` flag.


### Commands
- `run`: Executes the full miniogre pipeline, generating required files, building a Docker image, and optionally spinning up a container.
- `readme`: Generates or updates the project's `README.md` file based on source code analysis.
- `eval`: Evaluates the quality of the project's README file on a scale of 1-10.
- `spinup`: Spins up a Docker container of the application if an image has already been built.
- `version`: Displays the installed version of miniogre.
- `build-ogre-image`: Builds a base Docker image with miniogre pre-installed (primarily for deployments to environments like Google Cloud Run).
- `cloud`: Sends the project folder as a tarball to a terminal server in the cloud (e.g. `terminal.ogre.run`).
- `ask`: Asks a question about the project or a code issue (still experimental).


## Contributing
Contributions are welcome!  For inquiries, contact [contact@ogre.run](mailto:contact@ogre.run).
