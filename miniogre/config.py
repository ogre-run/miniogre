import os
import platform
import random
import requests

from dotenv import load_dotenv
from zoneinfo import ZoneInfo
from tzlocal import get_localzone

from .constants import *

# Get system timezone
TIMEZONE = get_localzone().key

load_dotenv()


def load_wordlist(url):

    # Local filename to save the downloaded file
    filename = "wordlist.txt"

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Write the content to a local file
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"File '{filename}' downloaded successfully.")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

    with open(filename, "r") as file:
        wordlist = [line.strip() for line in file.readlines()]

    # Clean up before returning wordlist
    file_path = "./{}".format(filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File '{file_path}' deleted successfully.")
    else:
        print(f"File '{file_path}' does not exist.")

    return wordlist


def generate_secure_passphrase(wordlist, num_words=2):
    passphrase = " ".join(random.choice(wordlist) for _ in range(num_words))
    return passphrase.replace("\t", "").replace(" ", "")


def config_ogre_dir(ogre_dir):
    """
    Check for existence of ogre_dir directory. If it exists, nothing is
    done. If it doesn't, it is created.
    """
    if not os.path.exists(ogre_dir):
        os.makedirs(ogre_dir)

    return ogre_dir


def _run_welcome(project_path, product, version, ogre_dir, date):

    original_pwd = os.getcwd()

    os.chdir(project_path)

    repo = os.popen("git remote get-url origin").read()
    author = os.popen("git log -1 --pretty=format:'%ae'").read()
    commit = os.popen("git log -1 --pretty=%h").read()
    commit = ''.join(commit.splitlines())
    # date = datetime.today().strftime("%Y-%m-%d-%H:%M:%S")

    os.chdir(original_pwd)

    BOILERPLATE = """# Git repo info\necho REPOSITORY = {}\necho COMMIT = {}\necho COMMIT_AUTHOR = {}""".format(
        repo[:-1], commit, author
    )

    with open("{}/bashrc".format(ogre_dir), "a") as f:
        f.write(BOILERPLATE)
    f.close()


def config_bashrc(project_dir, ogre_dir, product, version, date):
    """
    Check for existence of bashrc. If it exists, nothing is done. If it
    doesn't, it is created.
    """

    if os.path.isfile("{}/bashrc".format(project_dir)):
        # print("   bashrc exists in {}".format(project_dir))
        os.popen("cp {}/bashrc {}/bashrc".format(project_dir, ogre_dir))

    else:
        # print("   bashrc doesn't exist. Making a new one for you.")
        with open("{}/bashrc".format(ogre_dir), "w") as f:
            f.write(BASHRC)
        f.close()
    _run_welcome(project_dir, product, version, ogre_dir, date)

    return os.path.isfile("{}/bashrc".format(ogre_dir))


def config_ttyd_entrypoint(ogre_dir):
    """
    Config ttyd_entrypoint script
    """

    file_path = "{}/ttyd_entrypoint.sh".format(ogre_dir)

    with open(file_path, "w") as f:
        f.write(TTYD_ENTRYPOINT)

    # Make the file executable
    os.chmod(file_path, 0o755)

    return os.path.isfile("{}/ttyd_entrypoint.sh".format(ogre_dir))


def config_bashrc_baseimage(ogre_dir):
    """
    Create simple bashrc.
    """

    with open("{}/bashrc".format(ogre_dir), "w") as f:
        f.write(BASHRC)
    f.close()

    return os.path.isfile("{}/bashrc".format(ogre_dir))


def config_dockerfile(
    project_dir, 
    project_name,
    framework,
    ogre_dir, 
    baseimage, 
    dry=False, 
    base=False
):
    """
    Check for existence of Dockerfile. If it exists, nothing is done. If it
    doesn't, a new Dockerfile is generate following the parameters in the
    config file.
    """

    REQUIREMENTS_LINE = "RUN cat ./{}/requirements.txt | xargs -L 1 uv pip install --system; exit 0".format(
        os.path.basename(ogre_dir)
    )
    if dry:
        print("Dry build -- no requirements will be installed {}".format(baseimage))

        dockerfile_string = DOCKERFILE_DRY

        with open("{}/Dockerfile".format(ogre_dir), "w") as f:
            f.write(dockerfile_string.format(project_name))
        f.close()
        with open("{}/Dockerfile".format(ogre_dir), "r+") as f:
            content = f.read()
            f.seek(0, 0)
            f.write("FROM {}\nENV TZ={}".format(baseimage, TIMEZONE) + content)
        f.close()

        return os.path.isfile("{}/Dockerfile".format(ogre_dir))

    if base:
        print("Building baseimage.")

        dockerfile_string = DOCKERFILE_BASEIMAGE

        # Load wordlist from a file (replace 'eff_wordlist.txt' with your actual file path)
        wordlist = load_wordlist(WORDLIST_URL)
        secure_passphrase = generate_secure_passphrase(wordlist)

        with open("{}/Dockerfile".format(ogre_dir), "w") as f:
            f.write(dockerfile_string.format(secure_passphrase))
        f.close()
        with open("{}/Dockerfile".format(ogre_dir), "r+") as f:
            content = f.read()
            f.seek(0, 0)
            f.write("FROM {}\nENV TZ={}".format(baseimage, TIMEZONE) + content)
        f.close()

        return secure_passphrase

    else:

        if os.path.isfile("{}/Dockerfile".format(project_dir)):
            print("   Dockerfile exists in {}".format(project_dir))
            os.popen("cp {}/Dockerfile {}/Dockerfile".format(project_dir, ogre_dir))
        else:
            print(
                "   Dockerfile doesn't exist. Making a new one for you using {}".format(
                    baseimage
                )
            )
            if framework == None: 
                dockerfile_string = DOCKERFILE
                print
                with open("{}/Dockerfile".format(ogre_dir), "w") as f:
                    f.write(dockerfile_string.format(project_name))
                f.close()
                with open("{}/Dockerfile".format(ogre_dir), "r+") as f:
                    content = f.read()
                    f.seek(0, 0)
                    f.write("FROM {}\nENV TZ={}".format(baseimage, TIMEZONE) + content)
                    # Find last line
                    f.seek(0, 2)
                    f.write("{}".format(REQUIREMENTS_LINE))
                f.close()
            elif framework in FRAMEWORKS_LIST:
                dockerfile_string = DOCKERFILE_NODE
                with open("{}/Dockerfile".format(ogre_dir), "w") as f:
                    f.write(dockerfile_string.format(project_name))
                f.close()
                with open("{}/Dockerfile".format(ogre_dir), "r+") as f:
                    content = f.read()
                    f.seek(0, 0)
                    f.write("FROM {}\nENV TZ={}".format(baseimage, TIMEZONE) + content)
                f.close()
        return os.path.isfile("{}/Dockerfile".format(ogre_dir))

def config_baseimage(framework = None):

    platform_machine = "{}".format(platform.machine())
    if framework == None:
        baseimage = (os.getenv("OGRE_BASEIMAGE", OGRE_BASEIMAGE)).format(platform_machine)
    else:
        print("{} framework identified. Picking a proper baseimage.".format(framework))
        baseimage = FRAMEWORK_BASEIMAGE[framework]
    return baseimage


def config_requirements(project_dir, ogre_dir, force=False):

    # Check if requirements.txt is in the root folder
    if os.path.isfile("{}/requirements.txt".format(project_dir)):
        if force:
            print(
                "   requirements.txt exists in {}, but it will be OVERWRITTEN".format(
                    project_dir
                )
            )
            return True
        print("   requirements.txt already exists and it will be reused.")
        os.popen(
            "cp {}/requirements.txt {}/requirements.txt".format(project_dir, ogre_dir)
        )
        res = False
    else:
        print("   requirements.txt does not exist. miniogre will create one for you.")
        res = True
    return res
