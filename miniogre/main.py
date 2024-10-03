import importlib.metadata
import os

import typer
from dotenv import load_dotenv
from openai import OpenAI

from .actions import *
from .agent.agent import agent as run_agent
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
    num_tokens = count_tokens(context_contents)
    print("Total number of tokens: {}".format(num_tokens))
    new_readme = rewrite_readme(provider, context_contents)
    readme_path = save_readme(new_readme, ogre_dir_path)
    end_emoji()

    return 0


@app.command()
def eval(provider: str = "openai", verbose: bool = False):
    """
    Determine the reproducibility score of the repository
    """

    display_figlet()
    starting_emoji()

    # Start by evaluating the README quality
    readme = read_readme(os.getcwd())
    readme_score = evaluate_readme(provider, readme, verbose)
    print(emoji.emojize(":upside-down_face: Readme score: {}".format(readme_score)))

    end_emoji()

    return 0


@app.command()
def run(
    provider: str = "openai",
    baseimage: str = "auto",
    port_map: str = "8001:8001",
    dry: bool = False,
    force_requirements_generation: bool = True,
    sbom_format: str = "pip-licenses",
    no_container: bool = False,
    verbose: bool = False,
    cache: bool = False,
    host_platform: str = None,
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
    ipynb_to_py_list = ipynb_to_py(project_path, verbose)
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
    if not dry:
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
    cleanup_converted_py(ipynb_to_py_list)
    if no_container == False:
        build_docker_image(
            os.path.join(ogre_dir_path, "Dockerfile"),
            project_name,
            host_platform,
            verbose,
            cache,
        )
        spin_up_container(project_name, project_path, port_map)
    end_emoji()


@app.command()
def spinup(port_map: str = "8001:8001"):
    """
    Spin up container if image was previously built with `run`
    """

    display_figlet()
    starting_emoji()

    project_name = os.path.basename(project_path)
    spin_up_container(project_name, project_path, port_map)

    end_emoji()


@app.command()
def build_ogre_image(
    baseimage: str = "auto",
    image_name: str = "baseimage",
    verbose: bool = False,
    cache: bool = False,
    host_platform: str = None,
):
    """
    Build miniogre baseimage
    """

    display_figlet()
    starting_emoji()

    if baseimage == "auto":
        baseimage = config_baseimage()

    ogre_dir_path = config_ogre_dir(
        os.path.join(project_path, os.getenv("OGRE_DIR", OGRE_DIR))
    )

    config_bashrc_baseimage(ogre_dir_path)
    config_ttyd_entrypoint(ogre_dir_path)
    secure_passphrase = config_dockerfile(
        project_path, "ogre", ogre_dir_path, baseimage, dry=False, base=True
    )
    build_docker_image(
        os.path.join(ogre_dir_path, "Dockerfile"),
        image_name,
        host_platform,
        verbose,
        cache,
    )

    print("Secure Passphrase for container user 'user':\n {}".format(secure_passphrase))

    end_emoji()


@app.command()
def cloud(
    destination: str = "https://fileserver.ogrerun.xyz",
):
    """
    Move local work to the cloud
    """

    display_figlet()
    starting_emoji()

    filename = create_tar(project_path, 'ogre-tarfile')
    res = send_tarfile_to_server(filename, destination)
    delete_tarfile(filename)


@app.command()
def agent(file_path: str, provider: str = "openai"):
    """
    Run miniogre agent on a file
    """

    display_figlet()
    starting_emoji()

    result = run_agent(file_path, provider)

    end_emoji()

if __name__ == "__main__":
    app()

