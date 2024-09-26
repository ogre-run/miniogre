import json
import ast
import glob
import os
import platform
import subprocess
import tarfile
import requests
import uuid
from string import Template

import emoji
import google.generativeai as googleai
import tiktoken
from groq import Groq
# from groq.cloud.core import Completion
#from mistralai.client import MistralClient
#from mistralai.models.chat_completion import ChatMessage
from octoai.client import Client as OctoAiClient
from openai import OpenAI
from pyfiglet import Figlet
from rich import print as rprint
from yaspin import yaspin
from ollama import Client

from .constants import *


def starting_emoji():
    print(emoji.emojize(":ogre: Starting miniogre..."))


def end_emoji():
    print(emoji.emojize(":hourglass_done: Done."))


def build_emoji():
    print(emoji.emojize(":spouting_whale: Building Docker image..."))


def spinup_emoji():
    print(emoji.emojize(":rocket: Spinning up container..."))


def requirements_emoji():
    print(emoji.emojize(":thinking_face: Generating requirements..."))


def cleaning_requirements_emoji():
    print(emoji.emojize(":cooking: Refining..."))


def generate_context_emoji():
    print(emoji.emojize(":magnifying_glass_tilted_left: Generating context..."))


def readme_emoji():
    print(emoji.emojize(":notebook: Generating new README.md..."))


def eval_emoji():
    print(emoji.emojize(":magnifying_glass_tilted_left: Evaluating..."))


def list_files(project_path):
    # List all files in current directory and subdirectories
    files = []
    for root, dirs, filenames in os.walk(project_path):
        if ".git" in dirs:
            dirs.remove(".git")
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")
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


def ipynb_to_py(project_path, verbose=False):
    """
    Convert ipynb files (jupyter notebooks) to python scripts.
    """

    ipynbfiles = []

    pattern_ipynb = glob.glob(
        os.path.join("{}".format(project_path), "**/", "*.ipynb"),
        recursive=True,
    )

    if verbose:
        stderr = None
        progress = "plain"
    else:
        stderr = subprocess.PIPE
        progress = "auto"

    for filename in pattern_ipynb:
        # subprocess to convert notebook to python
        convert_cmd = 'jupyter nbconvert --to python "{}"'.format(filename)
        p = subprocess.Popen(
            convert_cmd, stdout=subprocess.PIPE, stderr=stderr, shell=True
        )
        (out, err) = p.communicate()
        p_status = p.wait()

        filename_py = filename[:-5] + "py"
        ipynbfiles.append(filename_py)

    return ipynbfiles


def cleanup_converted_py(ipynb_to_py_list):
    # Loop through the list and remove each file
    if not ipynb_to_py_list:
        print(
            "There were no .ipynb files originally, so no .py files were generated. Nothing to clean up here."
        )
    else:
        for file_path in ipynb_to_py_list:
            try:
                os.remove(file_path)
                print(f"Removed: {file_path}")
            except FileNotFoundError:
                print(f"File not found: {file_path}. It can't be removed.")
            except PermissionError:
                print(f"Permission denied: {file_path}. It can't be removed.")
            except Exception as e:
                print(f"Error removing {file_path}: {e}")


# Get most prevalent extension for code files
def determine_most_ext(counts):
    # TODO: implement logic to determine the codebase.
    return ".py"


def find_readme(project_path):
    files = list_files(project_path)
    readme_files = [
        f for f in files if os.path.basename(f).lower().startswith("readme")
    ]

    if readme_files:
        return readme_files[0]
    else:
        return None


def read_file_contents(path_to_file):
    if path_to_file == None:
        return ""
    else:
        if os.path.exists(path_to_file):
            with open(path_to_file, "r") as f:
                contents = f.read()
            return contents
        else:
            return ""


