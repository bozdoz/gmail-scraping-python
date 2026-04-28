FROM python:3.14-alpine

WORKDIR /app

COPY requirements.* .

RUN apk add --no-cache git

RUN pip install pip-tools==7.5.3

COPY . .

CMD ["python", "main.py"]
