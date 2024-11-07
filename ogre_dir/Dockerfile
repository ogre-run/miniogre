FROM ogrerun/base:ubuntu22.04-x86_64
ENV TZ=America/Chicago
WORKDIR /opt/miniogre
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
COPY . .
RUN cp ./ogre_dir/bashrc /etc/bash.bashrc
RUN chmod a+rwx /etc/bash.bashrc
RUN pip install uv pip-licenses cyclonedx-bom
RUN cat ./ogre_dir/requirements.txt | xargs -L 1 uv pip install --system; exit 0