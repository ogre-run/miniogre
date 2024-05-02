DOCKERFILE = """
ENV TZ=America/Chicago
WORKDIR /opt/{}
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
COPY . .
RUN cp ./ogre_dir/bashrc /etc/bash.bashrc
RUN chmod a+rwx /etc/bash.bashrc
RUN pip install uv pip-licenses cyclonedx-bom
"""

DOCKERFILE_DRY = """
ENV TZ=America/Chicago
WORKDIR /opt/{}
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
COPY . .
RUN cp ./ogre_dir/bashrc /etc/bash.bashrc
RUN chmod a+rwx /etc/bash.bashrc
RUN pip install uv pip-licenses cyclonedx-bom
"""

BASHRC = """
_python_argcomplete() {
    local IFS=$'\013'
    local SUPPRESS_SPACE=0
    if compopt +o nospace 2> /dev/null; then
        SUPPRESS_SPACE=1
    fi
    COMPREPLY=( $(IFS="$IFS" \
                  COMP_LINE="$COMP_LINE" \
                  COMP_POINT="$COMP_POINT" \
                  COMP_TYPE="$COMP_TYPE" \
                  _ARGCOMPLETE_COMP_WORDBREAKS="$COMP_WORDBREAKS" \
                  _ARGCOMPLETE=1 \
                  _ARGCOMPLETE_SUPPRESS_SPACE=$SUPPRESS_SPACE \
                  "$1" 8>&1 9>&2 1>/dev/null 2>/dev/null) )
    if [[ $? != 0 ]]; then
        unset COMPREPLY
    elif [[ $SUPPRESS_SPACE == 1 ]] && [[ "$COMPREPLY" =~ [=/:]$ ]]; then
        compopt -o nospace
    fi
}
complete -o nospace -o default -o bashdefault -F _python_argcomplete "az"

[ -z "$PS1" ] && return

export PS1="\[\e[31m\]ogre\[\e[m\] \[\e[33m\]\w\[\e[m\] > "
export TERM=xterm-256color
alias grep="grep --color=auto"
alias ls="ls --color=auto"

echo -e "\e[1;36m"
cat<<'OGRE'
  ___   __ _ _ __ ___
 / _ \ / _` | '__/ _ \ 
| (_) | (_| | | |  __/
 \___/ \__, |_|  \___|
       |___/
OGRE
echo -e "\e[0;33m"

echo "
Made by ogre.run, Inc.

Reach out to us: contact@ogre.run
"

# Turn off colors
# echo -e "\e[m"

# Aliases
alias python="python3"
"""

FILE_EXTENSIONS = {
    "python": [".py"],
    "javascript": [".js"],
    "c++": [".cpp", ".cxx", ".cc", ".c", ".hpp", ".hxx", ".hh", ".h"],
    "java": [".java"],
    "c#": [".cs"],
    "ruby": [".rb"],
    "php": [".php"],
    "go": [".go"],
    "rust": [".rs"],
    "swift": [".swift"],
    "kotlin": [".kt"],
    "scala": [".scala"],
    "clojure": [".clj"],
    "haskell": [".hs"],
    "erlang": [".erl"],
    "elixir": [".ex", ".exs"],
    "lua": [".lua"],
    "perl": [".pl"],
    "r": [".r"],
    "julia": [".jl"],
    "dart": [".dart"],
    "typescript": [".ts"],
    "coffeescript": [".coffee"],
    "ocaml": [".ml", ".mli"],
    "f#": [".fs", ".fsi", ".fsx"],
    "scheme": [".scm", ".ss"],
    "common lisp": [".lisp", ".lsp"],
    "racket": [".rkt"],
    "nim": [".nim"],
    "crystal": [".cr"],
    "groovy": [".groovy"],
    "d": [".d"],
    "fortran": [".f", ".f90", ".f95"],
    "cobol": [".cbl", ".cob", ".cpy"],
    "jupyter": [".ipynb"],
}

ALL_EXTENSIONS = [
    ".py",
    ".js",
    ".cpp",
    ".cxx",
    ".cc",
    ".c",
    ".hpp",
    ".hxx",
    ".hh",
    ".h",
    ".java",
    ".cs",
    ".rb",
    ".php",
    ".go",
    ".rs",
    ".swift",
    ".kt",
    ".scala",
    ".clj",
    ".hs",
    ".erl",
    ".ex",
    ".exs",
    ".lua",
    ".pl",
    ".r",
    ".jl",
    ".dart",
    ".ts",
    ".coffee",
    ".ml",
    ".mli",
    ".fs",
    ".fsi",
    ".fsx",
    ".scm",
    ".ss",
    ".lisp",
    ".lsp",
    ".rkt",
    ".nim",
    ".cr",
    ".groovy",
    ".d",
    ".f",
    ".f90",
    ".f95",
    ".cbl",
    ".cob",
    ".cpy",
    ".ipynb",
]

OGRE_DIR = "ogre_dir"
OGRE_BASEIMAGE = "ogrerun/base:ubuntu22.04-{}"

OPENAI_MODEL = "gpt-4-turbo"
OPENAI_SECRET_PROMPT = """You are a Python requirements generator.
You should generate the contents of a Python requirements file (raw text only) taking into account the text sent by the user.
The raw text sent by the user consists of a combination of the README file contents and the source code contents.
You generate only the file contents as answer.
If the text sent by the user is invalid or is empty, just generate an empty content.
You should ignore the Python version 2 or 3.
The python package should not be included in the requirements file.
Note that some packages do not exist in the PyPi repository, they are only local, and thus shouldnt be added to the requirements.txt file.
Ignore the following Python packages: git, jittor, cuda, shihong, nvdiffrast: they do not exist on the PyPi repository.
Your output should be a raw ASCII text file."""

