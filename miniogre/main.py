import os
import typer
from openai import OpenAI
from dotenv import load_dotenv
from miniogre.actions import *
from miniogre.config import *


app = typer.Typer()
load_dotenv()

project_path = os.getcwd()
prompt = os.getenv('OPENAI_SECRET_PROMPT')

@app.command()
def requirements(model: str = 'gpt-3.5-turbo',
                 limit_source_files: int = 1):
    """
    Only generate requirements.txt 
    """

    display_figlet()
    display_emoji()
    global project_path, prompt

    ogre_dir_path = config_ogre_dir(os.path.join(project_path, os.getenv('OGRE_DIR')))
    files = list_files(project_path)
    extensions = get_extensions(files)
    counts = count_extensions(extensions)
    print(counts)
    most_ext = determine_most_ext(counts)
    print(most_ext)
    input()
    readme_path = find_readme(project_path)
    readme_contents = read_file_contents(readme_path)
    #source_contents = append_files_with_ext(project_path, most_ext, limit_source_files, 
    #                                        "{}/source_contents.txt".format(ogre_dir_path))
    pre_requirements = extract_requirements_from_code(project_path, most_ext)
    #context_contents = generate_context_file(readme_contents, source_contents, 
    #                                         "{}/context_file.txt".format(ogre_dir_path))
    requirements = extract_requirements(model, readme_contents, prompt)
    
    requirements_fullpath = save_requirements(requirements, ogre_dir_path)

    # print("> list of requirements: \n")
    # for req in requirements:
    #     print(req)

    return 0

@app.command()
def build(model: str = os.getenv('OPENAI_MODEL'), 
        baseimage: str = 'auto',
        dry: bool = False,
        limit_source_files: int = 5):
    """
    Build docker image
    """
    display_figlet()
    display_emoji()

    if baseimage == 'auto':
        baseimage = config_baseimage()
    
    project_path = os.getcwd()
    prompt = os.getenv('OPENAI_SECRET_PROMPT')

    ogre_dir_path = config_ogre_dir(os.path.join(project_path, os.getenv('OGRE_DIR')))
    files = list_files(project_path)
    extensions = get_extensions(files)
    counts = count_extensions(extensions)
    most_ext = determine_most_ext(counts)
    readme_path = find_readme(project_path)
    readme_contents = read_file_contents(readme_path)
    #source_contents = append_files_with_ext(project_path, most_ext, limit_source_files, 
    #                                        "{}/source_contents.txt".format(ogre_dir_path))
    #context_contents = generate_context_file(readme_contents, source_contents, 
    #                                         "{}/context_file.txt".format(ogre_dir_path))
    pre_requirements = extract_requirements_from_code(project_path, most_ext)
    requirements = extract_requirements(model, readme_contents, prompt)
    requirements_fullpath = save_requirements(requirements, ogre_dir_path)

    project_name = os.path.basename(project_path)
    config_bashrc(project_path, ogre_dir_path, None, None, None)
    config_dockerfile(project_path, project_name, ogre_dir_path, baseimage, dry)
    build_docker_image(os.path.join(ogre_dir_path, "Dockerfile"), project_name, ogre_dir_path)


@app.command()
def run(model: str = os.getenv('OPENAI_MODEL'), 
        baseimage: str = 'auto',
        dry: bool = False):
    """
    Run miniogre
    """
    display_figlet()
    display_emoji()

    if baseimage == 'auto':
        baseimage = config_baseimage()

    project_path = os.getcwd()
    prompt = os.getenv('OPENAI_SECRET_PROMPT')

    project_name = os.path.basename(project_path)

    files = list_files(project_path)
    extensions = get_extensions(files)
    counts = count_extensions(extensions)
    most_ext = determine_most_ext(counts)
    readme_path = find_readme(project_path)
    readme_contents = read_file_contents(readme_path)
    ogre_dir_path = config_ogre_dir(os.path.join(project_path, os.getenv('OGRE_DIR')))
    pre_requirements = extract_requirements_from_code(project_path, most_ext)
    requirements = extract_requirements(model, readme_contents, prompt)
    requirements_fullpath = save_requirements(requirements, ogre_dir_path)
    create_virtualenv(requirements, "3.9")
    #config_bashrc(project_path, ogre_dir_path, None, None, None)
    #config_dockerfile(project_path, project_name, ogre_dir_path, baseimage, dry)
    #build_docker_image(os.path.join(ogre_dir_path, "Dockerfile"), project_name, ogre_dir_path)
    #spin_up_container(project_name, project_path)


if __name__ == '__main__':
    app()