def conform_to_pep8(filename):

    pep8_cmd = "autopep8 --in-place --aggressive {}".format(filename)

    p = subprocess.Popen(
        pep8_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    (out, err) = p.communicate()
    p_status = p.wait()

    return 0


def extract_external_imports(code):

    external_imports = []

    tree = ast.parse(code)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                if not name.name.startswith("."):
                    external_imports.append(name.name)
        elif isinstance(node, ast.ImportFrom):
            if not node.module.startswith("."):
                external_imports.append(node.module)

    return external_imports


def extract_requirements_from_code(project_path, ext, generate=True):

    requirements_emoji()

    if generate:
        files = list_files(project_path)
        matching = [f for f in files if os.path.splitext(f)[1] == ext]

        external_imports = []
        for filename in matching:
            i = 0
            while i < 2:
                with open(os.path.join(project_path, filename), "r") as readfile:
                    content = readfile.read()
                    try:
                        external_imports.append(extract_external_imports(content))
                        i = 2
                    except Exception as e:
                        if i == 1:
                            i = 2
                            print(e)
                            print(
                                "External imports extraction failed for file {}: {}".format(
                                    filename, Exception
                                )
                            )
                        else:
                            conform_to_pep8(filename)
                            i += 1

        external_imports = [
            imp.split(".")[0] for sublist in external_imports for imp in sublist
        ]
        external_imports = list(set(external_imports))

        requirements = "\n".join(external_imports)
    else:
        with open(
            "{}/requirements.txt".format(os.getenv("OGRE_DIR", OGRE_DIR)), "r"
        ) as f:
            requirements = f.read()
    return requirements


def append_files_with_ext(project_path, ext, limit, output_file):
    files = list_files(project_path)
    matching = [f for f in files if os.path.splitext(f)[1] == ext]

    if limit < len(matching):
        matching = matching[:limit]

    contents = ""
    with open(output_file, "a") as outfile:
        for filename in matching:
            with open(os.path.join(project_path, filename), "r") as readfile:
                contents += readfile.read()

    return contents


def generate_context_file(readme_text, source_text, output_file):
    """
    Generates the context file by appending the README and the source code text.
    The content of this file will be used to extract the dependencies.
    """
    out_text = readme_text + source_text

    with open(output_file, "w") as out:
        out.write(out_text)

    with open(output_file, "r") as f:
        return f.read()


def read_context(path_to_context_file):
    with open(path_to_context_file, "r") as f:
        contents = f.read()
    return contents


def extract_requirements(provider, contents):
    requirements_emoji()
    if provider == "openai":
        res = extract_requirements_openai(contents)
    elif provider == "octoai":
        res = extract_requirements_octoai(contents)
    elif provider == "groq":
        res = extract_requirements_groq(contents)
    return res


def extract_requirements_openai(contents):
    model = os.getenv("OPENAI_MODEL", OPENAI_MODEL)
    prompt = os.getenv("OPENAI_SECRET_PROMPT", OPENAI_SECRET_PROMPT)
    client = OpenAI()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": contents},
        ],
    )
    requirements = completion.choices[0].message.content

    return requirements


def extract_requirements_octoai(contents):
    model = os.getenv("OCTOAI_MODEL", OCTOAI_MODEL)
    prompt = os.getenv("OCTOAI_SECRET_PROMPT", OCTOAI_SECRET_PROMPT)
    client = OctoAiClient()

    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": contents},
        ],
        model=model,
        max_tokens=20000,
        presence_penalty=0,
        temperature=0.1,
        top_p=0.9,
    )

    requirements = completion.choices[0].message.content

    return requirements


# def extract_requirements_groq(contents):
#    prompt = os.getenv("GROQ_SECRET_PROMPT", GROQ_SECRET_PROMPT)
#    with Completion() as completion:
#        full_prompt = prompt + " " + contents
#        response, id, stats = completion.send_prompt(
#            "llama2-70b-4096", user_prompt=full_prompt
#        )
#        if response != "":
#            print(f"\nPrompt: {prompt}\n")
#            print(f"Request ID: {id}")
#            print(f"Output:\n {response}\n")
#            print(f"Stats:\n {stats}\n")
#    return response


