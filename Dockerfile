FROM python:3

RUN mkdir /app

COPY graphicator.py /app
COPY container_run.sh /app

RUN python3 -m pip install tqdm
RUN python3 -m pip install argparse
RUN python3 -m pip install termcolor
RUN python3 -m pip install urllib3
RUN python3 -m pip install requests
RUN apt update
RUN apt install zip
RUN chmod +x /app/container_run.sh

ENTRYPOINT ["/app/container_run.sh"]
