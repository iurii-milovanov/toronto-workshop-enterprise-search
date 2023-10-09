ARG IMAGE=python:3.11
FROM --platform=amd64 mcr.microsoft.com/devcontainers/${IMAGE}

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  nodejs \
  npm

RUN curl -fsSL https://aka.ms/install-azd.sh | bash

RUN mkdir /code
WORKDIR /code

RUN mkdir /code/backend
ADD ./backend/requirements.txt /code/backend/
WORKDIR /code/backend
RUN python3 -m venv backend_env
RUN ./backend_env/bin/python -m pip install -r requirements.txt  --pre --no-cache-dir

ADD ./frontend /code/
WORKDIR /code/frontend
RUN npm install
RUN npm run build

ADD . /code/
WORKDIR /code

EXPOSE 8000

ENTRYPOINT [ "/bin/bash" ]
CMD ["start.sh"]