def clean_requirements(provider, requirements):
    cleaning_requirements_emoji()
    if provider == "openai":
        res = clean_requirements_openai(requirements)
    elif provider == "gemini":
        res = clean_requirements_gemini(requirements)
    elif provider == "ogre":
        res = clean_requirements_ogre(requirements)
    elif provider == "llama3.2":
        res = clean_requirements_llama32(requirements)
    elif provider == "ollama":
        res = clean_requirements_ollama(requirements)
    elif provider == "octoai":
        res = clean_requirements_octoai(requirements)
    elif provider == "groq":
        res = clean_requirements_groq(requirements)
    elif provider == "mistral":
        res = clean_requirements_mistral(requirements)
    return res


def clean_requirements_openai(requirements):
    model = os.getenv("OPENAI_MODEL", OPENAI_MODEL)
    prompt = os.getenv(
        "CLEAN_REQUIREMENTS_SECRET_PROMPT", CLEAN_REQUIREMENTS_SECRET_PROMPT
    )
    # print(f"{model=} {prompt=}")
    client = OpenAI()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": requirements},
        ],
    )
    requirements = completion.choices[0].message.content
    # print(f"{requirements=}")
    return requirements


def clean_requirements_gemini(requirements):
    model = os.getenv("GEMINI_MODEL", GEMINI_MODEL)
    prompt = os.getenv(
        "CLEAN_REQUIREMENTS_SECRET_PROMPT", CLEAN_REQUIREMENTS_SECRET_PROMPT
    )
    # print(f"{model=}")
    client = googleai.GenerativeModel(model)
    full_prompt = f"{prompt}\n---\n{requirements}"
    # print(f"{full_prompt=}")
    response = client.generate_content(full_prompt, request_options={"timeout": 1000})
    requirements = response.text
    # print(f"{requirements=}")
    return requirements


def clean_requirements_ogre(requirements):
    model = os.getenv("OGRE_MODEL", OGRE_MODEL)
    prompt = os.getenv(
        "CLEAN_REQUIREMENTS_SECRET_PROMPT", CLEAN_REQUIREMENTS_SECRET_PROMPT
    )
    api_server = os.getenv("OGRE_API_SERVER", OGRE_API_SERVER)
    ogre_token = os.getenv("OGRE_TOKEN", OGRE_TOKEN)
    
    # Define headers
    headers = {
        "Content-Type": "application/json"
    }

    full_prompt = prompt + " " + requirements
    
    # Define the data to be sent in JSON format
    data = {
        "model": model,
        "prompt": full_prompt,
        "ogre_token": ogre_token,
    }

    # Send the POST request
    response = requests.post(api_server, headers=headers, json=data)

    # Process the response
    response_json = json.loads(response.json()['data'])
    requirements = response_json['response']
    
    return requirements


def clean_requirements_llama32(requirements):
   
    model = os.getenv("LLAMA_MODEL", LLAMA_MODEL)
    prompt = os.getenv(
        "CLEAN_REQUIREMENTS_SECRET_PROMPT", CLEAN_REQUIREMENTS_SECRET_PROMPT
    )
    api_server = os.getenv("LLAMA_API_SERVER", LLAMA_API_SERVER)

    full_prompt = prompt + " " + requirements
    
    client = Client(host=api_server)
    response = client.generate(model=model, prompt=full_prompt)
    
    return json.loads(json.dumps(response))['response']


def clean_requirements_ollama(requirements):
    model = os.getenv("OLLAMA_MODEL", OLLAMA_MODEL)
    prompt = os.getenv(
        "CLEAN_REQUIREMENTS_SECRET_PROMPT", CLEAN_REQUIREMENTS_SECRET_PROMPT
    )
    api_server = os.getenv("OLLAMA_API_SERVER", OLLAMA_API_SERVER)
    # print(f"{api_server=} {model=} {prompt=}")
    client = OpenAI(base_url=api_server, api_key="ollama")
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": requirements},
        ],
    )
    requirements = completion.choices[0].message.content

    return requirements


