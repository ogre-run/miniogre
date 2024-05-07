import importlib.metadata
import os

import typer
from dotenv import load_dotenv
from openai import OpenAI

from .actions import *
from .config import *

app = typer.Typer()
load_dotenv()

project_path = os.getcwd()


@app.command()
def version():
    """
    Display version
    """
    version_string = importlib.metadata.version("miniogre")
    print("{}".format(version_string))

    return 0


@app.command()
def readme(provider: str = "openai"):
    """
    Rewrite readme
    """

    display_figlet()
    starting_emoji()

    ogre_dir_path = config_ogre_dir(
        os.path.join(project_path, os.getenv("OGRE_DIR", OGRE_DIR))
    )
    context_contents = run_gptify(os.getcwd())
    new_readme = rewrite_readme(provider, context_contents)
    readme_path = save_readme(new_readme, ogre_dir_path)
    end_emoji()

    return 0


@app.command()
def run(
    provider: str = "openai",
    baseimage: str = "auto",
    port: str = "8001",
    dry: bool = False,
    force_requirements_generation: bool = True,
    sbom_format: str = "pip-licenses",
    no_container: bool = False,
    verbose: bool = False,
    with_readme: bool = False,
):
    """
    Run full miniogre pipeline
    """

    display_figlet()
    starting_emoji()

    if baseimage == "auto":
        baseimage = config_baseimage()

    project_name = os.path.basename(project_path)

    files = list_files(project_path)
    extensions = get_extensions(files)
    counts = count_extensions(extensions)
    most_ext = determine_most_ext(counts)
    ogre_dir_path = config_ogre_dir(
        os.path.join(project_path, os.getenv("OGRE_DIR", OGRE_DIR))
    )
    if with_readme:
        context_contents = run_gptify(os.getcwd())
        new_readme = rewrite_readme(provider, context_contents)
        readme_path = save_readme(new_readme, ogre_dir_path)
    generate_requirements = config_requirements(
        project_path, ogre_dir_path, force_requirements_generation
    )
    local_requirements = extract_requirements_from_code(
        project_path, most_ext, generate_requirements
    )
    final_requirements = clean_requirements(provider, local_requirements)
    requirements_fullpath = save_requirements(final_requirements, ogre_dir_path)
    config_bashrc(project_path, ogre_dir_path, None, None, None)
    config_dockerfile(project_path, project_name, ogre_dir_path, baseimage, dry)
    create_sbom(project_name, project_path, sbom_format, verbose)
    if no_container == False:
        build_docker_image(
            os.path.join(ogre_dir_path, "Dockerfile"), project_name, verbose
        )
        spin_up_container(project_name, project_path, port)
    end_emoji()


@app.command()
def spinup(port: str = "8001"):
    """
    Spin up container if image was previously built with `run`
    """

    display_figlet()
    starting_emoji()

    project_name = os.path.basename(project_path)
    spin_up_container(project_name, project_path, port)

    end_emoji()


if __name__ == "__main__":
    app()
