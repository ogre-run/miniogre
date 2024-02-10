import os
import typer
import emoji
from openai import OpenAI
from dotenv import load_dotenv
from miniogre.actions import *
from miniogre.config import *


app = typer.Typer()
load_dotenv()

@app.command()
def requirements(model: str = 'gpt-3.5-turbo'):
    """
    Only generate requirements.txt 
    """

    project_path = os.getcwd()
    prompt = os.getenv('OPENAI_SECRET_PROMPT')

    files = list_files(project_path)
    extensions = get_extensions(files)
    counts = count_extensions(extensions)
    codebase = determine_most_ext(counts)
    readme_path = find_readme(project_path)
    readme_contents = read_readme(readme_path)
    ogre_dir_path = config_ogre_dir(os.path.join(project_path, os.getenv('OGRE_DIR')))
    requirements = extract_requirements(model, readme_contents, prompt)
    requirements_fullpath = save_requirements(requirements, ogre_dir_path)

    # print(codebase)
    # print(files)
    # print(extensions)
    # print(counts)
    # print(readme_path)
    # print(readme_contents)
    print(requirements)

    return 0

@app.command()
def build(model: str = os.getenv('OPENAI_MODEL'), 
        baseimage: str = os.getenv('OGRE_BASEIMAGE'),
        dry: bool = False):
    """
    Build docker image
    """
    print(emoji.emojize('Starting miniogre :ogre:'))

    project_path = os.getcwd()
    prompt = os.getenv('OPENAI_SECRET_PROMPT')

    project_name = os.path.basename(project_path)

    files = list_files(project_path)
    extensions = get_extensions(files)
    counts = count_extensions(extensions)
    codebase = determine_most_ext(counts)
    readme_path = find_readme(project_path)
    readme_contents = read_readme(readme_path)
    ogre_dir_path = config_ogre_dir(os.path.join(project_path, os.getenv('OGRE_DIR')))
    requirements = extract_requirements(model, readme_contents, prompt)
    save_requirements(requirements, ogre_dir_path)
    config_bashrc(project_path, ogre_dir_path, None, None, None)
    config_dockerfile(project_path, project_name, ogre_dir_path, baseimage, dry)
    build_docker_image(os.path.join(ogre_dir_path, "Dockerfile"), project_name, ogre_dir_path)


@app.command()
def run(model: str = os.getenv('OPENAI_MODEL'), 
        baseimage: str = os.getenv('OGRE_BASEIMAGE'),
        dry: bool = False):
    """
    Run miniogre
    """
    print(emoji.emojize('Starting miniogre :ogre:'))

    project_path = os.getcwd()
    prompt = os.getenv('OPENAI_SECRET_PROMPT')

    project_name = os.path.basename(project_path)

    files = list_files(project_path)
    extensions = get_extensions(files)
    counts = count_extensions(extensions)
    codebase = determine_most_ext(counts)
    readme_path = find_readme(project_path)
    readme_contents = read_readme(readme_path)
    ogre_dir_path = config_ogre_dir(os.path.join(project_path, os.getenv('OGRE_DIR')))
    requirements = extract_requirements(model, readme_contents, prompt)
    save_requirements(requirements, ogre_dir_path)
    config_bashrc(project_path, ogre_dir_path, None, None, None)
    config_dockerfile(project_path, project_name, ogre_dir_path, baseimage, dry)
    build_docker_image(os.path.join(ogre_dir_path, "Dockerfile"), project_name, ogre_dir_path)
    spin_up_container(project_name, project_path)


if __name__ == '__main__':
    app()