def clean_requirements_mistral(requirements):
    raise NotImplementedError("rewrite_readme_octoai is not implemented.")
    #model = os.getenv("MISTRAL_MODEL", MISTRAL_MODEL)
    #prompt = os.getenv(
    #    "CLEAN_REQUIREMENTS_SECRET_PROMPT", CLEAN_REQUIREMENTS_SECRET_PROMPT
    #)
    #api_key = os.environ["MISTRAL_API_KEY"]
    #client = MistralClient(api_key=api_key)
    #content = prompt + "\n" + requirements
    #messages = [ChatMessage(role="user", content=content)]

    ## No streaming
    #chat_response = client.chat(
    #    model=model,
    #    messages=messages,
    #)
    #requirements = chat_response.choices[0].message.content

    #return requirements


def clean_requirements_groq(requirements):
    model = os.getenv("GROQ_MODEL", GROQ_MODEL)
    prompt = os.getenv(
        "GROQ_CLEAN_REQUIREMENTS_SECRET_PROMPT", GROQ_CLEAN_REQUIREMENTS_SECRET_PROMPT
    )

    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
    )

    response = chat_completion.choices[0].message.content
    #    with Completion() as completion:
    #        full_prompt = prompt + " " + requirements
    #        response, id, stats = completion.send_prompt(model, user_prompt=full_prompt)

    return response


def clean_requirements_octoai(requirements):
    model = os.getenv("OCTOAI_MODEL", OCTOAI_MODEL)
    prompt = os.getenv(
        "CLEAN_REQUIREMENTS_SECRET_PROMPT", CLEAN_REQUIREMENTS_SECRET_PROMPT
    )
    client = OctoAiClient()

    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": requirements},
        ],
        model=model,
        max_tokens=20000,
        presence_penalty=0,
        temperature=0.1,
        top_p=0.9,
    )

    requirements = completion.choices[0].message.content

    return requirements


def save_requirements(requirements, ogre_dir_path):
    requirements_fullpath = os.path.join(ogre_dir_path, "requirements.txt")
    with open(requirements_fullpath, "w") as f:
        f.write(requirements)
    return requirements_fullpath


def count_tokens(string) -> int:
    from importlib.resources import files

    tiktoken_cache_dir = str(files("miniogre").joinpath("encodings"))
    os.environ["TIKTOKEN_CACHE_DIR"] = tiktoken_cache_dir
    cache_key = "9b5ad71b2ce5302211f9c61530b329a4922fc6a4"  # cl100k_base
    assert os.path.exists(os.path.join(tiktoken_cache_dir, cache_key))
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens


def rewrite_readme(provider, readme):
    readme_emoji()

    if provider == "openai":
        res = rewrite_readme_openai(readme)
    elif provider == "gemini":
        res = rewrite_readme_gemini(readme)
    elif provider == "ogre":
        res = rewrite_readme_ogre(readme)
    elif provider == "llama3.2":
        res = rewrite_readme_llama32(readme)
    elif provider == "ollama":
        res = rewrite_readme_ollama(readme)
    elif provider == "octoai":
        res = rewrite_readme_octoai(readme)
    elif provider == "groq":
        res = rewrite_readme_groq(readme)
    elif provider == "mistral":
        res = rewrite_readme_mistral(readme)
    return res


def rewrite_readme_openai(readme):
    model = os.getenv("OPENAI_MODEL", OPENAI_MODEL)
    prompt = os.getenv("REWRITE_README_PROMPT", REWRITE_README_PROMPT)
    # print(f"{model=} {prompt=}")
    new_readme = ""
    if "OPENAI_API_KEY" not in os.environ:
        raise EnvironmentError("OPENAI_API_KEY environment variable not defined")
    try:
        client = OpenAI()
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": readme},
            ],
        )
        # print(completion)
        new_readme = completion.choices[0].message.content
    except Exception as e:
        print(e)
    return new_readme