# OLLAMA_MODEL = "mistral:7b"
OLLAMA_MODEL = "phi3"
OLLAMA_API_SERVER = "http://localhost:11434/v1"
# OLLAMA_SECRET_PROMPT = '''You are a Python requirements generator.
# You should generate the contents of a Python requirements file (raw text only) taking into account the text sent by the user.
# The raw text sent by the user consists of a combination of the README file contents and the source code contents.
# You generate only the file contents as answer.
# If the text sent by the user is invalid or is empty, just generate an empty content.
# You should ignore the Python version 2 or 3.
# The python package should not be included in the requirements file.
# Note that some packages do not exist in the PyPi repository, they are only local, and thus shouldnt be added to the requirements.txt file.
# Ignore the following Python packages: git, jittor, cuda, shihong, nvdiffrast: they do not exist on the PyPi repository.
# Your output should be a raw ASCII text file.'''

OCTOAI_MODEL = "mistral-7b-instruct-fp16"
OCTOAI_SECRET_PROMPT = """You are a Python requirements generator.
You should generate the contents of a Python requirements file (raw text only) taking into account the text sent by the user.
The raw text sent by the user consists of a combination of the README file contents and the source code contents.
If the text sent by the user is invalid or is empty, just generate an empty content.
You should ignore the Python version 2 or 3.
The python package should not be included in the requirements file.
Some packages do not exist in the PyPi repository, they are only local, and thus shouldnt be added to the requirements.txt file.
Ignore the following Python packages: git, jittor, cuda, shihong, nvdiffrast: they do not exist on the PyPi repository.
Your output should be a raw ASCII text file.
Do not return parts of the text sent by the user. We just want the requirements list.
Only return the list of requirements. No other text like the filename at the top of the response or symbols are allowed."""

REWRITE_README_PROMPT = """You are a specialist in understanding and explaining source code. 
You are also a specialist in writing clear documentation (e.g README files) that helps people to understand the source code.
Your task is to take a text input containing the current README and the code and use it to write an updated version of the README file.
The README file should highlight the actual requirements that need to be installed."""

#GROQ_MODEL = "mixtral-8x7b-32768"
GROQ_MODEL = "llama3-70b-8192"
GROQ_SECRET_PROMPT = """You are a Python requirements generator.
You should generate the contents of a Python requirements file (raw text only) taking into account the text sent by the user.
The raw text sent by the user consists of a combination of the README file contents and the source code contents.
If the text sent by the user is invalid or is empty, just generate an empty content.
You should ignore the Python version 2 or 3.
The python package should not be included in the requirements file.
Some packages do not exist in the PyPi repository, they are only local, and thus shouldnt be added to the requirements.txt file.
Ignore the following Python packages: git, jittor, cuda, shihong, nvdiffrast: they do not exist on the PyPi repository.
Your output should be a raw ASCII text file containg only the list of requirements. Do not return sentences. 
Do not return parts of the text sent by the user. We just want the requirements list."""

MISTRAL_MODEL = "mistral-large-latest"
# MISTRAL_SECRET_PROMPT = '''You are a Python requirements generator.
# You should generate the contents of a Python requirements file (raw text only) taking into account the text sent by the user.
# The raw text sent by the user consists of a combination of the README file contents and the source code contents.
# You generate only the file contents as answer.
# If the text sent by the user is invalid or is empty, just generate an empty content.
# You should ignore the Python version 2 or 3.
# The python package should not be included in the requirements file.
# Note that some packages do not exist in the PyPi repository, they are only local, and thus shouldnt be added to the requirements.txt file.
# Ignore the following Python packages: git, jittor, cuda, shihong, nvdiffrast: they do not exist on the PyPi repository.
# Your output should be a raw ASCII text file.'''

CLEAN_REQUIREMENTS_SECRET_PROMPT = """Here is the content of a requirements.txt file. 
It is a list of Python libraries to be installed in the a Python environment. 
Not all entries in the list are actual Python libraries available on the PyPi repository. 
Identify those that arent available on PyPi and remove them from the list.
Get the remaining entries (those that are available on PypI) and generate an updated list of requirements.
If any of the packages in the updated list is represented by a name under which it can not be found on PyPi, change the name to the one that is available on PyPi.
For example, the library `PIL` is not available under that name in PyPi, but `Pillow` is.
Do not explain how the new list is generated. Do not provide any context related to how you proceeded.
Your response must contain only the list of packages to be installed.
Remove any blank lines."""

GROQ_CLEAN_REQUIREMENTS_SECRET_PROMPT = """Here is the content of a requirements.txt file. 
It is a list of Python libraries to be installed in the a Python environment. 
Not all entries in the list are actual Python libraries available on the PyPi repository. 
Identify those that arent available on PyPi and remove them from the list.
Get the remaining entries (those that are available on PypI) and generate an updated list of requirements.
If any of the packages in the updated list is represented by a name under which it can not be found on PyPi, change the name to the one that is available on PyPi.
For example, the library `PIL` is not available under that name in PyPi, but `Pillow` is.
No explanation notes on your reasoning are allowed. Nobody wants to know which packages were removed. Your response must contain only the list of packages to be installed.
Remove any blank lines."""
