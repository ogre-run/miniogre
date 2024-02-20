import os
import typer
from openai import OpenAI
from dotenv import load_dotenv
from .actions import *
from .config import *


app = typer.Typer()
load_dotenv()

project_path = os.getcwd()
prompt = os.getenv('OPENAI_SECRET_PROMPT')
prompt_rewrite_readme = os.getenv('PROMPT_REWRITE_README')

@app.command()
def readme(model: str = os.getenv('OPENAI_MODEL'),
                  limit_source_files: int = 1):
    """
    Rewrite readme
    """

    display_figlet()
    display_emoji()
    #global project_path, prompt, 

    ogre_dir_path = config_ogre_dir(os.path.join(project_path, os.getenv('OGRE_DIR')))
    files = list_files(project_path)
    extensions = get_extensions(files)
    counts = count_extensions(extensions)
    most_ext = determine_most_ext(counts)
    readme_path = find_readme(project_path)
    readme_contents = read_file_contents(readme_path)
    source_contents = append_files_with_ext(project_path, most_ext, limit_source_files, 
                                            "{}/source_contents.txt".format(ogre_dir_path))
    pre_requirements = extract_requirements_from_code(project_path, most_ext)
    context_contents = generate_context_file(readme_contents, source_contents, 
                                             "{}/context_file.txt".format(ogre_dir_path))
    requirements = extract_requirements(model, readme_contents, prompt)
    new_readme = rewrite_readme(model, context_contents, prompt_rewrite_readme)
    
    print(new_readme)

    #requirements_fullpath = save_requirements(requirements, ogre_dir_path)

    # print("> list of requirements: \n")
    # for req in requirements:
    #     print(req)

    return 0

@app.command()
def run(model: str = os.getenv('OPENAI_MODEL'), 
        baseimage: str = 'auto',
        port: str = '8001',
        dry: bool = False,
        sbom_format: str = 'pip-licenses'):
    """
    Run miniogre
    """
    display_figlet()
    starting_emoji()

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
    config_bashrc(project_path, ogre_dir_path, None, None, None)
    config_dockerfile(project_path, project_name, ogre_dir_path, baseimage, dry)
    build_docker_image(os.path.join(ogre_dir_path, "Dockerfile"), project_name, ogre_dir_path)
    create_sbom(project_name, project_path, sbom_format)
    end_emoji()
    spin_up_container(project_name, project_path, port)

if __name__ == '__main__':
    app()