def rewrite_readme_gemini(readme):
    model = os.getenv("GEMINI_MODEL", GEMINI_MODEL)
    prompt = os.getenv("REWRITE_README_PROMPT", REWRITE_README_PROMPT)
    full_prompt = f"{prompt}\n---\n{readme}"
    # print(f"{model=} {full_prompt=}")
    new_readme = ""
    if "GEMINI_API_KEY" not in os.environ:
        raise EnvironmentError("GEMINI_API_KEY environment variable not defined")
    try:
        client = googleai.GenerativeModel(model)
        response = client.generate_content(full_prompt)
        new_readme = response.text
    except Exception as e:
        print(e)
    return new_readme


def rewrite_readme_ogre(readme):

    model = os.getenv("OGRE_MODEL", OGRE_MODEL)
    prompt = os.getenv("REWRITE_README_PROMPT", REWRITE_README_PROMPT)
    api_server = os.getenv("OGRE_API_SERVER", OGRE_API_SERVER)
    ogre_token = os.getenv("OGRE_TOKEN", OGRE_TOKEN)
    
    full_prompt = prompt + " " + readme

    # Define headers
    headers = {
        "Content-Type": "application/json"
    }

    # Define the data to be sent in JSON format
    data = {
        "model": model,
        "prompt": full_prompt,
        "ogre_token": ogre_token,
    }
    new_readme = ""
    #try:
    # Send the POST request
    response = requests.post(api_server, headers=headers, json=data)

    # Process the response
    response_json = json.loads(response.json()['data'])
    new_readme = response_json['response']
    #except Exception as e:
        #print(e)
    return new_readme

def rewrite_readme_llama32(readme):

    model = os.getenv("LLAMA_MODEL", LLAMA_MODEL)
    prompt = os.getenv("REWRITE_README_PROMPT", REWRITE_README_PROMPT)
    api_server = os.getenv("LLAMA_API_SERVER", LLAMA_API_SERVER)
    
    new_readme = ""
    full_prompt = prompt + " " + readme

    client = Client(host=api_server)
    response = client.generate(model=model, prompt=full_prompt)
    
    new_readme = json.loads(json.dumps(response))['response']
    
    return new_readme

def rewrite_readme_ollama(readme):
    model = os.getenv("OLLAMA_MODEL", OLLAMA_MODEL)
    prompt = os.getenv("REWRITE_README_PROMPT", REWRITE_README_PROMPT)
    api_server = os.getenv("OLLAMA_API_SERVER", OLLAMA_API_SERVER)
    # print(f"{api_server=} {model=} {prompt=}")
    new_readme = ""
    try:
        client = OpenAI(base_url=api_server, api_key="ollama")
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": readme},
            ],
        )
        new_readme = completion.choices[0].message.content
    except Exception as e:
        print(e)
    return new_readme


def rewrite_readme_octoai(readme):
    raise NotImplementedError("rewrite_readme_octoai is not implemented.")


def rewrite_readme_groq(readme):
    model = os.getenv("GROQ_MODEL", GROQ_MODEL)
    prompt = os.getenv("REWRITE_README_PROMPT", REWRITE_README_PROMPT)

    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": readme},
        ],
        model=model,
    )

    response = chat_completion.choices[0].message.content

    return response


def rewrite_readme_mistral(readme):
    raise NotImplementedError("rewrite_readme_octoai is not implemented.")
    #model = os.getenv("MISTRAL_MODEL", MISTRAL_MODEL)
    #prompt = os.getenv("REWRITE_README_PROMPT", REWRITE_README_PROMPT)
    #api_key = os.environ["MISTRAL_API_KEY"]
    #client = MistralClient(api_key=api_key)
    #content = prompt + "\n" + readme
    #messages = [ChatMessage(role="user", content=content)]

    ## No streaming
    #chat_response = client.chat(
    #    model=model,
    #    messages=messages,
    #)
    #new_readme = chat_response.choices[0].message.content

    #return new_readme


