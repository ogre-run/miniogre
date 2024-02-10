import os
import platform
import subprocess
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

def append_files_with_ext(project_path, ext, limit, output_file):
    files = list_files(project_path)
    matching = [f for f in files if os.path.splitext(f)[1] == ext]
    
    if limit < len(matching):
        matching = matching[:limit]
        
    with open(output_file, 'a') as outfile:
        for filename in matching:
            with open(os.path.join(project_path, filename), 'r') as readfile:
                outfile.write(readfile.read())

    return outfile
                
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

def build_docker_image(dockerfile, image_name, ogre_dir_path):
    # build docker image
    
    platform_name = "linux/{}".format(platform.machine())
    image_name = "miniogre/{}:{}".format(image_name.lower(), "latest")

    print("Build docker image...")
    print("platform = {}".format(platform_name)) 
    print("image name = {}".format(image_name))
    
    build_cmd = (
        "DOCKER_BUILDKIT=1 docker buildx build --load --progress=auto --platform {} -t {} -f {} .".format(
            platform_name, image_name, dockerfile
        )
    )
    print(build_cmd)
    p = subprocess.Popen(build_cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = p.communicate()
    p_status = p.wait()

    return out

def spin_up_container(image_name, project_path):
    # spin up container
    
    platform_name = "linux/{}".format(platform.machine())
    project_name = image_name
    image_name = "miniogre/{}:{}".format(image_name.lower(), "latest")
    container_name = "miniogre-{}".format(image_name.lower())

    print("Build docker image...")
    print("platform = {}".format(platform_name)) 
    print("image name = {}".format(image_name))
    
    spin_up_cmd = (
        "docker run -d --rm -v {}:/opt/{} \
            -p 8001:8001 \
            --name {} \
            {} bash".format(project_path, project_name, container_name, image_name)  
    )

    print(spin_up_cmd)
    p = subprocess.Popen(spin_up_cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = p.communicate()
    p_status = p.wait()

    return out
    

