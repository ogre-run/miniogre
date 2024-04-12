import os
import ast
import emoji
import platform
import subprocess
from openai import OpenAI
from octoai.client import Client as OctoAiClient
from groq.cloud.core import Completion
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from pyfiglet import Figlet
from rich import print as rprint
from yaspin import yaspin
from .constants import *


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

def cleaning_requirements_emoji():
    print(emoji.emojize(':cooking: Refining...'))

def readme_emoji():
    print(emoji.emojize(':notebook: Generating new README.md...'))

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
    if path_to_file == None:
        return ''
    else:
        if os.path.exists(path_to_file):
            with open(path_to_file, 'r') as f:
                contents = f.read()
            return contents
        else:
            return ''

def conform_to_pep8(filename):

    pep8_cmd = 'autopep8 --in-place --aggressive {}'.format(filename)
    
    p = subprocess.Popen(pep8_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = p.communicate()
    p_status = p.wait()

    return 0

def extract_external_imports(code):

    external_imports = []
    
    tree = ast.parse(code)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                if not name.name.startswith('.'):
                    external_imports.append(name.name)
        elif isinstance(node, ast.ImportFrom):
            if not node.module.startswith('.'):
                external_imports.append(node.module)
   
    return external_imports

def extract_requirements_from_code(project_path, ext, generate = True):

    requirements_emoji()

    if generate:
        files = list_files(project_path)
        matching = [f for f in files if os.path.splitext(f)[1] == ext]

        external_imports = []
        for filename in matching:
            i = 0
            while i < 2:
                with open(os.path.join(project_path, filename), 'r') as readfile:
                    content = readfile.read()
                    try:
                        external_imports.append(extract_external_imports(content))
                        i = 2
                    except Exception as e:
                        if i == 1:
                            i = 2
                            print(e)
                            print("External imports extraction failed for file {}: {}".format(filename, Exception))
                        else:
                            conform_to_pep8(filename)
                            i += 1
                
        external_imports = [imp.split('.')[0] for sublist in external_imports for imp in sublist]
        external_imports = list(set(external_imports))

        requirements = '\n'.join(external_imports)
    else:
        with open('{}/requirements.txt'.format(os.getenv('OGRE_DIR')), 'r') as f:
            requirements = f.read()
    return requirements



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

def extract_requirements(provider, contents):
    requirements_emoji()
    if provider == 'openai':
        res = extract_requirements_openai(contents)
    elif provider == 'octoai':
        res = extract_requirements_octoai(contents)
    elif provider == 'groq':
        res = extract_requirements_groq(contents)
    return res

def extract_requirements_openai(contents):
    model = os.getenv('OPENAI_MODEL')
    prompt = os.getenv('OPENAI_SECRET_PROMPT')
    client = OpenAI()
    completion = client.chat.completions.create(
                  model=model,
                  messages=[
                      {"role": "system", "content": prompt},
                      {"role": "user", "content": contents}
                  ]
              )
    requirements = completion.choices[0].message.content
    
    return requirements

def extract_requirements_octoai(contents):
    model = os.getenv('OCTOAI_MODEL')
    prompt = os.getenv('OCTOAI_SECRET_PROMPT')
    client = OctoAiClient()

    completion = client.chat.completions.create(
    messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": contents
            }
        ],
    model=model,
    max_tokens=20000,
    presence_penalty=0,
    temperature=0.1,
    top_p=0.9)

    requirements = completion.choices[0].message.content

    return requirements

def extract_requirements_groq(contents):
    prompt = os.getenv('GROQ_SECRET_PROMPT')
    with Completion() as completion:
        full_prompt = prompt + " " + contents
        response, id, stats = completion.send_prompt("llama2-70b-4096", user_prompt=full_prompt)
        if response != "":
            print(f"\nPrompt: {prompt}\n")
            print(f"Request ID: {id}")
            print(f"Output:\n {response}\n")
            print(f"Stats:\n {stats}\n")
    return response

