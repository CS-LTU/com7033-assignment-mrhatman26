FROM python:3
ADD . /HealthStack
WORKDIR /HealthStack
COPY requirements.txt /HealthStack
RUN pip install -r requirements.txt