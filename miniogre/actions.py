import os
import emoji
import platform
import subprocess
import xmlrpc.client
import pkg_resources
from openai import OpenAI
from pyfiglet import Figlet
from rich import print as rprint
from yaspin import yaspin
from .constants import *


client = OpenAI()

def list_files(project_path):
    # List all files in current directory and subdirectories
    files = []
    for root, dirs, filenames in os.walk(project_path):
        if '.git' in dirs:
            dirs.remove('.git')
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
        for filename in filenames:
            files.append(os.path.join(root, filename))
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

# Get most prevalent extension for code files
def determine_most_ext(counts):
    #TODO: implement logic to determine the codebase.    
    return '.py'

def find_readme(project_path):
    files = list_files(project_path)
    readme_files = [f for f in files if os.path.basename(f).lower().startswith('readme')]

    if readme_files:
        return readme_files[0]
    else:
        return None

def read_file_contents(path_to_file):
    if os.path.exists(path_to_file):
        with open(path_to_file, 'r') as f:
            contents = f.read()
        return contents
    else:
        return None

import ast

def extract_external_imports(code):
    tree = ast.parse(code)
    external_imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                if not name.name.startswith('.'):
                    external_imports.append(name.name)
        elif isinstance(node, ast.ImportFrom):
            if not node.module.startswith('.'):
                external_imports.append(node.module)
    
    return external_imports

def extract_requirements_from_code(project_path, ext):
    
    files = list_files(project_path)
    matching = [f for f in files if os.path.splitext(f)[1] == ext]

    external_imports = []
    for filename in matching:
        with open(os.path.join(project_path, filename), 'r') as readfile:
            content = readfile.read()
            try:
                external_imports.append(extract_external_imports(content))
            except Exception:
                print("External imports extraction failed for file {}: {}".format(filename, Exception))
    external_imports = [imp for sublist in external_imports for imp in sublist]
    external_imports = list(set(external_imports))

    return external_imports

def append_files_with_ext(project_path, ext, limit, output_file):
    files = list_files(project_path)
    matching = [f for f in files if os.path.splitext(f)[1] == ext]
    
    if limit < len(matching):
        matching = matching[:limit]
        
    contents = ''
    with open(output_file, 'a') as outfile:
        for filename in matching:
            with open(os.path.join(project_path, filename), 'r') as readfile:
                contents += readfile.read()

    return contents

def generate_context_file(readme_text, source_text, output_file):
    """
    Generates the context file by appending the README and the source code text. 
    The content of this file will be used to extract the dependencies.
    """
    out_text = readme_text + source_text
    
    with open(output_file, 'w') as out:
        out.write(out_text)
    
    with open(output_file, 'r') as f:
        return f.read()

def read_context(path_to_context_file):
    with open(path_to_context_file, 'r') as f:
        contents = f.read()
    return contents

def extract_requirements(model, contents, prompt):
    requirements_emoji()
    completion = client.chat.completions.create(
                  model=model,
                  messages=[
                      {"role": "system", "content": prompt},
                      {"role": "user", "content": contents}
                  ]
              )
    requirements = completion.choices[0].message.content
    
    return requirements

def rewrite_readme(model, contents, prompt):
    completion = client.chat.completions.create(
                  model=model,
                  messages=[
                      {"role": "system", "content": prompt},
                      {"role": "user", "content": contents}
                  ]
              )
    new_readme = completion.choices[0].message.content
    
    return new_readme

def extract_requirements_groq(contents, prompt):
    print("> groq")
    with Completion() as completion:
        full_prompt = prompt + " " + contents
        response, id, stats = completion.send_prompt("llama2-70b-4096", user_prompt=full_prompt)
        if response != "":
            print(f"\nPrompt: {prompt}\n")
            print(f"Request ID: {id}")
            print(f"Output:\n {response}\n")
            print(f"Stats:\n {stats}\n")

def save_requirements(requirements, ogre_dir_path):
    requirements_fullpath = os.path.join(ogre_dir_path, 'requirements.txt')
    with open(requirements_fullpath, 'w') as f:
        f.write(requirements)
        
    return requirements_fullpath 