def clean_requirements(provider, requirements):
    cleaning_requirements_emoji()
    if provider == 'openai':
        res = clean_requirements_openai(requirements)
    elif provider == 'octoai':
        res = clean_requirements_octoai(requirements)
    elif provider == 'groq':
        res = clean_requirements_groq(requirements)
    elif provider == 'mistral':
        res = clean_requirements_mistral(requirements)
    return res

def clean_requirements_openai(requirements):
    model = os.getenv('OPENAI_MODEL')
    prompt = os.getenv('CLEAN_REQUIREMENTS_SECRET_PROMPT')
    client = OpenAI()
    completion = client.chat.completions.create(
                  model=model,
                  messages=[
                      {"role": "system", "content": prompt},
                      {"role": "user", "content": requirements}
                  ]
              )
    requirements = completion.choices[0].message.content

    return requirements

def clean_requirements_mistral(requirements):
    model = os.getenv('MISTRAL_MODEL')
    prompt = os.getenv('CLEAN_REQUIREMENTS_SECRET_PROMPT')
    api_key = os.environ["MISTRAL_API_KEY"]
    client = MistralClient(api_key=api_key)
    content = prompt + '\n' + requirements
    messages = [ChatMessage(role="user", content=content)]

    # No streaming
    chat_response = client.chat(
        model=model,
        messages=messages,
    )
    requirements = chat_response.choices[0].message.content

    return requirements

def clean_requirements_groq(requirements):
    model = os.getenv('GROQ_MODEL')
    prompt = os.getenv('GROQ_CLEAN_REQUIREMENTS_SECRET_PROMPT')
    with Completion() as completion:
        full_prompt = prompt + " " + requirements
        response, id, stats = completion.send_prompt(model, user_prompt=full_prompt)
        
    return response

def clean_requirements_octoai(requirements):
    model = os.getenv('OCTOAI_MODEL')
    prompt = os.getenv('CLEAN_REQUIREMENTS_SECRET_PROMPT')
    client = OctoAiClient()

    completion = client.chat.completions.create(
        messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": requirements
                }
            ],
        model=model,
        max_tokens=20000,
        presence_penalty=0,
        temperature=0.1,
        top_p=0.9)

    requirements = completion.choices[0].message.content

    return requirements

def save_requirements(requirements, ogre_dir_path):
    requirements_fullpath = os.path.join(ogre_dir_path, 'requirements.txt')
    with open(requirements_fullpath, 'w') as f:
        f.write(requirements)
    return requirements_fullpath 

def rewrite_readme(provider, readme):
    readme_emoji()
    if provider == 'openai':
        res = rewrite_readme_openai(readme)
    elif provider == 'octoai':
        res = rewrite_readme_octoai(readme)
    elif provider == 'groq':
        res = rewrite_readme_groq(readme)
    elif provider == 'mistral':
        res = rewrite_readme_mistral(readme)
    return res

def rewrite_readme_openai(readme):
    model = os.getenv('OPENAI_MODEL')
    prompt = os.getenv('REWRITE_README_PROMPT')
    client = OpenAI()
    if 'OPENAI_API_KEY' not in os.environ:
        raise EnvironmentError("OPENAI_API_KEY environment variable not defined")
    
    try:
        completion = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": prompt},
                            {"role": "user", "content": readme}
                        ]
                    )
        new_readme = completion.choices[0].message.content
    except Exception as e:
        print(e)

    return new_readme

def rewrite_readme_octoai(readme):
    raise NotImplementedError("rewrite_readme_octoai is not implemented.")

def rewrite_readme_groq(readme):
    raise NotImplementedError("rewrite_readme_groq is not implemented.")

def rewrite_readme_mistral(readme):
    model = os.getenv('MISTRAL_MODEL')
    prompt = os.getenv('REWRITE_README_PROMPT')
    api_key = os.environ["MISTRAL_API_KEY"]
    client = MistralClient(api_key=api_key)
    content = prompt + '\n' + readme
    messages = [ChatMessage(role="user", content=content)]
    
    # No streaming
    chat_response = client.chat(
        model=model,
        messages=messages,
    )
    requirements = chat_response.choices[0].message.content

    return requirements

