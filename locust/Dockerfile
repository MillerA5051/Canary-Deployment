# FILE: locust/Dockerfile
# PURPOSE: Packages Locust into a container so it can run inside the cluster
#          as a Kubernetes Deployment and generate traffic continuously.

# base image
FROM python:3.11-slim
# sets the working directory inside the container. all commands run form here. this is where lcust finds locustfile.py automatically
WORKDIR /app
# copies reqirements.txt into /app then install sit
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# copies locustfile into /app
COPY locustfile.py .
# default web ui port. not used in the headless mode.
EXPOSE 8089 
# default command when the container starts (no args)
CMD ["locust"]