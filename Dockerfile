FROM ubuntu:18.04
RUN adduser --quiet --disabled-password qtuser
RUN apt-get update
RUN apt-get install -y python3 python3-pip python3-pyqt5
WORKDIR /src
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
COPY ./src .
COPY stem_setup.py .
COPY ./ui ./ui_files
COPY ./res ./res_files
COPY ./scripts/docker.sh .
RUN [ -d ui_compiled ] || mkdir ui_compiled
RUN [ -d res_compiled ] || mkdir res_compiled
RUN /bin/bash -c 'source docker.sh'
RUN apt-get install -y sudo wget
RUN sudo -H -u qtuser python3 stem_setup.py
RUN wget -q https://downloads.wkhtmltopdf.org/0.12/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb
RUN apt-get install -y ./wkhtmltox_0.12.5-1.bionic_amd64.deb
CMD python3 main.py