def save_readme(readme, ogre_dir_path):
    readme_fullpath = os.path.join(ogre_dir_path, "README.md")
    with open(readme_fullpath, "w") as f:
        f.write(readme)
    return readme_fullpath


def build_docker_image(
    dockerfile, image_name, host_platform=None, verbose=False, cache=False
):
    # build docker image

    if host_platform == None:
        platform_name = "linux/{}".format(platform.machine())
    else:
        platform_name = host_platform
    image_name = "miniogre/{}:{}".format(image_name.lower(), "latest")

    build_emoji()
    print("   platform = {}".format(platform_name))
    print("   image name = {}".format(image_name))

    if verbose:
        stderr = None
        progress = "plain"
    else:
        stderr = subprocess.PIPE
        progress = "auto"

    if cache:
        cache_option = ""
    else:
        cache_option = "--no-cache"

    build_cmd = "DOCKER_BUILDKIT=1 docker buildx build {} --load --progress={} --platform {} -t {} -f {} .".format(
        cache_option, progress, platform_name, image_name, dockerfile
    )
    print("   build command = {}".format(build_cmd))

    if verbose:
        p = subprocess.Popen(
            build_cmd, stdout=subprocess.PIPE, stderr=stderr, shell=True
        )
        (out, err) = p.communicate()
        p_status = p.wait()
    else:
        with yaspin().aesthetic as sp:
            sp.text = "generating ogre environment"
            p = subprocess.Popen(
                build_cmd, stdout=subprocess.PIPE, stderr=stderr, shell=True
            )
            (out, err) = p.communicate()
            p_status = p.wait()
    return out


def spin_up_container(image_name, project_path, port_map):
    # spin up container
    spinup_emoji()

    project_name = image_name
    container_name = "miniogre-{}".format(image_name.lower())
    image_name = "miniogre/{}:{}".format(image_name.lower(), "latest")
    # cmd = "uv venv; source .venv/bin/activate; cat ./{}/requirements.txt | xargs -L 1 uv pip install; exit 0;"
    # cmd = "cat ./ogre_dir/requirements.txt | xargs -L 1 uv pip install; exit 0"
    spin_up_cmd = "docker run -it --rm -v {}:/opt/{} -p {} --name {} {} bash".format(
        project_path, project_name, port_map, container_name, image_name
    )

    print("   spin up command = {}".format(spin_up_cmd))
    subprocess.call(spin_up_cmd.split())
    # p = subprocess.Popen(spin_up_cmd, stdout=subprocess.PIPE, shell=True)
    # (out, err) = p.communicate()
    # p_status = p.wait()

    return 0


def create_sbom(image_name, project_path, format, verbose=False):
    # Create SBOM from inside the container
    print(emoji.emojize(":desktop_computer:  Generating SBOM..."))

    project_name = image_name
    container_name = "miniogre-{}".format(image_name.lower())
    image_name = "miniogre/{}:{}".format(image_name.lower(), "latest")

    if format == "cyclonedx":
        sbom_format_cmd = "cyclonedx-py requirements ./ogre_dir/requirements.txt &> ./ogre_dir/sbom.json"
    elif format == "pip-licenses":
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


# def create_virtualenv(requirements, python_version):

#     env_name = 'miniogre-env'

#     venv_cmd = "python -m venv {}".format(env_name)
#     # venv_activate_cmd = 'source {}/bin/activate'.format(env_name)

#     #os.popen(venv_cmd)
#     #os.popen(venv_activate_cmd)
#     p = subprocess.Popen(venv_cmd, stdout=subprocess.PIPE, shell=True)
#     (out, err) = p.communicate()
#     p_status = p.wait()

#     venv_activate_cmd = 'source {}/bin/activate'.format(env_name)
#     p = subprocess.Popen(venv_activate_cmd, stdout=subprocess.PIPE, shell=True)
#     (out, err) = p.communicate()
#     p_status = p.wait()

