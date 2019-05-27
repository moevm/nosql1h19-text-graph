FROM ubuntu:18.04
RUN adduser --quiet --disabled-password qtuser
RUN apt-get update
RUN apt-get install -y python3 python3-pip python3-pyqt5
WORKDIR /src
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
COPY ./src .
COPY stem_setup.py .
RUN apt-get install sudo
RUN sudo -H -u qtuser python3 stem_setup.py
CMD python3 main.py