def save_readme(readme, ogre_dir_path):
    readme_fullpath = os.path.join(ogre_dir_path, 'README.md')
    with open(readme_fullpath, 'w') as f:
        f.write(readme)
    return readme_fullpath 

def build_docker_image(dockerfile, image_name, verbose = False):
    # build docker image
    
    platform_name = "linux/{}".format(platform.machine())
    image_name = "miniogre/{}:{}".format(image_name.lower(), "latest")

    build_emoji()
    print("   platform = {}".format(platform_name)) 
    print("   image name = {}".format(image_name))
    
    if verbose:
        stderr = None
        progress = 'plain'
    else:
        stderr = subprocess.PIPE
        progress = 'auto'

    build_cmd = (
        "DOCKER_BUILDKIT=1 docker buildx build --no-cache --load --progress={} --platform {} -t {} -f {} .".format(
            progress, platform_name, image_name, dockerfile
        )
    )
    print("   build command = {}".format(build_cmd))

    if verbose:
        p = subprocess.Popen(build_cmd, stdout=subprocess.PIPE, stderr=stderr, shell=True)
        (out, err) = p.communicate()
        p_status = p.wait()
    else:
        with yaspin().aesthetic as sp:
            sp.text = "generating ogre environment" 
            p = subprocess.Popen(build_cmd, stdout=subprocess.PIPE, stderr=stderr, shell=True)
            (out, err) = p.communicate()
            p_status = p.wait()
    return out

def spin_up_container(image_name, project_path, port):
    # spin up container
    spinup_emoji()

    project_name = image_name
    container_name = "miniogre-{}".format(image_name.lower())
    image_name = "miniogre/{}:{}".format(image_name.lower(), "latest")
    #cmd = "uv venv; source .venv/bin/activate; cat ./{}/requirements.txt | xargs -L 1 uv pip install; exit 0;"
    #cmd = "cat ./ogre_dir/requirements.txt | xargs -L 1 uv pip install; exit 0"
    spin_up_cmd = (
        "docker run -it --rm -v {}:/opt/{} -p {}:{} --name {} {}".format(project_path, project_name, port, port, container_name, image_name)  
    )

    print("   spin up command = {}".format(spin_up_cmd))
    subprocess.call(spin_up_cmd.split())
    #p = subprocess.Popen(spin_up_cmd, stdout=subprocess.PIPE, shell=True)
    #(out, err) = p.communicate()
    #p_status = p.wait()

    return 0

def create_sbom(image_name, project_path, format, verbose = False):
    # Create SBOM from inside the container
    print(emoji.emojize(':desktop_computer:  Generating SBOM...'))

    project_name = image_name
    container_name = "miniogre-{}".format(image_name.lower())
    image_name = "miniogre/{}:{}".format(image_name.lower(), "latest")

    if format == 'cyclonedx':
        sbom_format_cmd = "cyclonedx-py requirements ./ogre_dir/requirements.txt &> ./ogre_dir/sbom.json"
    elif format == 'pip-licenses':
        sbom_format_cmd = "pip-licenses --with-authors --with-maintainers --with-urls --with-description -l --format json --output-file ./ogre_dir/sbom.json"

    # sbom_cmd = (
    #     "   docker run -d --rm -v {}:/opt/{} --name {}_sbom {} bash -c '{}; wait'".format(project_path, project_name, container_name, image_name, sbom_format_cmd)  
    # )
    sbom_cmd = sbom_format_cmd
    
    if verbose:
        stderr = None
        print(sbom_cmd)
    else:
        stderr = subprocess.PIPE
    p = subprocess.Popen(sbom_cmd, stdout=subprocess.PIPE, stderr=stderr, shell=True)
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

def run_gptify(repo_path):
    
    gptrepo_cmd = 'gptify {}'.format(repo_path)
    p = subprocess.Popen(gptrepo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = p.communicate()
    p_status = p.wait()

    print("generated gptify_output")

    with open('gptify_output.txt', 'r') as f:
        return f.read()
