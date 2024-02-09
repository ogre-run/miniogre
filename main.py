import os
import typer
from openai import OpenAI
from dotenv import load_dotenv
from miniogre_cli.actions import *
from miniogre_cli.config import *


app = typer.Typer()
load_dotenv()

@app.command()
def requirements(project: str,
                 model: str = 'gpt-3.5-turbo'):
    """
    Only generate requirements.txt 
    """

    project_path = project
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
def run(project: str,
        model: str = os.getenv('OPENAI_MODEL'), 
        baseimage: str = os.getenv('OGRE_BASEIMAGE'),
        dry: bool = False):
    """
    Run miniogre
    """
    
    project_path = project
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


if __name__ == '__main__':
    app()
    

    # parser = argparse.ArgumentParser()
    # parser.add_argument('-p', '--project_path', required=True, help='path to project directory')
    # args = parser.parse_args()
    
    # project_path = args.project_path

    

