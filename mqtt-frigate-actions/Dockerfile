FROM python:3.9

WORKDIR /app
COPY main.py .
RUN pip install paho-mqtt

CMD [ "python", "./main.py" ]