def build_docker_image(dockerfile, image_name, ogre_dir_path):
    # build docker image
    
    platform_name = "linux/{}".format(platform.machine())
    image_name = "miniogre/{}:{}".format(image_name.lower(), "latest")

    build_emoji()
    print("   platform = {}".format(platform_name)) 
    print("   image name = {}".format(image_name))
    
    build_cmd = (
        "DOCKER_BUILDKIT=1 docker buildx build --load --progress=auto --platform {} -t {} -f {} .".format(
            platform_name, image_name, dockerfile
        )
    )
    print("   build command = {}".format(build_cmd))
    with yaspin().aesthetic as sp:
        sp.text = "generating ogre environment" 
        p = subprocess.Popen(build_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate()
        p_status = p.wait()

    return out

def spin_up_container(image_name, project_path, port):
    # spin up container
    spinup_emoji()

    project_name = image_name
    container_name = "miniogre-{}".format(image_name.lower())
    image_name = "miniogre/{}:{}".format(image_name.lower(), "latest")
    
    spin_up_cmd = (
        "docker run -it --rm -v {}:/opt/{} -p {}:{} --name {} {}".format(project_path, project_name, port, port, container_name, image_name)  
    )

    print("   spin up command = {}".format(spin_up_cmd))
    subprocess.call(spin_up_cmd.split())
    #p = subprocess.Popen(spin_up_cmd, stdout=subprocess.PIPE, shell=True)
    #(out, err) = p.communicate()
    #p_status = p.wait()

    return 0

def create_sbom(image_name, project_path, format):
    # Create SBOM from inside the container
    print(emoji.emojize(':desktop_computer:  Generating SBOM...'))

    project_name = image_name
    container_name = "miniogre-{}".format(image_name.lower())
    image_name = "miniogre/{}:{}".format(image_name.lower(), "latest")

    if format == 'cyclonedx':
        sbom_format_cmd = "cyclonedx-py requirements ./ogre_dir/requirements.txt &> ./ogre_dir/sbom.json"
    elif format == 'pip-licenses':
        sbom_format_cmd = "pip-licenses --with-authors --with-maintainers --with-urls --with-description -l --format json --output-file ./ogre_dir/sbom.json"

    sbom_cmd = (
        "   docker run -d --rm -v {}:/opt/{} --name {}_sbom {} bash -c '{}; wait'".format(project_path, project_name, container_name, image_name, sbom_format_cmd)  
    )
    
    print(sbom_cmd)
    p = subprocess.Popen(sbom_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    p.communicate()
    p.wait()

    return 0
    
def display_figlet():
    # Display Ogre figlet
    f = Figlet(font="slant")
    # Get version
    # ogre_version = pkg_resources.get_distribution('miniogre').version
    rprint("[cyan] {} [/cyan]".format(f.renderText("miniogre")))
    rprint("[blue bold]miniogre - {}[/blue bold]".format("https://ogre.run"))
    print("\n")
    
def starting_emoji():
    print(emoji.emojize(':ogre: Starting miniogre...'))

def end_emoji():
    print(emoji.emojize(':hourglass_done: Done.'))

def build_emoji():
    print(emoji.emojize(':spouting_whale: Building Docker image...'))

def spinup_emoji():
    print(emoji.emojize(':rocket: Spinning up container...'))

def requirements_emoji():
    print(emoji.emojize(':thinking_face: Generating requirements...'))

def create_virtualenv(requirements, python_version):
  
    env_name = 'miniogre-env'

    venv_cmd = "python -m venv {}".format(env_name)
    # venv_activate_cmd = 'source {}/bin/activate'.format(env_name) 

    #os.popen(venv_cmd)
    #os.popen(venv_activate_cmd)
    p = subprocess.Popen(venv_cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = p.communicate()
    p_status = p.wait()

    venv_activate_cmd = 'source {}/bin/activate'.format(env_name)
    p = subprocess.Popen(venv_activate_cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = p.communicate()
    p_status = p.wait()

    pip_cmd = '{}/bin/pip'.format(env_name)
    with open(requirements) as f:
        requirements_list = []
        for line in f:
            requirements_list.append(line.strip('\n'))

        pip_cmd = 'pip' 
        for req in requirements_list:
            print(req)
            input()
            subprocess.call([pip_cmd, 'install', req.strip()])


