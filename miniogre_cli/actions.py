import os
import typer
import docker
from openai import OpenAI
from dotenv import load_dotenv

client = OpenAI()

def list_files(project_path):
    # List all files in current directory
    files = os.listdir(project_path)
    return files

# Get file extensions
def get_extensions(files):
    extensions = [os.path.splitext(f)[1] for f in files]
    return extensions

# Count file extensions
def count_extensions(extensions):
    counts = {}
    for ext in extensions:
        if ext in counts:
            counts[ext] += 1
        else:
            counts[ext] = 1
    return counts

# Get main extension
def determine_most_ext(counts):
    main_lang = max(counts, key=counts.get)
    if main_lang in ['.md', '']:
        for ext in ['.md', '']:
            del counts[ext]
        main_lang = max(counts, key=counts.get)
    return main_lang

def find_readme(project_path):
    files = list_files(project_path)
    readme_files = [os.path.join(project_path, f) for f in files if f.lower().startswith('readme')]

    if readme_files:
        return readme_files[0]
    else:
        return None

def read_readme(path_to_readme):
    with open(path_to_readme, 'r') as f:
        contents = f.read()
    return contents

def extract_requirements(model, contents, prompt):
    completion = client.chat.completions.create(
                  model=model,
                  messages=[
                      {"role": "system", "content": prompt},
                      {"role": "user", "content": contents}
                  ]
              )
    requirements = completion.choices[0].message.content
    
    return requirements

def save_requirements(requirements, ogre_dir_path):
    requirements_fullpath = os.path.join(ogre_dir_path, 'requirements.txt')
    with open(requirements_fullpath, 'w') as f:
        f.write(requirements)
    return requirements_fullpath 

def build_docker_image(dockerfile, image_name):
    client = docker.from_env()

    # Read in Dockerfile contents
    with open(dockerfile, 'r') as f:
        dockerfile_contents = f.read()

    # Build Docker image
    image, logs = client.images.build(
        tag=image_name,
        path='.',
        dockerfile=dockerfile,
        rm=True
    )

    return image

    

