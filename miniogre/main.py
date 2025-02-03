import importlib.metadata
import platform
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
def ask(question: str = "",
        provider: str = "ogre"):
    """
    Ask question related to the project
    """

    display_figlet()
    starting_emoji()

    ogre_dir_path = config_ogre_dir(
        os.path.join(project_path, os.getenv("OGRE_DIR", OGRE_DIR))
    )

    context_contents = run_gptify(os.getcwd())
    num_tokens = count_tokens(context_contents)
    print("Total number of tokens: {}".format(num_tokens))

    # Send request to API
    answer = ask_miniogre(provider, context_contents, question)

    print(f"\nHere is the answer:\n\n{answer}")
    # TODO: Save answer in Google Storage

    end_emoji()

    return 0

@app.command()
def readme(provider: str = "ogre"):
    """
    Generate README file for the project
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
def docs(provider: str = "ogre"):
    """
    Generate and/or update comments in the entire source code.
    """

    display_figlet()
    starting_emoji()

    ogre_dir_path = config_ogre_dir(
        os.path.join(project_path, os.getenv("OGRE_DIR", OGRE_DIR))
    )

    # Go through all files
    for file_path, contents in walk_repo_and_return_contents(project_path):
        print(f'> Create comments for {file_path}')
        new_contents = write_comments(provider, contents)
        source_path = save_source(new_contents, file_path)

        remove_first_last_tags(source_path)
    
    end_emoji()

    return 0

@app.command()
def comment(provider: str = "ogre",
            filepath: str = "./main.py"):
    """
    Generate and/or update comments in an input file.
    """

    display_figlet()
    starting_emoji()

    ogre_dir_path = config_ogre_dir(
        os.path.join(project_path, os.getenv("OGRE_DIR", OGRE_DIR))
    )

    # Go through all files
    file_path, contents = return_file_contents(filepath)
    print(f'> Create comments for {file_path}')
    new_contents = write_comments(provider, contents)
    source_path = save_source(new_contents, file_path)

    remove_first_last_tags(source_path)
    end_emoji()

    return 0


@app.command()
def eval(provider: str = "ogre", verbose: bool = False):
    """
    [Beta] Determine the reproducibility score of the repository
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
    provider: str = "ogre",
    baseimage: str = "auto",
    port_map: str = "8001:8001",
    dry: bool = False,
    force_requirements_generation: bool = True,
    sbom_format: str = "pip-licenses",
    no_container: bool = False,
    verbose: bool = False,
    cache: bool = False,
    host_platform: str = "auto",
    with_readme: bool = False,
    device: str = "cpu"):
    """
    Run full miniogre pipeline
    """

    display_figlet()
    starting_emoji()

    project_name = os.path.basename(project_path)

    files = list_files(project_path)
    ipynb_to_py_list = ipynb_to_py(project_path, verbose)
    lang_frame = detect_language_and_framework(project_path)
    extensions = get_extensions(files)
    counts = count_extensions(extensions)
    most_ext = determine_most_ext(counts)
    ogre_dir_path = config_ogre_dir(
        os.path.join(project_path, os.getenv("OGRE_DIR", OGRE_DIR))
    )
    if with_readme:
        context_contents = run_gptify(os.getcwd())
        num_tokens = count_tokens(context_contents)
        print("Total number of tokens: {}".format(num_tokens))
        new_readme = rewrite_readme(provider, context_contents)
        readme_path = save_readme(new_readme, ogre_dir_path)
    if not dry:
        generate_requirements = config_requirements(
            project_path, ogre_dir_path, force_requirements_generation
        )
        local_requirements = extract_requirements_from_code(
            project_path, most_ext, generate_requirements, verbose
        )
        
        # Remove cleaning with LLM and lock requirements
        final_requirements = lock_requirements(local_requirements)

        # final_requirements = clean_requirements(provider, local_requirements)
        requirements_fullpath = save_requirements(final_requirements, ogre_dir_path)
    config_bashrc(project_path, ogre_dir_path, None, None, None)

    if host_platform == 'auto':
        platform_machine = "{}".format(platform.machine())
    else:
        platform_machine = host_platform

    if baseimage == "auto":
        baseimage_name = config_baseimage(lang_frame['framework'], platform_machine)
    else:
        baseimage_name = baseimage
    config_dockerfile(project_path, project_name, lang_frame['framework'],
                      ogre_dir_path, baseimage_name, dry)
    create_sbom(project_name, project_path, sbom_format, verbose)
    cleanup_converted_py(ipynb_to_py_list)
    if no_container == False:
        build_docker_image(
            os.path.join(ogre_dir_path, "Dockerfile"),
            project_name,
            platform_machine,
            verbose,
            cache,
        )
        spin_up_container(project_name, 
                          project_path, 
                          port_map, 
                          lang_frame['framework'], 
                          device)
    end_emoji()


@app.command()
def spinup(port_map: str = "8001:8001",
           device: str = "cpu"):
    """
    Spin up container if image was previously built with `run`
    """

    display_figlet()
    starting_emoji()

    project_name = os.path.basename(project_path)
    lang_frame = detect_language_and_framework(project_path)
    spin_up_container(project_name, 
                      project_path, 
                      port_map, 
                      lang_frame['framework'], 
                      device)
    end_emoji()


@app.command()
def build_ogre_image(
    baseimage: str = "auto",
    image_name: str = "baseimage",
    verbose: bool = False,
    cache: bool = False,
    host_platform: str = "auto",
):
    """
    Build miniogre baseimage
    """

    display_figlet()
    starting_emoji()

    if host_platform == "auto":
        platform_machine = "{}".format(platform.machine())
    else:
        platform_machine = host_platform

    if baseimage == "auto":
        baseimage_name = config_baseimage(None, platform_machine)
    else:
        baseimage_name = baseimage

    ogre_dir_path = config_ogre_dir(
        os.path.join(project_path, os.getenv("OGRE_DIR", OGRE_DIR))
    )

    config_bashrc_baseimage(ogre_dir_path)
    config_ttyd_entrypoint(ogre_dir_path)
    secure_passphrase = config_dockerfile(
        project_path, "ogre", None, ogre_dir_path, baseimage_name, dry=False, base=True
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
    proxy: str = "https://fileserver.ogrerun.xyz",
):
    """
    Move local project folder to an enviroment in another computer.
    Ideally, that computer has more computational power and you can continously run
    a service from there (that's why one would use the cloud).

    Proxy is just a service that process your project folder using a standalone
    version of miniogre. It generates the reproducibility artifacts (e.g. README).

    Once the processing is done, a tarball of your project containing the artifacts
    is generated and stored somewhere (that's up to the proxy to define that).

    For example, if you use th default proxy above, the tarball is temporarily stored
    in the proxy filesystem and then relayed to a cloud terminal in (terminal.ogre.run).
    After that, the tarball is deleted.

    You can create your own proxy with your own rules (instructions TBD).
    """

    display_figlet()
    starting_emoji()

    filename = create_tar(project_path, 'ogre-tarfile')
    res = send_tarfile_to_server(filename, proxy)
    delete_tarfile(filename)

if __name__ == "__main__":
    app()
