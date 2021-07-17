FROM python:3.9

SHELL ["/bin/bash", "-c"]
RUN apt update -y && apt install -y git pulseaudio-utils
RUN git clone https://github.com/Jaunty-Jackals/jaunty-jackals.git
WORKDIR "/jaunty-jackals"
RUN python3.9 -m venv venv
RUN source venv/bin/activate
RUN python -m pip install -r requirements/dev-requirements.txt

CMD [ "python", "bin/demo.py" ]
