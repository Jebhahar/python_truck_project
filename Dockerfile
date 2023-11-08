FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install python3 -y
WORKDIR /roja
COPY . /roja/
CMD [ "python3", "app.py"]

