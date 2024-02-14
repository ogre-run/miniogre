DOCKERFILE = """
ENV TZ=America/Chicago
WORKDIR /opt/{}
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
COPY . .
RUN cp ./ogre_dir/bashrc /etc/bash.bashrc
RUN chmod a+rwx /etc/bash.bashrc
"""

DOCKERFILE_DRY = """
ENV TZ=America/Chicago
WORKDIR /opt/{}
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
COPY . .
RUN cp ./ogre_dir/bashrc /etc/bash.bashrc
RUN chmod a+rwx /etc/bash.bashrc
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
Made by ogre.run

Reach out to us: contact@ogre.run
"

if [[ $EUID -eq 0 ]]; then
  cat <<WARN
WARNING: You are running this container as root, which can cause new files in
mounted volumes to be created as the root user on your host machine.

To avoid this, run the container by specifying your user's userid:

$ docker run -u \$(id -u):\$(id -g) args...
WARN
else
  cat <<EXPL
You are running this container as user with ID $(id -u) and group $(id -g),
which should map to the ID and group for your user on the Docker host. Great!
EXPL
fi

# Turn off colors
# echo -e "\e[m"

# Aliases
alias python="python3"
"""

FILE_EXTENSIONS = {
    'python': ['.py'],
    'javascript': ['.js'],
    'c++': ['.cpp', '.cxx', '.cc', '.c', '.hpp', '.hxx', '.hh', '.h'],
    'java': ['.java'],
    'c#': ['.cs'],
    'ruby': ['.rb'],
    'php': ['.php'],
    'go': ['.go'],
    'rust': ['.rs'],
    'swift': ['.swift'],
    'kotlin': ['.kt'],
    'scala': ['.scala'],
    'clojure': ['.clj'],
    'haskell': ['.hs'],
    'erlang': ['.erl'],
    'elixir': ['.ex', '.exs'],
    'lua': ['.lua'],
    'perl': ['.pl'],
    'r': ['.r'],
    'julia': ['.jl'],
    'dart': ['.dart'],
    'typescript': ['.ts'],
    'coffeescript': ['.coffee'],
    'ocaml': ['.ml', '.mli'],
    'f#': ['.fs', '.fsi', '.fsx'],
    'scheme': ['.scm', '.ss'],
    'common lisp': ['.lisp', '.lsp'],
    'racket': ['.rkt'],
    'nim': ['.nim'],
    'crystal': ['.cr'],
    'groovy': ['.groovy'],
    'd': ['.d'],
    'fortran': ['.f', '.f90', '.f95'],
    'cobol': ['.cbl', '.cob', '.cpy'],
    'jupyter': ['.ipynb']
}

ALL_EXTENSIONS = ['.py', '.js', '.cpp', '.cxx', '.cc', '.c', '.hpp', '.hxx', '.hh', '.h', '.java', '.cs', '.rb', '.php', '.go', '.rs', '.swift', '.kt', '.scala', '.clj', '.hs', '.erl', '.ex', '.exs', '.lua', '.pl', '.r', '.jl', '.dart', '.ts', '.coffee', '.ml', '.mli', '.fs', '.fsi', '.fsx', '.scm', '.ss', '.lisp', '.lsp', '.rkt', '.nim', '.cr', '.groovy', '.d', '.f', '.f90', '.f95', '.cbl', '.cob', '.cpy', '.ipynb']



