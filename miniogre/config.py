import os
import platform
from dotenv import load_dotenv
from .constants import *


load_dotenv()

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
    # date = datetime.today().strftime("%Y-%m-%d-%H:%M:%S")

    os.chdir(original_pwd)

    BOILERPLATE = """
        echo PRODUCT = {}
        echo VERSION = {}
        echo BUILD_DATE = {} 
        echo REPOSITORY = {} 
        echo COMMIT = {}echo COMMIT_AUTHOR = {} 
        """.format(product, version, date, repo[:-1], commit, author)

    with open("{}/bashrc".format(ogre_dir), "a") as f:
        f.write(BOILERPLATE)
    f.close()

def config_bashrc(project_dir, ogre_dir, product, version, date):

    """
    Check for existence of bashrc. If it exists, nothing is done. If it
    doesn't, it is created.
    """

    if os.path.isfile("{}/bashrc".format(project_dir)):
        print("bashrc exists in {}".format(project_dir))
        os.popen("cp {}/bashrc {}/bashrc".format(project_dir, ogre_dir))

    else:
        print("bashrc doesn't exist. Making a new one for you.")
        with open("{}/bashrc".format(ogre_dir), "w") as f:
            f.write(BASHRC)
        f.close()
    _run_welcome(project_dir, product, version, ogre_dir, date)

    return os.path.isfile("{}/bashrc".format(ogre_dir))

def config_dockerfile(project_dir, project_name, ogre_dir,
                      baseimage, dry = False):
    """
    Check for existence of Dockerfile. If it exists, nothing is done. If it
    doesn't, a new Dockerfile is generate following the parameters in the
    config file.
    """

    REQUIREMENTS_LINE = 'RUN cat ./{}/requirements.txt | xargs -L 1 pip3 install; exit 0'.format(os.path.basename(ogre_dir))

    if dry:
        print(
            "Dry build -- no requirements will be installed {}".format(
                baseimage
            )
        )

        dockerfile_string = DOCKERFILE_DRY

        with open("{}/Dockerfile".format(ogre_dir), "w") as f:
            f.write(dockerfile_string.format(project_name))
        f.close()
        with open("{}/Dockerfile".format(ogre_dir), "r+") as f:
            content = f.read()
            f.seek(0, 0)
            f.write("FROM {}".format(baseimage) + content)
        f.close()
    
    else:

        if os.path.isfile("{}/Dockerfile".format(project_dir)):
            print("Dockerfile exists in {}".format(project_dir))
            os.popen("cp {}/Dockerfile {}/Dockerfile".format(project_dir, ogre_dir))
        else:
            print(
                "Dockerfile doesn't exist. Making a new one for you using {}".format(
                    baseimage
                )
            )

            dockerfile_string = DOCKERFILE

            with open("{}/Dockerfile".format(ogre_dir), "w") as f:
                f.write(dockerfile_string.format(project_name))
            f.close()
            with open("{}/Dockerfile".format(ogre_dir), "r+") as f:
                content = f.read()
                f.seek(0, 0)
                f.write("FROM {}".format(baseimage) + content)
                # Find last line
                f.seek(0, 2)
                #while f.read(1) != b'\n':
                #    f.seek(-2, 1)
                f.write("{}".format(REQUIREMENTS_LINE))
            f.close()

    return os.path.isfile("{}/Dockerfile".format(ogre_dir))


def config_baseimage():

    platform_machine = "{}".format(platform.machine())
    baseimage = (os.getenv("OGRE_BASEIMAGE")).format(platform_machine)

    return baseimage
    
