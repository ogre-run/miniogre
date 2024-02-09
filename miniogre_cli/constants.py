DOCKERFILE = """
ENV TZ=Europe/Paris
WORKDIR /opt/{}
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
COPY ogre_dir/bashrc /etc/bash.bashrc·
RUN chmod a+rwx /etc/bash.bashrc
COPY . .
RUN pip install jupyterlab
"""

DOCKERFILE_DRY = """
WORKDIR /opt/{}
# RUN apt update && apt install -y python3-dev python3-pip
COPY ogre_dir/bashrc /etc/bash.bashrc 
RUN chmod a+rwx /etc/bash.bashrc
COPY . .
RUN pip install jupyterlab
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
   / _ \ / _` | '__/ _ \·
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