#     pip_cmd = '{}/bin/pip'.format(env_name)
#     with open(requirements) as f:
#         requirements_list = []
#         for line in f:
#             requirements_list.append(line.strip('\n'))

#         pip_cmd = 'pip'
#         for req in requirements_list:
#             print(req)
#             input()
#             subprocess.call([pip_cmd, 'install', req.strip()])


def run_gptify(repo_path):

    generate_context_emoji()

    if not os.path.exists("ogre_dir"):
        os.mkdir("ogre_dir")

    gptrepo_cmd = 'gptify {} --output "ogre_dir/gptify_output.txt"'.format(repo_path)
    p = subprocess.Popen(
        gptrepo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    (out, err) = p.communicate()
    p_status = p.wait()

    with open("ogre_dir/gptify_output.txt", "r") as f:
        return f.read()


def cleanup():
    """
    Delete unnecessary files
    """
    if os.path.exists("ogre_dir/gptify_output.txt"):
        os.remove("ogre_dir/gptify_output.txt")


def read_readme(repo_path):
    # List of possible README file names (without specific case)
    possible_names = ["README.md", "README.txt", "README.rst", "README.adoc", "README"]

    # Get all files in the directory
    files_in_directory = os.listdir(repo_path)

    # Check for each possible README name in a case-insensitive manner
    for name in possible_names:
        for file in files_in_directory:
            if file.lower() == name.lower():
                readme_path = os.path.join(repo_path, file)
                with open(readme_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    return content

    # If no README file is found, raise an exception
    raise FileNotFoundError("No README file found in the repository.")


def evaluate_readme(provider, readme, verbose):
    eval_emoji()
    if provider == "openai":
        return evaluate_readme_openai(readme, verbose)
    elif provider == "gemini":
        return evaluate_readme_gemini(readme, verbose)
    elif provider == "ollama":
        return evaluate_readme_ollama(readme, verbose)
    elif provider == "groq":
        return evaluate_readme_groq(readme, verbose)
    elif provider == "octoai":
        # return evaluate_readme_octoai(readme, verbose)
        raise NotImplementedError("This provider is not yet implemented")
    elif provider == "mistral":
        # res = evaluate_readme_mistral(readme, verbose)
        raise NotImplementedError("This provider is not yet implemented")
    else:
        raise ValueError("Invalid provider")


def evaluate_readme_openai(readme, verbose):
    model = os.getenv("OPENAI_MODEL", OPENAI_MODEL)
    system_prompt = os.getenv("README_EVAL_SYSTEM_PROMPT", README_EVAL_SYSTEM_PROMPT)
    user_prompt_template = Template(
        os.getenv("README_EVAL_USER_PROMPT", README_EVAL_USER_PROMPT)
    )
    user_prompt = user_prompt_template.substitute(README=readme)
    if verbose:
        print(f"\n{model=}\n{system_prompt=}\n{user_prompt=}\n")
    score = "0"
    if "OPENAI_API_KEY" not in os.environ:
        raise EnvironmentError("OPENAI_API_KEY environment variable not defined")
    try:
        client = OpenAI()
        completion = client.chat.completions.create(
            model=model,
            seed=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        score = completion.choices[0].message.content
        if verbose:
            print(f"\n{score=}\n")
    except Exception as e:
        print(e)
    return score


def evaluate_readme_gemini(readme, verbose):
    model = os.getenv("GEMINI_MODEL", GEMINI_MODEL)
    prompt_template = Template(os.getenv("README_EVAL_PROMPT", README_EVAL_PROMPT))
    prompt = prompt_template.substitute(README=readme)
    if verbose:
        print(f"\n{model=}\n{prompt=}\n")
    score = "0"
    if "GEMINI_API_KEY" not in os.environ:
        raise EnvironmentError("GEMINI_API_KEY environment variable not defined")
    try:
        client = googleai.GenerativeModel(model)
        response = client.generate_content(prompt)
        score = response.text
        if verbose:
            print(f"\n{score=}\n")
    except Exception as e:
        print(e)
    return score


def evaluate_readme_ollama(readme, verbose):
    model = os.getenv("OLLAMA_MODEL", OLLAMA_MODEL)
    api_server = os.getenv("OLLAMA_API_SERVER", OLLAMA_API_SERVER)
    system_prompt = os.getenv("README_EVAL_SYSTEM_PROMPT", README_EVAL_SYSTEM_PROMPT)
    user_prompt_template = Template(
        os.getenv("README_EVAL_USER_PROMPT", README_EVAL_USER_PROMPT)
    )
    user_prompt = user_prompt_template.substitute(README=readme)
    if verbose:
        print(f"\n{model=}\n{api_server=}\n{system_prompt=}\n{user_prompt=}\n")
    score = "0"
    try:
        client = OpenAI(base_url=api_server, api_key="ollama")
        completion = client.chat.completions.create(
            model=model,
            seed=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        score = completion.choices[0].message.content
        if verbose:
            print(f"\n{score=}\n")
    except Exception as e:
        print(e)
    return score


def evaluate_readme_groq(readme, verbose):
    model = os.getenv("GROQ_MODEL", GROQ_MODEL)
    prompt_template = Template(os.getenv("README_EVAL_PROMPT", README_EVAL_PROMPT))
    prompt = prompt_template.substitute(README=readme)
    if verbose:
        print(f"\n{model=}\n{prompt=}\n")
    score = "0"
    if "GROQ_API_KEY" not in os.environ:
        raise EnvironmentError("GROQ_API_KEY environment variable not defined")
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model,
            seed=0,
        )
        score = chat_completion.choices[0].message.content
        if verbose:
            print(f"\n{score=}\n")
    except Exception as e:
        print(e)
    return score

def create_tar(folder_path, output_filename):
    # Generate a unique hash using UUID
    unique_hash = uuid.uuid4().hex
    
    # Add the unique hash to the output filename
    output_filename_with_hash = f"{output_filename}_{unique_hash}.tar"
    
    # Create the tar file with the unique name
    with tarfile.open(output_filename_with_hash, 'w') as tarf:
        tarf.add(folder_path, arcname=os.path.basename(folder_path))

    print(f"tarfile created: {output_filename_with_hash}")

    return os.path.join(folder_path, output_filename_with_hash)

def send_tarfile_to_server(file_path, server_url):
    """
    Sends a tarfile to the specified server URL using a POST request.

    :param file_path: Path to the tarfile to be sent.
    :param server_url: URL of the server to send the file to.
    :return: Response from the server.
    """
    try:
        # Open the tarfile in binary mode
        with open(file_path, 'rb') as file:
            # Create a dictionary to hold the file data
            files = {'file': (file_path, file)}

            # Send the POST request to the server
            response = requests.post(server_url, files=files)

            # Check if the request was successful
            if response.status_code == 200:
                print(f"\nSuccessful upload to Ogre Terminal \n \n {response.text}")
            else:
                print(f"Failed to upload file. Status code: {response.status_code}, Response: {response.text}")

            return response
    except Exception as e:
        print(f"An error occurred: {e}")

def delete_tarfile(file_path):
    """
    Deletes a tar file specified by file_path.

    :param file_path: Path to the tar file to be deleted.
    :type file_path: str
    :raises FileNotFoundError: If the specified file does not exist.
    :raises PermissionError: If the file cannot be deleted due to insufficient permissions.
    """
    try:
        os.remove(file_path)
        #print(f"File '{file_path}' has been deleted successfully.")
    except FileNotFoundError:
        print(f"File '{file_path}' does not exist.")
    except PermissionError:
        print(f"Permission denied: cannot delete '{file_path}'.")
    except Exception as e:
        print(f"An error occurred while trying to delete the file: {e}")
